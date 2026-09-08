"""Turn retained motion samples into what an interface may honestly draw.

The local simulation runs a built-in arm. That is by design, and it is the
whole reason this module exists: somebody who has just analysed a video is
owed a picture of *their* video's movement, drawn from their own samples,
sitting next to the built-in trajectory rather than being confused with it.

What the samples support is one timeline per joint. What they do not support
is a silhouette. A set of angles carries no link lengths, no joint positions,
and no statement of which joint attaches to which, so any figure drawn from
them would be geometry this system invented and then presented as evidence.
The rule this module enforces instead is narrower and keepable: draw each
joint's own angle over time, and never join two points across a moment when
the joint was not seen.
"""

from __future__ import annotations

from statistics import median

from app.models.motion_analysis import (
    JointVisibility,
    MotionAnalysisRecord,
    ObservedJointAngle,
    ObservedJointTrack,
    ObservedMotionPreview,
    ObservedTrackPoint,
)


# How many joint timelines a reader can actually take in at once. A quadruped
# gait analysis returns eight; a dense one can return more than fits.
MAX_TRACKS = 12

# A stroke is broken when the wait since the previous sample is much longer
# than this joint's own usual spacing. The multiple is deliberately generous:
# the cost of a false break is a visible seam, and the cost of a missed break
# is a line through time the video never showed.
GAP_MULTIPLE = 2.5

# Below this, a "gap" is sampling jitter rather than a joint going missing.
MIN_GAP_SECONDS = 0.001


def _label(sample: ObservedJointAngle) -> str:
    """Name the joint the way a person would say it out loud."""
    if sample.side == "center":
        return sample.joint_name
    return f"{sample.side} {sample.joint_name}"


def _typical_interval(times: list[float]) -> float:
    """Report this joint's own usual spacing between samples."""
    if len(times) < 2:
        return 0.0
    steps = [
        later - earlier
        for earlier, later in zip(times, times[1:])
        if later - earlier > MIN_GAP_SECONDS
    ]
    return median(steps) if steps else 0.0


def _build_track(label: str, samples: list[ObservedJointAngle]) -> ObservedJointTrack:
    """Assemble one joint's timeline, marking where it must be broken."""
    ordered = sorted(samples, key=lambda sample: sample.timestamp_seconds)
    times = [sample.timestamp_seconds for sample in ordered]
    interval = _typical_interval(times)
    limit = interval * GAP_MULTIPLE if interval > 0 else 0.0

    points: list[ObservedTrackPoint] = []
    previous: ObservedJointAngle | None = None
    for sample in ordered:
        if previous is None:
            starts = True
        elif previous.visibility is JointVisibility.OCCLUDED:
            # The joint was not visible when it was last read, so whatever it
            # did between then and now is unknown, however short the wait was.
            starts = True
        elif limit > 0 and sample.timestamp_seconds - previous.timestamp_seconds > limit:
            starts = True
        else:
            starts = False
        points.append(
            ObservedTrackPoint(
                timestamp_seconds=sample.timestamp_seconds,
                angle_degrees=sample.angle_degrees,
                confidence=sample.confidence,
                visibility=sample.visibility,
                starts_segment=starts,
            )
        )
        previous = sample

    angles = [sample.angle_degrees for sample in ordered]
    clear = sum(
        1 for sample in ordered if sample.visibility is JointVisibility.CLEAR
    )
    return ObservedJointTrack(
        joint_name=ordered[0].joint_name,
        side=ordered[0].side,
        label=label,
        point_count=len(ordered),
        minimum_degrees=min(angles),
        maximum_degrees=max(angles),
        range_degrees=max(angles) - min(angles),
        mean_confidence=sum(s.confidence for s in ordered) / len(ordered),
        clear_ratio=clear / len(ordered),
        segment_count=sum(1 for point in points if point.starts_segment),
        points=points,
    )


def build_observed_motion_preview(
    record: MotionAnalysisRecord,
) -> ObservedMotionPreview:
    """Return the observed movement in the shape an interface can draw.

    Joints are ordered by how much of the movement they carry, so the ones
    that moved most are the ones that survive the cap. The cap is reported
    rather than applied silently.
    """
    grouped: dict[str, list[ObservedJointAngle]] = {}
    for sample in record.samples:
        grouped.setdefault(_label(sample), []).append(sample)

    tracks = [_build_track(label, samples) for label, samples in grouped.items()]
    tracks.sort(key=lambda track: (-track.range_degrees, track.label))
    kept = tracks[:MAX_TRACKS]
    kept.sort(key=lambda track: track.label)

    times = [sample.timestamp_seconds for sample in record.samples]
    start = min(times) if times else 0.0
    end = max(times) if times else 0.0

    return ObservedMotionPreview(
        analysis_id=record.analysis_id,
        extraction_id=record.extraction_id,
        subject_kind=record.subject_kind,
        kinematic_chain=record.kinematic_chain,
        evidence_verdict=record.audit.verdict,
        span_start_seconds=start,
        span_end_seconds=end,
        duration_seconds=max(0.0, end - start),
        mean_confidence=record.mean_confidence,
        tracks=kept,
        omitted_joint_count=max(0, len(tracks) - len(kept)),
    )

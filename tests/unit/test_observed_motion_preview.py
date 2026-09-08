"""Tests for what an interface is allowed to draw from observed samples.

The interesting rules are all about restraint: a wait breaks a stroke, a joint
that was occluded is not joined to what came after it, and no amount of
shaping turns estimated angles into a body.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.motion_analysis import (
    JointVisibility,
    MotionAnalysisRecord,
    MotionEvidenceAudit,
    MotionEvidenceVerdict,
    MotionRetargetVerdict,
    MotionSubjectKind,
    ObservedJointAngle,
)
from app.services.observed_motion_preview import (
    MAX_TRACKS,
    build_observed_motion_preview,
)


def sample(
    time: float,
    joint: str,
    angle: float,
    side: str = "left",
    confidence: float = 0.8,
    visibility: JointVisibility = JointVisibility.CLEAR,
) -> ObservedJointAngle:
    return ObservedJointAngle(
        timestamp_seconds=time,
        joint_name=joint,
        side=side,
        angle_degrees=angle,
        confidence=confidence,
        visibility=visibility,
    )


def record(samples: list[ObservedJointAngle]) -> MotionAnalysisRecord:
    """Wrap samples in the retained record shape, with derived counts honest."""
    times = [item.timestamp_seconds for item in samples]
    span = (max(times) - min(times)) if times else 0.0
    joints = {(item.side, item.joint_name) for item in samples}
    return MotionAnalysisRecord(
        analysis_id="mot_test",
        project_id="prj_test",
        extraction_id="vex_test",
        source_url="https://youtube.com/shorts/P-7Mfa5a8Uk",
        requested_fps=4.0,
        window_start_seconds=0.0,
        window_end_seconds=max(1.0, span),
        subject_kind=MotionSubjectKind.OTHER,
        kinematic_chain="quadrupedal_locomotion",
        joint_names=sorted({item.joint_name for item in samples}),
        samples=samples,
        sample_count=len(samples),
        distinct_joint_count=len(joints),
        observed_span_seconds=span,
        samples_per_second=(len(samples) / span) if span else 0.0,
        mean_confidence=(
            sum(item.confidence for item in samples) / len(samples)
            if samples
            else 0.0
        ),
        clear_sample_count=sum(
            1 for item in samples if item.visibility is JointVisibility.CLEAR
        ),
        audit=MotionEvidenceAudit(
            verdict=MotionEvidenceVerdict.USABLE,
            findings=[],
            mirrored_frame_ratio=0.0,
            distinct_confidence_values=len({item.confidence for item in samples}),
            distinct_visibility_values=len({item.visibility for item in samples}),
            acyclic_joints=[],
            checked_joint_count=len(joints),
        ),
        retarget=MotionRetargetVerdict(
            retarget_supported=False,
            observed_chain="quadrupedal_locomotion",
            reason="No joint map exists for this destination.",
        ),
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=3.0,
        created_at=datetime.now(timezone.utc),
    )


def gait(
    joint: str,
    side: str,
    count: int = 12,
    amplitude: float = 30.0,
) -> list[ObservedJointAngle]:
    """A joint that swings, sampled evenly, so a track has something to draw."""
    return [
        sample(index * 0.25, joint, amplitude * ((index % 4) - 1.5), side=side)
        for index in range(count)
    ]


# --- what the preview is, and is not ---------------------------------------


def test_the_preview_never_claims_to_be_a_body_or_a_measurement() -> None:
    preview = build_observed_motion_preview(record(gait("knee", "left")))

    assert preview.physically_measured is False
    assert preview.reconstructed_body_geometry is False
    assert preview.interpolated_across_gaps is False
    assert preview.preview_kind == "observed_joint_angle_tracks"


def test_the_preview_carries_its_own_lineage() -> None:
    preview = build_observed_motion_preview(record(gait("knee", "left")))

    assert preview.analysis_id == "mot_test"
    assert preview.extraction_id == "vex_test"
    assert preview.kinematic_chain == "quadrupedal_locomotion"
    assert preview.evidence_verdict is MotionEvidenceVerdict.USABLE


def test_an_analysis_with_no_samples_draws_nothing_rather_than_something() -> None:
    preview = build_observed_motion_preview(record([]))

    assert preview.tracks == []
    assert preview.duration_seconds == 0.0
    assert preview.omitted_joint_count == 0


# --- grouping ---------------------------------------------------------------


def test_each_side_of_a_joint_is_its_own_timeline() -> None:
    preview = build_observed_motion_preview(
        record(gait("knee", "left") + gait("knee", "right"))
    )

    assert [track.label for track in preview.tracks] == ["left knee", "right knee"]
    assert all(track.point_count == 12 for track in preview.tracks)


def test_a_center_joint_is_not_labelled_with_a_side() -> None:
    samples = [
        sample(index * 0.25, "pelvis", float(index), side="center")
        for index in range(4)
    ]

    preview = build_observed_motion_preview(record(samples))

    assert preview.tracks[0].label == "pelvis"
    assert preview.tracks[0].side == "center"


def test_points_are_ordered_by_time_even_when_samples_are_not() -> None:
    samples = [
        sample(1.0, "knee", 10.0),
        sample(0.25, "knee", 5.0),
        sample(0.5, "knee", 7.0),
    ]

    preview = build_observed_motion_preview(record(samples))

    times = [point.timestamp_seconds for point in preview.tracks[0].points]
    assert times == sorted(times)


# --- the gap rule -----------------------------------------------------------


def test_an_evenly_sampled_joint_is_one_unbroken_stroke() -> None:
    preview = build_observed_motion_preview(record(gait("knee", "left")))

    track = preview.tracks[0]
    assert track.segment_count == 1
    assert track.points[0].starts_segment is True
    assert all(point.starts_segment is False for point in track.points[1:])


def test_a_long_wait_between_samples_breaks_the_stroke() -> None:
    samples = [
        sample(0.0, "knee", 0.0),
        sample(0.25, "knee", 10.0),
        sample(0.5, "knee", 20.0),
        sample(4.0, "knee", 30.0),  # the joint disappeared for 3.5 s
        sample(4.25, "knee", 32.0),
    ]

    track = build_observed_motion_preview(record(samples)).tracks[0]

    assert track.segment_count == 2
    assert [point.starts_segment for point in track.points] == [
        True,
        False,
        False,
        True,
        False,
    ]


def test_an_occluded_reading_breaks_the_stroke_however_short_the_wait() -> None:
    """Occlusion means what followed was not seen, not that it was smooth."""
    samples = [
        sample(0.0, "knee", 0.0),
        sample(0.25, "knee", 10.0, visibility=JointVisibility.OCCLUDED),
        sample(0.5, "knee", 40.0),
        sample(0.75, "knee", 45.0),
    ]

    track = build_observed_motion_preview(record(samples)).tracks[0]

    assert [point.starts_segment for point in track.points] == [
        True,
        False,
        True,
        False,
    ]
    assert track.segment_count == 2


def test_a_partial_reading_does_not_break_the_stroke() -> None:
    """Partially visible is still visible; only occlusion is a hole."""
    samples = [
        sample(0.0, "knee", 0.0),
        sample(0.25, "knee", 10.0, visibility=JointVisibility.PARTIAL),
        sample(0.5, "knee", 20.0),
    ]

    track = build_observed_motion_preview(record(samples)).tracks[0]

    assert track.segment_count == 1


def test_a_single_reading_is_a_point_not_a_trajectory() -> None:
    track = build_observed_motion_preview(
        record([sample(2.0, "knee", 15.0)])
    ).tracks[0]

    assert track.point_count == 1
    assert track.segment_count == 1
    assert track.range_degrees == 0.0


def test_irregular_but_continuous_sampling_is_not_treated_as_a_gap() -> None:
    """Jitter around the usual spacing is sampling noise, not a missing joint."""
    samples = [
        sample(time, "knee", time * 10)
        for time in (0.0, 0.24, 0.51, 0.74, 1.02, 1.25)
    ]

    assert build_observed_motion_preview(record(samples)).tracks[0].segment_count == 1


# --- summary numbers a reader can recompute ---------------------------------


def test_a_track_reports_its_own_range_confidence_and_clarity() -> None:
    samples = [
        sample(0.0, "knee", -10.0, confidence=0.6),
        sample(0.25, "knee", 30.0, confidence=1.0, visibility=JointVisibility.PARTIAL),
    ]

    track = build_observed_motion_preview(record(samples)).tracks[0]

    assert track.minimum_degrees == -10.0
    assert track.maximum_degrees == 30.0
    assert track.range_degrees == 40.0
    assert track.mean_confidence == 0.8
    assert track.clear_ratio == 0.5


def test_the_span_comes_from_the_samples_themselves() -> None:
    samples = [sample(2.0, "knee", 0.0), sample(6.5, "knee", 20.0)]

    preview = build_observed_motion_preview(record(samples))

    assert preview.span_start_seconds == 2.0
    assert preview.span_end_seconds == 6.5
    assert preview.duration_seconds == 4.5


# --- the cap ----------------------------------------------------------------


def test_the_joints_that_moved_most_survive_the_cap_and_the_rest_are_counted() -> None:
    samples: list[ObservedJointAngle] = []
    for index in range(MAX_TRACKS + 3):
        # Later joints move more, so the first three should be the ones dropped.
        samples += gait(
            f"joint{index:02d}", "left", count=4, amplitude=float(index + 1)
        )

    preview = build_observed_motion_preview(record(samples))

    assert len(preview.tracks) == MAX_TRACKS
    assert preview.omitted_joint_count == 3
    kept = {track.joint_name for track in preview.tracks}
    assert kept.isdisjoint({"joint00", "joint01", "joint02"})
    assert "joint14" in kept


def test_kept_tracks_are_returned_in_a_stable_readable_order() -> None:
    preview = build_observed_motion_preview(
        record(gait("hip", "right") + gait("knee", "left") + gait("ankle", "center"))
    )

    labels = [track.label for track in preview.tracks]
    assert labels == sorted(labels)

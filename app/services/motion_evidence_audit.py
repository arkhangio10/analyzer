"""Deterministic plausibility audit of returned motion samples.

A dense response is not the same as a measurement. A vision model asked for
hundreds of joint angles can answer with a smooth, confident-looking pattern
that never came from the video, and the shape of that answer gives it away:
both legs move identically, every confidence is the same number, and each
angle traces one arc instead of cycling.

None of those are possible in real bipedal gait, so they can be checked with
arithmetic rather than judgement. Each check runs on the numbers alone, states
what it counted, and any two of them together are enough to stop the analysis
being treated as evidence. This is the check that keeps a paid call from
turning fabricated data into a robot trajectory.

Findings carry their counts as data as well as prose, so an interface can state
them in the reader's language while the server stays language-neutral.
"""

from __future__ import annotations

from collections import defaultdict

from app.models.motion_analysis import (
    MotionAuditCode,
    MotionAuditFinding,
    MotionEvidenceAudit,
    MotionEvidenceVerdict,
    ObservedJointAngle,
)


MIRROR_RATIO_THRESHOLD = 0.8
MIN_PAIRED_FRAMES = 6
MIN_SERIES_POINTS = 8
MIN_UNIFORM_SAMPLES = 10
MIN_SWING_SPAN_DEGREES = 30.0


def _series_by_joint(
    samples: list[ObservedJointAngle],
) -> dict[str, list[tuple[float, float]]]:
    series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for sample in samples:
        key = f"{sample.side}.{sample.joint_name}"
        series[key].append((sample.timestamp_seconds, sample.angle_degrees))
    for values in series.values():
        values.sort(key=lambda item: item[0])
    return dict(series)


def _mirrored_frame_ratio(samples: list[ObservedJointAngle]) -> tuple[float, int, int]:
    """Report how often left and right carried exactly the same angle."""
    frames: dict[tuple[float, str], dict[str, float]] = defaultdict(dict)
    for sample in samples:
        if sample.side in {"left", "right"}:
            frames[(sample.timestamp_seconds, sample.joint_name)][sample.side] = (
                sample.angle_degrees
            )
    paired = [
        values
        for values in frames.values()
        if "left" in values and "right" in values
    ]
    if not paired:
        return 0.0, 0, 0
    identical = sum(1 for values in paired if values["left"] == values["right"])
    return round(identical / len(paired), 3), identical, len(paired)


def _direction_reversals(angles: list[float]) -> int:
    """Count how many times a series changes direction."""
    reversals = 0
    previous = 0
    for earlier, later in zip(angles, angles[1:]):
        delta = later - earlier
        if delta == 0:
            continue
        direction = 1 if delta > 0 else -1
        if previous and direction != previous:
            reversals += 1
        previous = direction
    return reversals


def _acyclic_joints(
    series: dict[str, list[tuple[float, float]]],
) -> tuple[list[str], int]:
    """Find joints that swing wide without repeating, which gait never does.

    A joint that travels tens of degrees but reverses at most once has traced
    a single ramp or a single arc. Walking repeats roughly once a second, so
    over any usable window a real hip or knee reverses many times. One arc
    across the whole window is the signature of a drawn curve, not a measured
    one.
    """
    flagged: list[str] = []
    checked = 0
    for key, values in series.items():
        if len(values) < MIN_SERIES_POINTS:
            continue
        checked += 1
        angles = [angle for _, angle in values]
        if max(angles) - min(angles) < MIN_SWING_SPAN_DEGREES:
            continue
        if _direction_reversals(angles) <= 1:
            flagged.append(key)
    return sorted(flagged), checked


def audit_motion_samples(
    samples: list[ObservedJointAngle],
    *,
    window_seconds: float,
) -> MotionEvidenceAudit:
    """Judge whether returned samples can be treated as observations at all."""
    if not samples:
        return MotionEvidenceAudit(
            verdict=MotionEvidenceVerdict.NOT_EVIDENCE,
            findings=[
                MotionAuditFinding(
                    code=MotionAuditCode.NO_SAMPLES,
                    message="The analysis returned no usable joint samples.",
                )
            ],
            mirrored_frame_ratio=0.0,
            distinct_confidence_values=0,
            distinct_visibility_values=0,
            acyclic_joints=[],
            checked_joint_count=0,
        )

    findings: list[MotionAuditFinding] = []
    total = len(samples)
    ratio, identical, paired = _mirrored_frame_ratio(samples)
    if paired >= MIN_PAIRED_FRAMES and ratio >= MIRROR_RATIO_THRESHOLD:
        findings.append(
            MotionAuditFinding(
                code=MotionAuditCode.MIRRORED_SIDES,
                message=(
                    f"Left and right carry exactly the same angle in {identical} "
                    f"of {paired} paired readings. Two limbs of a walking body "
                    "do not move identically, so these sides are not "
                    "independent observations."
                ),
                values={"identical": str(identical), "paired": str(paired)},
            )
        )

    confidences = {sample.confidence for sample in samples}
    if total >= MIN_UNIFORM_SAMPLES and len(confidences) == 1:
        confidence = next(iter(confidences))
        findings.append(
            MotionAuditFinding(
                code=MotionAuditCode.UNIFORM_CONFIDENCE,
                message=(
                    f"All {total} samples report the identical confidence "
                    f"{confidence:g}, so confidence distinguishes nothing and "
                    "was not estimated per sample."
                ),
                values={"samples": str(total), "confidence": f"{confidence:g}"},
            )
        )

    visibilities = {sample.visibility for sample in samples}
    if total >= MIN_UNIFORM_SAMPLES and len(visibilities) == 1:
        visibility = next(iter(visibilities)).value
        findings.append(
            MotionAuditFinding(
                code=MotionAuditCode.UNIFORM_VISIBILITY,
                message=(
                    f"All {total} samples report the identical visibility "
                    f"'{visibility}', so occlusion was not judged frame by frame."
                ),
                values={"samples": str(total), "visibility": visibility},
            )
        )

    series = _series_by_joint(samples)
    acyclic, checked = _acyclic_joints(series)
    joints = ", ".join(acyclic)
    if acyclic and checked and len(acyclic) == checked:
        findings.append(
            MotionAuditFinding(
                code=MotionAuditCode.ACYCLIC_ALL,
                message=(
                    f"Every measured joint ({joints}) traces a single rise and "
                    f"fall across the whole {window_seconds:g}s window. Walking "
                    "repeats about once a second, so one arc is a drawn curve "
                    "rather than a measured gait cycle."
                ),
                values={"joints": joints, "window": f"{window_seconds:g}"},
            )
        )
    elif acyclic:
        findings.append(
            MotionAuditFinding(
                code=MotionAuditCode.ACYCLIC_SOME,
                message=(
                    f"{len(acyclic)} of {checked} joints ({joints}) swing widely "
                    "but reverse at most once across the window."
                ),
                values={
                    "flagged": str(len(acyclic)),
                    "checked": str(checked),
                    "joints": joints,
                },
            )
        )

    if len(findings) >= 2:
        verdict = MotionEvidenceVerdict.NOT_EVIDENCE
    elif findings:
        verdict = MotionEvidenceVerdict.SUSPECT
    else:
        verdict = MotionEvidenceVerdict.USABLE

    return MotionEvidenceAudit(
        verdict=verdict,
        findings=findings,
        mirrored_frame_ratio=ratio,
        distinct_confidence_values=len(confidences),
        distinct_visibility_values=len(visibilities),
        acyclic_joints=acyclic,
        checked_joint_count=checked,
    )

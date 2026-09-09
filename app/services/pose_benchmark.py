"""Compare measured landmarks with ones a person placed, and fail closed.

This is the half of P3.2 that decides whether a pose source is any good, as
opposed to merely not fabricating. The audits ask "could this have come from a
body?"; this asks "is it where the body actually was?", and only a person
marking frames of the real video can answer that.

Everything here refuses rather than guesses:

- No labelled case for this video's bytes: `unvalidated`. Not a pass.
- A labelled frame with no measured frame near it in time: counted as
  unmatched, never matched to the nearest frame at any distance.
- A landmark a person labelled that the measurement never produced: counted as
  missing and held against the measurement, because failing to find a joint is
  a failure to measure it.

Cases are read from a protected directory and never written by anything in the
learning loop, exactly like the frozen evaluation set.
"""

from __future__ import annotations

import logging
from math import sqrt
from pathlib import Path

from pydantic import ValidationError

from app.models.pose_benchmark import (
    LabelledPoseFrame,
    LandmarkComparison,
    PoseBenchmarkCase,
    PoseBenchmarkResult,
)
from app.models.pose_measurement import PoseMeasurementRecord


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POSE_BENCHMARK_DIR = PROJECT_ROOT / "data" / "pose-benchmarks"


def load_pose_benchmark_cases(
    directory: Path | str | None = None,
) -> list[PoseBenchmarkCase]:
    """Read every valid labelled case, skipping ones that do not qualify.

    A file that will not parse, or that claims a provenance other than a
    person, is skipped with a warning. It is never repaired into a usable case.
    """
    path = Path(directory) if directory else DEFAULT_POSE_BENCHMARK_DIR
    if not path.is_dir():
        return []
    cases: list[PoseBenchmarkCase] = []
    for file in sorted(path.glob("*.json")):
        try:
            cases.append(
                PoseBenchmarkCase.model_validate_json(file.read_text(encoding="utf-8"))
            )
        except (ValidationError, ValueError, OSError) as error:
            logger.warning("Skipping pose benchmark case %s: %s", file.name, error)
    return cases


def case_for_source(
    source_sha256: str,
    cases: list[PoseBenchmarkCase],
) -> PoseBenchmarkCase | None:
    """Find the labelled case drawn on exactly these bytes, if there is one."""
    for case in cases:
        if case.source_sha256 == source_sha256:
            return case
    return None


def _nearest_frame(
    record: PoseMeasurementRecord,
    labelled: LabelledPoseFrame,
    tolerance: float,
):
    """Return the measured frame closest in time, if one is close enough."""
    best = None
    best_distance = tolerance
    for frame in record.frames:
        distance = abs(frame.timestamp_seconds - labelled.timestamp_seconds)
        if distance <= best_distance:
            best, best_distance = frame, distance
    return best


def compare_with_labels(
    record: PoseMeasurementRecord,
    case: PoseBenchmarkCase | None,
) -> PoseBenchmarkResult:
    """Report how far a measurement sat from a person's labels."""
    if case is None:
        return PoseBenchmarkResult(
            verdict="unvalidated",
            reason=(
                "No human-labelled case exists for this video's bytes, so the "
                "measurement has not been checked against anything. This is "
                "not a pass."
            ),
            counts_as_external_validation=False,
        )
    if case.source_sha256 != record.source_sha256:  # pragma: no cover - guarded above
        return PoseBenchmarkResult(
            case_id=case.case_id,
            verdict="unvalidated",
            reason="The labelled case was drawn on a different file.",
            counts_as_external_validation=False,
        )

    comparisons: list[LandmarkComparison] = []
    missing: list[str] = []
    unmatched = 0

    for labelled in case.frames:
        frame = _nearest_frame(record, labelled, case.timestamp_tolerance_seconds)
        if frame is None:
            unmatched += 1
            continue
        measured = {reading.name: reading for reading in frame.landmarks}
        for mark in labelled.landmarks:
            reading = measured.get(mark.name)
            if reading is None:
                missing.append(mark.name)
                continue
            error = sqrt((reading.x - mark.x) ** 2 + (reading.y - mark.y) ** 2)
            comparisons.append(
                LandmarkComparison(
                    name=mark.name,
                    timestamp_seconds=labelled.timestamp_seconds,
                    error_normalised=error,
                    within_tolerance=error <= case.tolerance_normalised,
                )
            )

    if not comparisons:
        # Nothing was compared, and the two reasons for that are different
        # failures: no frame landed near a labelled moment, or frames landed
        # there and no labelled joint was found in them.
        nothing_in_time = unmatched == len(case.frames)
        return PoseBenchmarkResult(
            case_id=case.case_id,
            verdict="failed",
            reason=(
                f"{unmatched} labelled frame(s) had no measurement near them "
                "in time, so nothing could be compared."
                if nothing_in_time
                else (
                    "The measurement produced nothing to compare with this "
                    "case's labels, so it did not find the body a person "
                    "could see."
                )
            ),
            labelled_frame_count=len(case.frames),
            compared_frame_count=0,
            unmatched_labelled_frames=unmatched,
            missing_landmarks=sorted(set(missing))[:40],
            counts_as_external_validation=True,
        )

    errors = [item.error_normalised for item in comparisons]
    within = sum(1 for item in comparisons if item.within_tolerance)
    # A labelled landmark the measurement never produced is a miss, not an
    # absence: scoring only what was found would reward a model for looking
    # away from the hard frames.
    scored = len(comparisons) + len(missing)
    ratio = within / scored if scored else 0.0
    worst = max(comparisons, key=lambda item: item.error_normalised)
    passed = (
        ratio >= case.minimum_landmark_pass_ratio
        and unmatched == 0
    )

    return PoseBenchmarkResult(
        case_id=case.case_id,
        verdict="passed" if passed else "failed",
        reason=(
            f"{within} of {scored} labelled landmarks landed within "
            f"{case.tolerance_normalised:.3f} of where a person put them"
            + (f"; {unmatched} labelled frame(s) had no measurement near them" if unmatched else "")
            + "."
        ),
        labelled_frame_count=len(case.frames),
        compared_frame_count=len(case.frames) - unmatched,
        compared_landmark_count=scored,
        within_tolerance_count=within,
        landmark_pass_ratio=ratio,
        mean_error_normalised=sum(errors) / len(errors),
        worst_error_normalised=worst.error_normalised,
        worst_landmark=worst.name,
        unmatched_labelled_frames=unmatched,
        missing_landmarks=sorted(set(missing))[:40],
        comparisons=comparisons[:4000],
        counts_as_external_validation=True,
    )


def benchmark_measurement(
    record: PoseMeasurementRecord,
    directory: Path | str | None = None,
) -> PoseBenchmarkResult:
    """Load the labelled cases and judge one measurement against them."""
    cases = load_pose_benchmark_cases(directory)
    return compare_with_labels(record, case_for_source(record.source_sha256, cases))

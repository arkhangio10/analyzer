"""Tests for judging a measurement against landmarks a person placed.

Almost every test here is about refusing: no labels is not a pass, labels
drawn on another file do not count, a frame nobody measured is a miss, and a
landmark the measurement never found is held against it rather than skipped.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models.pose_benchmark import PoseBenchmarkCase
from app.models.pose_measurement import (
    PoseFrameReading,
    PoseLandmarkReading,
    PoseMeasurementRequest,
)
from app.services.pose_benchmark import (
    benchmark_measurement,
    case_for_source,
    compare_with_labels,
    load_pose_benchmark_cases,
)
from app.services.pose_measurement import build_pose_measurement


SOURCE = "c" * 64
OTHER_SOURCE = "d" * 64


def measured(frames: list[PoseFrameReading], source: str = SOURCE):
    return build_pose_measurement(
        project_id="prj_test",
        upload_id="upl_test",
        source_sha256=source,
        model_name="pose_landmarker_lite",
        model_sha256="b" * 64,
        request=PoseMeasurementRequest(subject_is_human=True),
        frames=frames,
        video_fps=30.0,
        video_duration_seconds=2.0,
        frames_sampled=len(frames),
        elapsed_seconds=0.5,
    )


def frame(timestamp: float, offset: float = 0.0) -> PoseFrameReading:
    """One measured frame; `offset` shifts every landmark off its true place."""
    places = {
        "left_hip": (0.50, 0.50),
        "left_knee": (0.50, 0.70),
        "left_ankle": (0.50, 0.90),
    }
    return PoseFrameReading(
        frame_index=int(timestamp * 10),
        timestamp_seconds=timestamp,
        landmarks=[
            PoseLandmarkReading(name=name, x=x + offset, y=y, visibility=0.9)
            for name, (x, y) in places.items()
        ],
    )


def case_payload(**overrides: object) -> dict:
    payload: dict = {
        "case_id": "walk-lateral-001",
        "description": "Three frames of a lateral walking shot, labelled by hand.",
        "authored_by": "person",
        "labelled_by": "operator",
        "source_sha256": SOURCE,
        "source_description": "Ten seconds of one person walking, filmed side on.",
        "tolerance_normalised": 0.05,
        "frames": [
            {
                "timestamp_seconds": 0.0,
                "landmarks": [
                    {"name": "left_hip", "x": 0.50, "y": 0.50},
                    {"name": "left_knee", "x": 0.50, "y": 0.70},
                    {"name": "left_ankle", "x": 0.50, "y": 0.90},
                ],
            }
        ],
    }
    payload.update(overrides)
    return payload


def case(**overrides: object) -> PoseBenchmarkCase:
    return PoseBenchmarkCase.model_validate(case_payload(**overrides))


# --- loading ---------------------------------------------------------------


def test_a_missing_directory_yields_no_cases_rather_than_an_error() -> None:
    assert load_pose_benchmark_cases(Path("nowhere-at-all")) == []


def test_a_valid_case_loads_and_an_unreadable_one_is_skipped(tmp_path: Path) -> None:
    (tmp_path / "good.json").write_text(json.dumps(case_payload()), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")

    cases = load_pose_benchmark_cases(tmp_path)

    assert [item.case_id for item in cases] == ["walk-lateral-001"]


def test_a_case_a_model_labelled_cannot_be_loaded_at_all(tmp_path: Path) -> None:
    """Provenance is a type, not a flag somebody has to remember to read."""
    (tmp_path / "generated.json").write_text(
        json.dumps(case_payload(authored_by="generated")), encoding="utf-8"
    )

    assert load_pose_benchmark_cases(tmp_path) == []


def test_a_case_is_found_by_the_bytes_it_was_drawn_on(tmp_path: Path) -> None:
    (tmp_path / "good.json").write_text(json.dumps(case_payload()), encoding="utf-8")
    cases = load_pose_benchmark_cases(tmp_path)

    assert case_for_source(SOURCE, cases) is not None
    assert case_for_source(OTHER_SOURCE, cases) is None


# --- failing closed --------------------------------------------------------


def test_no_labels_is_unvalidated_and_never_a_pass() -> None:
    result = compare_with_labels(measured([frame(0.0)]), None)

    assert result.verdict == "unvalidated"
    assert result.counts_as_external_validation is False
    assert result.passed is False
    assert "not a pass" in result.reason


def test_a_measurement_of_a_different_video_finds_no_case(tmp_path: Path) -> None:
    (tmp_path / "good.json").write_text(json.dumps(case_payload()), encoding="utf-8")

    result = benchmark_measurement(measured([frame(0.0)], source=OTHER_SOURCE), tmp_path)

    assert result.verdict == "unvalidated"
    assert result.counts_as_external_validation is False


def test_a_result_can_never_authorise_execution() -> None:
    result = compare_with_labels(measured([frame(0.0)]), case())

    assert result.approved_for_execution is False


# --- comparing -------------------------------------------------------------


def test_landmarks_placed_where_a_person_put_them_pass() -> None:
    result = compare_with_labels(measured([frame(0.0)]), case())

    assert result.verdict == "passed"
    assert result.passed is True
    assert result.within_tolerance_count == 3
    assert result.compared_landmark_count == 3
    assert result.landmark_pass_ratio == 1.0
    assert result.mean_error_normalised == 0.0


def test_landmarks_placed_far_from_the_labels_fail() -> None:
    result = compare_with_labels(measured([frame(0.0, offset=0.2)]), case())

    assert result.verdict == "failed"
    assert result.passed is False
    assert result.within_tolerance_count == 0
    assert abs(result.worst_error_normalised - 0.2) < 1e-9
    assert result.worst_landmark in {"left_hip", "left_knee", "left_ankle"}


def test_the_tolerance_is_the_case_authors_decision_not_the_codes() -> None:
    drifted = measured([frame(0.0, offset=0.08)])

    assert compare_with_labels(drifted, case()).verdict == "failed"
    assert compare_with_labels(drifted, case(tolerance_normalised=0.1)).verdict == "passed"


def test_a_labelled_frame_with_no_measurement_near_it_is_unmatched() -> None:
    """The nearest frame at any distance is not a match; time has a tolerance."""
    result = compare_with_labels(measured([frame(5.0)]), case())

    assert result.unmatched_labelled_frames == 1
    assert result.verdict == "failed"
    assert "no measurement near them" in result.reason


def test_a_landmark_the_measurement_never_found_counts_against_it() -> None:
    """Scoring only what was found would reward looking away from hard frames."""
    partial = PoseFrameReading(
        frame_index=0,
        timestamp_seconds=0.0,
        landmarks=[PoseLandmarkReading(name="left_hip", x=0.5, y=0.5, visibility=0.9)],
    )

    result = compare_with_labels(measured([partial]), case())

    assert result.missing_landmarks == ["left_ankle", "left_knee"]
    assert result.within_tolerance_count == 1
    assert result.compared_landmark_count == 3
    assert abs(result.landmark_pass_ratio - 1 / 3) < 1e-9
    assert result.verdict == "failed"


def test_finding_nothing_at_all_is_a_failure_not_an_absence() -> None:
    empty = PoseFrameReading(frame_index=0, timestamp_seconds=0.0, landmarks=[])

    result = compare_with_labels(measured([empty]), case())

    assert result.verdict == "failed"
    assert result.counts_as_external_validation is True
    assert "did not find the body" in result.reason


def test_the_pass_ratio_the_case_asks_for_is_the_one_applied() -> None:
    partial = PoseFrameReading(
        frame_index=0,
        timestamp_seconds=0.0,
        landmarks=[
            PoseLandmarkReading(name="left_hip", x=0.5, y=0.5, visibility=0.9),
            PoseLandmarkReading(name="left_knee", x=0.5, y=0.7, visibility=0.9),
            PoseLandmarkReading(name="left_ankle", x=0.9, y=0.9, visibility=0.9),
        ],
    )

    strict = compare_with_labels(measured([partial]), case())
    lenient = compare_with_labels(
        measured([partial]), case(minimum_landmark_pass_ratio=0.6)
    )

    assert strict.verdict == "failed"
    assert lenient.verdict == "passed"

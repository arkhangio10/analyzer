"""The measured-pose path, end to end, on real pixels and a real detector.

A rendered figure is written to an mp4, decoded, run through the pose model,
turned into joint angles and judged by both audits. Nothing is stubbed.

Two results come out of it, and the second matters more than the first.

The first is that measured samples pass the deterministic audit. That audit
rejected the vision-model path twice, and this is the first time anything in
this repository has produced joint angles that survive it: the sides move
independently, confidence varies because the detector reports its own, and
every joint cycles because the figure is walking.

The second is that the angles are still substantially wrong. The figure is
drawn at angles known exactly, and what comes back disagrees with them by
double digits. So the audit is necessary and nowhere near sufficient: it can
tell fabricated data from measured data, and it cannot tell accurate data from
inaccurate data. That is precisely why P3.2 asks for comparison against
landmarks a person placed, and it is why nothing generated inside this
repository can close that gap -- a fixture that is both the question and the
answer validates nothing.
"""

from __future__ import annotations

from pathlib import Path
from statistics import mean

import pytest

from app.models.motion_analysis import MotionEvidenceVerdict
from app.models.pose_measurement import PoseMeasurementRequest
from app.services.mediapipe_pose_source import read_pose_frames
from app.services.pose_benchmark import benchmark_measurement
from app.services.pose_measurement import build_pose_measurement
from tests.support.synthetic_walk import write_walk


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "pose_landmarker_lite.task"

WINDOW_SECONDS = 6.0
SAMPLE_FPS = 10.0

pytestmark = pytest.mark.skipif(
    not MODEL_PATH.is_file(),
    reason="No pose model on this machine; run scripts/fetch_pose_model.py.",
)


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    """Render a walk, measure it, and keep both the record and the truth."""
    pytest.importorskip("cv2")
    path = tmp_path_factory.mktemp("walk") / "walk.mp4"
    truth = write_walk(path, seconds=WINDOW_SECONDS, fps=30.0)
    if not path.is_file() or path.stat().st_size == 0:
        pytest.skip("This OpenCV build cannot write an mp4 to test against.")

    frames, properties, sampled = read_pose_frames(
        path,
        model_path=MODEL_PATH,
        frames_per_second=SAMPLE_FPS,
        window_start_seconds=0.0,
        window_seconds=WINDOW_SECONDS,
    )
    record = build_pose_measurement(
        project_id="prj_synthetic",
        upload_id="upl_synthetic",
        source_sha256="a" * 64,
        model_name=MODEL_PATH.stem,
        model_sha256="b" * 64,
        request=PoseMeasurementRequest(
            subject_is_human=True, window_seconds=WINDOW_SECONDS
        ),
        frames=frames,
        video_fps=properties.fps,
        frame_aspect_ratio=properties.aspect_ratio,
        video_duration_seconds=properties.duration_seconds,
        frames_sampled=sampled,
        elapsed_seconds=1.0,
    )
    return record, {round(moment, 3): pose for moment, pose in truth}, sampled


# --- the chain runs ---------------------------------------------------------


def test_the_detector_finds_the_figure_in_the_frames_that_were_read(measured) -> None:
    record, _, sampled = measured

    assert sampled == int(WINDOW_SECONDS * SAMPLE_FPS)
    assert record.frames_with_pose == sampled
    assert record.detection_ratio == 1.0


def test_measuring_produces_angles_for_both_sides_of_several_joints(measured) -> None:
    record, _, _ = measured

    sides = {(sample.side, sample.joint_name) for sample in record.samples}
    assert len(sides) >= 6
    assert {"left", "right"} <= {side for side, _ in sides}
    assert {"hip", "knee"} <= {joint for _, joint in sides}


def test_the_detectors_own_confidence_is_what_is_recorded(measured) -> None:
    """Not a constant this code chose: the spread is the detector's own."""
    record, _, _ = measured

    confidences = {sample.confidence for sample in record.samples}
    assert len(confidences) > 20
    assert 0.0 < record.mean_confidence < 1.0


# --- the audit that rejected the vision model -------------------------------


def test_measured_samples_survive_the_audit_that_rejected_the_model(measured) -> None:
    """The first joint angles in this repository ever to pass this audit."""
    record, _, _ = measured

    assert record.audit.verdict is MotionEvidenceVerdict.USABLE
    assert record.audit.findings == []
    # Each of these is the opposite of what the vision model returned, where
    # the ratio was 1.0, the confidences numbered 2, and every joint was acyclic.
    assert record.audit.mirrored_frame_ratio < 0.8
    assert record.audit.distinct_confidence_values > 10
    assert record.audit.acyclic_joints == []
    assert record.range_audit.within_human_range is True
    assert record.is_usable is True


# --- and are still wrong ----------------------------------------------------


def drawn_angle(pose, sample) -> float | None:
    return getattr(pose, f"{sample.joint_name}_{sample.side}", None)


def test_passing_the_audit_does_not_make_the_angles_right(measured) -> None:
    """The finding that justifies the whole human-labelled benchmark.

    The figure was drawn at known angles. The measurement passes both audits
    and still disagrees with those angles by double digits, so "this was not
    fabricated" and "this is correct" are different questions and only one of
    them has been answered here.

    If this ever fails because the error got small, that is good news and this
    test should be read again rather than deleted: it would mean the pipeline
    became accurate on a cartoon, which still would not be accuracy on a
    person.
    """
    record, truth, _ = measured

    errors = [
        abs(sample.angle_degrees - drawn)
        for sample in record.samples
        if (pose := truth.get(round(sample.timestamp_seconds, 3))) is not None
        and (drawn := drawn_angle(pose, sample)) is not None
    ]

    assert len(errors) > 100
    assert record.is_usable is True
    assert mean(errors) > 8.0


def test_nothing_here_counts_as_external_validation(measured) -> None:
    """A fixture that is its own answer key validates nothing, and says so."""
    record, _, _ = measured

    result = benchmark_measurement(record)

    assert result.verdict == "unvalidated"
    assert result.counts_as_external_validation is False
    assert result.passed is False

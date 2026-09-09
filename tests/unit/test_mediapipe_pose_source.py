"""Tests for the video-and-model adapter that do not need either.

The parts worth pinning down here are the sampling arithmetic, the naming of
landmarks, and every way this can refuse. Whether MediaPipe finds a person in a
real video is not something a unit test can answer, and pretending otherwise
with a stub that always succeeds would be worse than not testing it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.models.pose_measurement import PoseFrameReading, PoseLandmarkReading
from app.services.mediapipe_pose_source import (
    LANDMARK_NAMES,
    PoseModelUnavailable,
    PoseSourceUnreadable,
    VideoProperties,
    _landmarks_from,
    _sample_points,
    model_digest,
    read_pose_frames,
)
from app.services.pose_landmark_geometry import required_landmarks
from app.services.pose_measurement import samples_from_frame


# --- the landmark vocabulary ----------------------------------------------


def test_the_model_returns_the_thirty_three_landmarks_it_is_documented_to() -> None:
    assert len(LANDMARK_NAMES) == 33
    assert len(set(LANDMARK_NAMES)) == 33


def test_every_landmark_the_geometry_needs_has_a_name_here() -> None:
    """A joint the geometry can measure but the adapter cannot name is dead."""
    assert required_landmarks() <= set(LANDMARK_NAMES)


# --- sampling --------------------------------------------------------------


def properties(fps: float = 30.0, frames: int = 300, width: int = 1920, height: int = 1080):
    return VideoProperties(fps=fps, frame_count=frames, width=width, height=height)


def test_sampling_takes_the_requested_rate_not_every_frame() -> None:
    points = list(
        _sample_points(
            properties(), frames_per_second=10.0, window_start_seconds=0.0, window_seconds=1.0
        )
    )

    assert [index for index, _ in points] == [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
    assert points[1][1] == pytest.approx(0.1)


def test_sampling_starts_where_the_window_starts() -> None:
    points = list(
        _sample_points(
            properties(), frames_per_second=2.0, window_start_seconds=5.0, window_seconds=1.0
        )
    )

    assert points[0][0] == 150
    assert points[0][1] == pytest.approx(5.0)


def test_sampling_stops_at_the_end_of_the_file_not_the_end_of_the_window() -> None:
    points = list(
        _sample_points(
            properties(frames=60), frames_per_second=10.0, window_start_seconds=0.0, window_seconds=30.0
        )
    )

    assert max(index for index, _ in points) < 60


def test_asking_for_more_samples_than_there_are_frames_reads_each_once() -> None:
    """A higher requested rate does not invent frames the file does not have."""
    points = list(
        _sample_points(
            properties(fps=10.0, frames=20),
            frames_per_second=60.0,
            window_start_seconds=0.0,
            window_seconds=2.0,
        )
    )

    assert [index for index, _ in points] == list(range(20))


def test_a_video_that_reports_no_frames_yields_no_sample_points() -> None:
    assert list(
        _sample_points(
            properties(frames=0), frames_per_second=10.0, window_start_seconds=0.0, window_seconds=5.0
        )
    ) == []


# --- video properties ------------------------------------------------------


def test_duration_and_aspect_come_from_what_the_decoder_reported() -> None:
    reported = properties(fps=25.0, frames=250, width=1920, height=1080)

    assert reported.duration_seconds == pytest.approx(10.0)
    assert reported.aspect_ratio == pytest.approx(16 / 9)


def test_a_video_with_no_height_does_not_divide_by_zero() -> None:
    assert properties(width=100, height=0).aspect_ratio == 1.0
    assert properties(fps=0.0).duration_seconds == 0.0


def test_the_aspect_ratio_actually_changes_the_angle_it_corrects() -> None:
    """On 16:9 footage, ignoring it tilts every joint. This is that difference."""
    frame = PoseFrameReading(
        frame_index=0,
        timestamp_seconds=0.0,
        landmarks=[
            PoseLandmarkReading(name="left_shoulder", x=0.50, y=0.20, visibility=0.9),
            PoseLandmarkReading(name="left_hip", x=0.50, y=0.50, visibility=0.9),
            PoseLandmarkReading(name="left_knee", x=0.62, y=0.75, visibility=0.9),
        ],
    )

    square, _ = samples_from_frame(frame, minimum_visibility=0.5, aspect_ratio=1.0)
    wide, _ = samples_from_frame(frame, minimum_visibility=0.5, aspect_ratio=16 / 9)

    square_hip = next(s for s in square if s.joint_name == "hip").angle_degrees
    wide_hip = next(s for s in wide if s.joint_name == "hip").angle_degrees
    assert abs(wide_hip - square_hip) > 5.0


# --- the model digest ------------------------------------------------------


def test_the_model_is_identified_by_its_bytes(tmp_path: Path) -> None:
    model = tmp_path / "model.task"
    model.write_bytes(b"not really a model")

    assert model_digest(model) == hashlib.sha256(b"not really a model").hexdigest()


# --- refusing --------------------------------------------------------------


def test_a_missing_model_file_is_named_rather_than_worked_around(tmp_path: Path) -> None:
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"0" * 16)

    with pytest.raises(PoseModelUnavailable) as error:
        read_pose_frames(
            video,
            model_path=tmp_path / "absent.task",
            frames_per_second=10.0,
            window_start_seconds=0.0,
            window_seconds=1.0,
        )

    assert "fetch_pose_model" in str(error.value)


def test_a_file_that_is_not_a_video_is_refused(tmp_path: Path) -> None:
    model = tmp_path / "model.task"
    model.write_bytes(b"0" * 16)
    not_a_video = tmp_path / "notes.mp4"
    not_a_video.write_bytes(b"this is not a video at all")

    with pytest.raises((PoseSourceUnreadable, PoseModelUnavailable)):
        read_pose_frames(
            not_a_video,
            model_path=model,
            frames_per_second=10.0,
            window_start_seconds=0.0,
            window_seconds=1.0,
        )


# --- converting a detection ------------------------------------------------


def landmark(x: float, y: float, visibility: float | None) -> SimpleNamespace:
    return SimpleNamespace(x=x, y=y, z=0.0, visibility=visibility)


def test_no_person_found_produces_no_reading() -> None:
    assert _landmarks_from(SimpleNamespace(pose_landmarks=[])) == []
    assert _landmarks_from(SimpleNamespace(pose_landmarks=None)) == []


def test_landmarks_are_named_in_the_order_the_model_returns_them() -> None:
    detection = SimpleNamespace(
        pose_landmarks=[[landmark(0.1 * index, 0.2, 0.9) for index in range(33)]]
    )

    readings = _landmarks_from(detection)

    assert [reading.name for reading in readings] == list(LANDMARK_NAMES)


def test_a_model_that_reports_no_visibility_is_refused_not_given_a_constant() -> None:
    """Inventing one confidence for every point is the fabrication signature."""
    detection = SimpleNamespace(pose_landmarks=[[landmark(0.5, 0.5, None)]])

    with pytest.raises(PoseModelUnavailable) as error:
        _landmarks_from(detection)

    assert "audit exists to reject" in str(error.value)


def test_a_visibility_outside_zero_to_one_is_clamped_rather_than_rejected() -> None:
    detection = SimpleNamespace(
        pose_landmarks=[[landmark(0.5, 0.5, 1.4), landmark(0.5, 0.5, -0.2)]]
    )

    readings = _landmarks_from(detection)

    assert [reading.visibility for reading in readings] == [1.0, 0.0]

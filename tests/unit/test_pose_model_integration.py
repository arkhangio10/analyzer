"""Tests that run the real pose model, when this machine has one.

Every other pose test constructs landmarks and checks the arithmetic. These
run MediaPipe and OpenCV for real, so they are the only ones that can catch a
version of either behaving differently from what the adapter assumes.

They skip when the model file is absent, which is the ordinary state of a
machine that has not run `scripts/fetch_pose_model.py`. A skip here is not a
pass, and the fixture says which is which.

What is deliberately missing is a positive case. Proving that the model finds
a real person needs a real video of one, and there is none in this repository
to test against. Until that exists, what these tests establish is that the
model loads, a video decodes, the sampling arithmetic survives contact with a
real decoder, and nothing is invented where there is nothing to find.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.mediapipe_pose_source import (
    PoseSourceUnreadable,
    model_digest,
    read_pose_frames,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "pose_landmarker_lite.task"

# The bytes `scripts/fetch_pose_model.py` pins. A model that is not this one
# measures differently, so the tests below say which one they ran against.
EXPECTED_MODEL_SHA256 = (
    "59929e1d1ee95287735ddd833b19cf4ac46d29bc7afddbbf6753c459690d574a"
)


pytestmark = pytest.mark.skipif(
    not MODEL_PATH.is_file(),
    reason="No pose model on this machine; run scripts/fetch_pose_model.py.",
)


@pytest.fixture(scope="module")
def noise_video(tmp_path_factory) -> Path:
    """Three seconds of random noise: a video with certainly no person in it."""
    cv2 = pytest.importorskip("cv2")
    numpy = pytest.importorskip("numpy")

    path = tmp_path_factory.mktemp("pose") / "noise.mp4"
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), 30.0, (640, 360)
    )
    generator = numpy.random.default_rng(0)
    for _ in range(90):
        writer.write(generator.integers(0, 255, (360, 640, 3), dtype=numpy.uint8))
    writer.release()
    if not path.is_file() or path.stat().st_size == 0:
        pytest.skip("This OpenCV build cannot write an mp4 to test against.")
    return path


def test_the_installed_model_is_the_pinned_one() -> None:
    """A different model measures differently, so the digest is checked."""
    assert model_digest(MODEL_PATH) == EXPECTED_MODEL_SHA256


def test_a_real_video_decodes_and_reports_its_own_shape(noise_video: Path) -> None:
    _, properties, _ = read_pose_frames(
        noise_video,
        model_path=MODEL_PATH,
        frames_per_second=10.0,
        window_start_seconds=0.0,
        window_seconds=3.0,
    )

    assert properties.fps == pytest.approx(30.0)
    assert properties.frame_count == 90
    assert (properties.width, properties.height) == (640, 360)
    assert properties.aspect_ratio == pytest.approx(16 / 9, abs=1e-3)
    assert properties.duration_seconds == pytest.approx(3.0)


def test_the_requested_rate_is_what_is_actually_read(noise_video: Path) -> None:
    """Ten frames a second over three seconds is thirty reads, not ninety."""
    _, _, sampled = read_pose_frames(
        noise_video,
        model_path=MODEL_PATH,
        frames_per_second=10.0,
        window_start_seconds=0.0,
        window_seconds=3.0,
    )

    assert sampled == 30


def test_no_person_is_invented_where_there_is_none(noise_video: Path) -> None:
    """The negative control, and the one that would catch a hallucinating source.

    Random noise contains no body. A source that returns landmarks for it is
    not measuring anything, and everything downstream would be reading a
    fabrication with real-looking confidence values attached.
    """
    frames, _, sampled = read_pose_frames(
        noise_video,
        model_path=MODEL_PATH,
        frames_per_second=10.0,
        window_start_seconds=0.0,
        window_seconds=3.0,
    )

    assert sampled == 30
    assert frames == []


def test_a_file_that_is_not_a_video_is_refused_by_the_real_decoder(
    tmp_path: Path,
) -> None:
    not_a_video = tmp_path / "notes.mp4"
    not_a_video.write_bytes(b"this is not a video at all")

    with pytest.raises(PoseSourceUnreadable):
        read_pose_frames(
            not_a_video,
            model_path=MODEL_PATH,
            frames_per_second=10.0,
            window_start_seconds=0.0,
            window_seconds=1.0,
        )

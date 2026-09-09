"""Read an actual video file and return pose landmarks, or refuse clearly.

This is the only file that touches a pose model or a video decoder, so it is
the only one whose imports can fail on a machine that has neither. They are
imported inside the call rather than at module load, and every way this can be
unavailable raises `PoseModelUnavailable` with a sentence saying which way.

The model file is not fetched here. A runtime download is a network dependency
in the middle of a measurement and a different set of bytes on every container
that starts, so the file is a build input: `scripts/fetch_pose_model.py` gets
it once against a pinned checksum, the Dockerfile copies it in, and this module
reports its absence instead of reaching for the internet.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path

from app.models.pose_measurement import PoseFrameReading, PoseLandmarkReading


# MediaPipe Pose returns 33 landmarks in a fixed order. Naming them here means
# a reordering upstream becomes a wrong name rather than a silently rotated
# body, and it is the vocabulary a person labelling ground truth uses.
LANDMARK_NAMES: tuple[str, ...] = (
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
)


class PoseModelUnavailable(RuntimeError):
    """Raised when the pose model or the video decoder cannot be used."""


class PoseSourceUnreadable(ValueError):
    """Raised when the video file itself cannot be opened or has no frames."""


class VideoProperties:
    """What the decoder reported about the file, before any measuring."""

    def __init__(self, fps: float, frame_count: int, width: int, height: int) -> None:
        self.fps = fps
        self.frame_count = frame_count
        self.width = width
        self.height = height

    @property
    def duration_seconds(self) -> float:
        return (self.frame_count / self.fps) if self.fps else 0.0

    @property
    def aspect_ratio(self) -> float:
        return (self.width / self.height) if self.height else 1.0


def model_digest(model_path: Path) -> str:
    """Return the SHA-256 of the model file, so a record names its measurer."""
    digest = hashlib.sha256()
    with open(model_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_dependencies():
    """Import the decoder and the pose model, or say which one is missing."""
    try:
        import cv2  # noqa: PLC0415
    except ImportError as error:
        raise PoseModelUnavailable(
            "OpenCV is not installed, so no video can be decoded. Install the "
            "'pose' extra to enable local measurement."
        ) from error
    try:
        from mediapipe.tasks import python as mp_python  # noqa: PLC0415
        from mediapipe.tasks.python import vision  # noqa: PLC0415
        import mediapipe as mp  # noqa: PLC0415
    except ImportError as error:
        raise PoseModelUnavailable(
            "MediaPipe is not installed, so no pose can be measured. Install "
            "the 'pose' extra to enable local measurement."
        ) from error
    return cv2, mp, mp_python, vision


def read_pose_frames(
    video_path: Path | str,
    *,
    model_path: Path | str,
    frames_per_second: float,
    window_start_seconds: float,
    window_seconds: float,
) -> tuple[list[PoseFrameReading], VideoProperties, int]:
    """Measure one video and return its frames, its properties, and how many
    frames were sampled.

    Frames the model found no person in are not returned. They still count as
    sampled, so the detection ratio in the record reports how much of the
    window actually contained a visible body rather than hiding the misses.
    """
    cv2, mp, mp_python, vision = _require_dependencies()

    model = Path(model_path)
    if not model.is_file():
        raise PoseModelUnavailable(
            f"The pose model file is not present at {model}. Run "
            "scripts/fetch_pose_model.py to download it against its pinned "
            "checksum, or set POSE_MODEL_PATH to an existing copy."
        )

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise PoseSourceUnreadable("The video file could not be opened.")

    try:
        properties = VideoProperties(
            fps=float(capture.get(cv2.CAP_PROP_FPS) or 0.0),
            frame_count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0),
            width=int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
            height=int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
        )
        if properties.fps <= 0 or properties.frame_count <= 0:
            raise PoseSourceUnreadable(
                "The video reported no frame rate or no frames, so no moment "
                "in it can be given a timestamp."
            )

        options = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model)),
            running_mode=vision.RunningMode.VIDEO,
        )
        frames: list[PoseFrameReading] = []
        sampled = 0
        with vision.PoseLandmarker.create_from_options(options) as landmarker:
            for index, timestamp in _sample_points(
                properties,
                frames_per_second=frames_per_second,
                window_start_seconds=window_start_seconds,
                window_seconds=window_seconds,
            ):
                capture.set(cv2.CAP_PROP_POS_FRAMES, index)
                ok, frame = capture.read()
                if not ok:
                    continue
                sampled += 1
                image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                )
                result = landmarker.detect_for_video(image, int(timestamp * 1000))
                landmarks = _landmarks_from(result)
                if landmarks:
                    frames.append(
                        PoseFrameReading(
                            frame_index=index,
                            timestamp_seconds=round(timestamp, 3),
                            landmarks=landmarks,
                        )
                    )
        return frames, properties, sampled
    finally:
        capture.release()


def _sample_points(
    properties: VideoProperties,
    *,
    frames_per_second: float,
    window_start_seconds: float,
    window_seconds: float,
) -> Iterator[tuple[int, float]]:
    """Yield the frame indices to read, and the moment each one is."""
    step = properties.fps / frames_per_second
    if step < 1:
        # Asking for more samples than the file has frames does not create
        # frames; it just reads each one once.
        step = 1.0
    position = window_start_seconds * properties.fps
    end = min(
        properties.frame_count,
        (window_start_seconds + window_seconds) * properties.fps,
    )
    while position < end:
        index = int(position)
        yield index, index / properties.fps
        position += step


def _landmarks_from(result) -> list[PoseLandmarkReading]:
    """Convert one detection into named readings, or return nothing.

    A landmark set with no per-landmark visibility is refused rather than
    given a constant. Inventing one confidence for every point is precisely
    the shape the deterministic audit exists to catch, and a measurement path
    must not manufacture it.
    """
    poses = getattr(result, "pose_landmarks", None)
    if not poses:
        return []
    readings: list[PoseLandmarkReading] = []
    for index, landmark in enumerate(poses[0]):
        if index >= len(LANDMARK_NAMES):
            break
        visibility = getattr(landmark, "visibility", None)
        if visibility is None:
            raise PoseModelUnavailable(
                "This pose model returned landmarks without per-landmark "
                "visibility. A single confidence invented for every point is "
                "the shape the evidence audit exists to reject, so it is not "
                "substituted here."
            )
        readings.append(
            PoseLandmarkReading(
                name=LANDMARK_NAMES[index],
                x=float(landmark.x),
                y=float(landmark.y),
                visibility=max(0.0, min(1.0, float(visibility))),
            )
        )
    return readings

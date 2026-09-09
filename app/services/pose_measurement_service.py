"""Measure one retained upload, audit it, and check it against human labels.

This is the seam between the pieces: it asks storage for a readable file, asks
the adapter for landmarks, hands them to the arithmetic that owns the joint
angles and the audits, and then asks the benchmark whether any of it matches
what a person actually saw.

It spends nothing. There is no provider call anywhere on this path, so there
is no spend guard, no cost acknowledgement, and no token accounting -- and the
record says so permanently rather than by omission.
"""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter

from app.models.pose_benchmark import PoseBenchmarkResult
from app.models.pose_measurement import PoseMeasurementRecord, PoseMeasurementRequest
from app.models.upload import UploadedVideoRecord
from app.services.mediapipe_pose_source import (
    PoseModelUnavailable,
    model_digest,
    read_pose_frames,
)
from app.services.pose_benchmark import benchmark_measurement
from app.services.pose_measurement import build_pose_measurement
from app.services.record_store import RecordStore


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "pose_landmarker_lite.task"


class PoseMeasurementNotFoundError(LookupError):
    """Raised when no retained measurement exists for an upload."""


class PoseMeasurementService:
    """Turn one uploaded video into audited, benchmarked joint angles."""

    def __init__(
        self,
        model_path: Path | str | None = None,
        benchmark_dir: Path | str | None = None,
        store: RecordStore | None = None,
    ) -> None:
        self._model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        self._benchmark_dir = Path(benchmark_dir) if benchmark_dir else None
        self._store = store
        self._records: dict[str, PoseMeasurementRecord] = (
            store.load_all(PoseMeasurementRecord) if store else {}
        )

    @property
    def is_available(self) -> bool:
        """Report whether this deployment can measure a pose at all."""
        return self._model_path.is_file()

    @property
    def model_path(self) -> Path:
        """Return where this deployment looks for the pose model."""
        return self._model_path

    def measure(
        self,
        *,
        project_id: str,
        upload: UploadedVideoRecord,
        video_path: Path,
        request: PoseMeasurementRequest,
    ) -> PoseMeasurementRecord:
        """Measure one video that storage has already made readable."""
        if not self.is_available:
            raise PoseModelUnavailable(
                f"The pose model file is not present at {self._model_path}. Run "
                "scripts/fetch_pose_model.py to download it against its pinned "
                "checksum, or set POSE_MODEL_PATH to an existing copy."
            )

        started = perf_counter()
        frames, properties, sampled = read_pose_frames(
            video_path,
            model_path=self._model_path,
            frames_per_second=request.frames_per_second,
            window_start_seconds=request.window_start_seconds,
            window_seconds=request.window_seconds,
        )
        record = build_pose_measurement(
            project_id=project_id,
            upload_id=upload.upload_id,
            source_sha256=upload.sha256,
            model_name=self._model_path.stem,
            model_sha256=model_digest(self._model_path),
            request=request,
            frames=frames,
            video_fps=properties.fps,
            frame_aspect_ratio=properties.aspect_ratio,
            video_duration_seconds=properties.duration_seconds,
            frames_sampled=sampled,
            elapsed_seconds=perf_counter() - started,
        )
        self._retain(record)
        return record

    def benchmark(self, record: PoseMeasurementRecord) -> PoseBenchmarkResult:
        """Judge one measurement against whatever a person has labelled."""
        return benchmark_measurement(record, self._benchmark_dir)

    def latest_for_upload(self, upload_id: str) -> PoseMeasurementRecord:
        """Return the newest measurement of one upload."""
        matching = [
            record
            for record in self._records.values()
            if record.upload_id == upload_id
        ]
        if not matching:
            raise PoseMeasurementNotFoundError(
                f"No pose measurement exists for upload {upload_id}."
            )
        return max(matching, key=lambda record: record.created_at)

    def list_for_project(self, project_id: str) -> list[PoseMeasurementRecord]:
        """Return every measurement for one project, newest first."""
        matching = [
            record
            for record in self._records.values()
            if record.project_id == project_id
        ]
        return sorted(matching, key=lambda record: record.created_at, reverse=True)

    def _retain(self, record: PoseMeasurementRecord) -> None:
        self._records[record.measurement_id] = record
        if self._store:
            self._store.save(record.measurement_id, record)

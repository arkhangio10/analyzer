"""Local storage boundary for video a person supplies themselves.

This is deliberately not a cloud boundary. An uploaded file is written under
the configured data directory and stays there: nothing here uploads, forwards,
or hands a file to a provider, and the record it returns says so in its type.

The write is streamed and capped as it goes, so an oversized file is refused
partway through instead of being read into memory first, and a refused upload
leaves nothing behind.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.models.upload import (
    ALLOWED_EXTENSIONS,
    ALLOWED_VIDEO_TYPES,
    UploadedVideoRecord,
)
from app.services.record_store import JsonRecordStore


DEFAULT_MAX_UPLOAD_BYTES = 512 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024

_SAFE_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UNSAFE_NAME = re.compile(r"[^A-Za-z0-9._ -]")

STORAGE_NOTE = (
    "Uploaded video is written to this machine's data directory and is never "
    "sent to a cloud model. Extraction currently accepts only a public "
    "YouTube URL, so an upload can be kept and verified by its hash but "
    "cannot yet be turned into a procedure."
)


class UploadRejectedError(ValueError):
    """Raised when a file cannot be accepted, with a reason worth showing."""


def sanitize_filename(name: str) -> str:
    """Reduce a supplied filename to something safe to record and display."""
    base = os.path.basename((name or "").replace("\\", "/")).strip()
    base = _UNSAFE_NAME.sub("_", base).strip(". ")
    return base[:255] or "video"


class LocalVideoStorage:
    """Keep user-supplied video on this machine and describe what was kept."""

    def __init__(
        self,
        root: Path | str,
        store: JsonRecordStore | None = None,
        max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
    ) -> None:
        self._root = Path(root)
        self._store = store
        self._max_upload_bytes = max_upload_bytes
        self._records: dict[str, UploadedVideoRecord] = (
            store.load_all(UploadedVideoRecord) if store else {}
        )

    @property
    def max_upload_bytes(self) -> int:
        """Report the largest file this machine will accept."""
        return self._max_upload_bytes

    @property
    def is_durable(self) -> bool:
        """Report whether the upload index survives a restart."""
        return bool(self._store and self._store.is_durable)

    def list_for_project(self, project_id: str) -> list[UploadedVideoRecord]:
        """Return every retained upload for one project, oldest first."""
        records = [
            record
            for record in self._records.values()
            if record.project_id == project_id
        ]
        return sorted(records, key=lambda record: record.created_at)

    def total_bytes(self, project_id: str) -> int:
        """Report how much of this machine one project's uploads occupy."""
        return sum(record.size_bytes for record in self.list_for_project(project_id))

    def path_for(self, record: UploadedVideoRecord) -> Path:
        """Return where one retained upload lives on this machine."""
        return self._root / record.project_id / record.stored_filename

    def save(
        self,
        project_id: str,
        filename: str,
        content_type: str | None,
        stream: BinaryIO,
    ) -> UploadedVideoRecord:
        """Write one uploaded video to this machine, or refuse it with a reason."""
        if not _SAFE_PROJECT_ID.fullmatch(project_id):
            raise UploadRejectedError("The project identifier is not storable.")

        original = sanitize_filename(filename)
        extension = self._resolve_extension(original, content_type)
        upload_id = f"upl_{uuid4().hex[:12]}"
        stored_filename = f"{upload_id}{extension}"
        directory = self._root / project_id
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise UploadRejectedError(
                "This machine's data directory is not writable, so the video "
                "was not kept."
            ) from error

        destination = directory / stored_filename
        digest = hashlib.sha256()
        written = 0
        try:
            with destination.open("wb") as handle:
                while True:
                    chunk = stream.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > self._max_upload_bytes:
                        raise UploadRejectedError(
                            "The video is larger than this machine accepts "
                            f"({self._max_upload_bytes // (1024 * 1024)} MB). "
                            "Nothing was kept."
                        )
                    digest.update(chunk)
                    handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
        except UploadRejectedError:
            destination.unlink(missing_ok=True)
            raise
        except OSError as error:
            destination.unlink(missing_ok=True)
            raise UploadRejectedError(
                "The video could not be written to this machine."
            ) from error

        if written == 0:
            destination.unlink(missing_ok=True)
            raise UploadRejectedError("The selected file is empty.")

        record = UploadedVideoRecord(
            upload_id=upload_id,
            project_id=project_id,
            original_filename=original,
            stored_filename=stored_filename,
            content_type=self._resolve_content_type(extension, content_type),
            size_bytes=written,
            sha256=digest.hexdigest(),
            created_at=datetime.now(timezone.utc),
        )
        self._records[upload_id] = record
        if self._store:
            self._store.save(upload_id, record)
        return record

    def delete(self, project_id: str, upload_id: str) -> bool:
        """Remove one upload from this machine and forget it."""
        record = self._records.get(upload_id)
        if record is None or record.project_id != project_id:
            return False
        self.path_for(record).unlink(missing_ok=True)
        del self._records[upload_id]
        if self._store:
            self._store.delete(upload_id)
        return True

    def remove_project(self, project_id: str) -> None:
        """Forget every upload for one project and delete its directory."""
        for record in self.list_for_project(project_id):
            self.delete(project_id, record.upload_id)
        shutil.rmtree(self._root / project_id, ignore_errors=True)

    @staticmethod
    def _resolve_extension(filename: str, content_type: str | None) -> str:
        declared = (content_type or "").split(";")[0].strip().casefold()
        if declared in ALLOWED_VIDEO_TYPES:
            return ALLOWED_VIDEO_TYPES[declared]
        suffix = Path(filename).suffix.casefold()
        if suffix in ALLOWED_EXTENSIONS:
            return suffix
        accepted = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise UploadRejectedError(
            f"Only {accepted} video files are accepted; this file is not one."
        )

    @staticmethod
    def _resolve_content_type(extension: str, content_type: str | None) -> str:
        declared = (content_type or "").split(";")[0].strip().casefold()
        if declared in ALLOWED_VIDEO_TYPES:
            return declared
        for media_type, suffix in ALLOWED_VIDEO_TYPES.items():
            if suffix == extension:
                return media_type
        return "application/octet-stream"

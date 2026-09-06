"""Storage boundary for video a person supplies themselves.

This is not a provider boundary. An uploaded file is written to whichever
destination the deployment configured and stays there: nothing here uploads,
forwards, or hands a file to a cloud model, and the record it returns says so
in its type.

There are two destinations because there are two deployments. A machine with a
disk keeps uploads in a directory. A stateless container has no disk that
survives it, so uploads go to a bucket in the operator's own Google Cloud
project. `VideoStorage` holds everything that must be identical either way --
what is accepted, how the stream is capped, what the record claims -- and each
backend supplies only the bytes' destination. That split is the point: the
guarantees cannot drift apart if only one copy of them exists.

The write is streamed and capped as it goes, so an oversized file is refused
partway through instead of being read into memory first, and a refused upload
leaves nothing behind at either destination.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, ClassVar
from uuid import uuid4

from app.models.upload import (
    ALLOWED_EXTENSIONS,
    ALLOWED_VIDEO_TYPES,
    StorageLocation,
    UploadedVideoRecord,
)
from app.services.record_store import RecordStore


logger = logging.getLogger(__name__)

DEFAULT_MAX_UPLOAD_BYTES = 512 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024

_SAFE_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UNSAFE_NAME = re.compile(r"[^A-Za-z0-9._ -]")

LOCAL_STORAGE_NOTE = (
    "Uploaded video is written to this machine's data directory and is never "
    "sent to a cloud model. Extraction currently accepts only a public "
    "YouTube URL, so an upload can be kept and verified by its hash but "
    "cannot yet be turned into a procedure."
)

BUCKET_STORAGE_NOTE = (
    "Uploaded video is written to your own Cloud Storage bucket, not to this "
    "machine, and is never sent to a cloud model. Extraction currently accepts "
    "only a public YouTube URL, so an upload can be kept and verified by its "
    "hash but cannot yet be turned into a procedure."
)


class UploadRejectedError(ValueError):
    """Raised when a file cannot be accepted, with a reason worth showing."""


def sanitize_filename(name: str) -> str:
    """Reduce a supplied filename to something safe to record and display."""
    base = os.path.basename((name or "").replace("\\", "/")).strip()
    base = _UNSAFE_NAME.sub("_", base).strip(". ")
    return base[:255] or "video"


class VideoStorage:
    """What every destination guarantees about a video a person supplied."""

    location: ClassVar[StorageLocation]
    storage_note: ClassVar[str]

    def __init__(
        self,
        store: RecordStore | None = None,
        max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
    ) -> None:
        self._store = store
        self._max_upload_bytes = max_upload_bytes
        self._records: dict[str, UploadedVideoRecord] = (
            store.load_all(UploadedVideoRecord) if store else {}
        )

    @property
    def max_upload_bytes(self) -> int:
        """Report the largest file this deployment will accept."""
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
        """Report how much one project's uploads occupy."""
        return sum(record.size_bytes for record in self.list_for_project(project_id))

    def save(
        self,
        project_id: str,
        filename: str,
        content_type: str | None,
        stream: BinaryIO,
    ) -> UploadedVideoRecord:
        """Retain one uploaded video, or refuse it with a reason."""
        if not _SAFE_PROJECT_ID.fullmatch(project_id):
            raise UploadRejectedError("The project identifier is not storable.")

        original = sanitize_filename(filename)
        extension = self._resolve_extension(original, content_type)
        upload_id = f"upl_{uuid4().hex[:12]}"
        stored_filename = f"{upload_id}{extension}"

        written, digest = self._write(project_id, stored_filename, stream)
        if written == 0:
            self._remove(project_id, stored_filename)
            raise UploadRejectedError("The selected file is empty.")

        record = UploadedVideoRecord(
            upload_id=upload_id,
            project_id=project_id,
            original_filename=original,
            stored_filename=stored_filename,
            content_type=self._resolve_content_type(extension, content_type),
            size_bytes=written,
            sha256=digest,
            created_at=datetime.now(timezone.utc),
            storage_location=self.location,
        )
        self._records[upload_id] = record
        if self._store:
            self._store.save(upload_id, record)
        return record

    def delete(self, project_id: str, upload_id: str) -> bool:
        """Remove one upload from its destination and forget it."""
        record = self._records.get(upload_id)
        if record is None or record.project_id != project_id:
            return False
        self._remove(project_id, record.stored_filename)
        del self._records[upload_id]
        if self._store:
            self._store.delete(upload_id)
        return True

    def remove_project(self, project_id: str) -> None:
        """Forget every upload for one project and delete what it held."""
        for record in self.list_for_project(project_id):
            self.delete(project_id, record.upload_id)

    # --- what each destination supplies -----------------------------------

    def _write(
        self,
        project_id: str,
        stored_filename: str,
        stream: BinaryIO,
    ) -> tuple[int, str]:
        """Write the stream to this destination; return its size and hash."""
        raise NotImplementedError

    def _remove(self, project_id: str, stored_filename: str) -> None:
        """Delete one stored file if it is there."""
        raise NotImplementedError

    # --- shared streaming --------------------------------------------------

    def _consume(self, handle: Any, stream: BinaryIO) -> tuple[int, str]:
        """Copy the stream out, capping and hashing as it goes."""
        digest = hashlib.sha256()
        written = 0
        while True:
            chunk = stream.read(CHUNK_BYTES)
            if not chunk:
                break
            written += len(chunk)
            if written > self._max_upload_bytes:
                raise UploadRejectedError(
                    "The video is larger than this deployment accepts "
                    f"({self._max_upload_bytes // (1024 * 1024)} MB). "
                    "Nothing was kept."
                )
            digest.update(chunk)
            handle.write(chunk)
        return written, digest.hexdigest()

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


class LocalVideoStorage(VideoStorage):
    """Keep user-supplied video on this machine and describe what was kept."""

    location: ClassVar[StorageLocation] = "this_machine"
    storage_note: ClassVar[str] = LOCAL_STORAGE_NOTE

    def __init__(
        self,
        root: Path | str,
        store: RecordStore | None = None,
        max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
    ) -> None:
        self._root = Path(root)
        super().__init__(store=store, max_upload_bytes=max_upload_bytes)

    def path_for(self, record: UploadedVideoRecord) -> Path:
        """Return where one retained upload lives on this machine."""
        return self._root / record.project_id / record.stored_filename

    def remove_project(self, project_id: str) -> None:
        """Forget every upload for one project and delete its directory."""
        super().remove_project(project_id)
        shutil.rmtree(self._root / project_id, ignore_errors=True)

    def _write(
        self,
        project_id: str,
        stored_filename: str,
        stream: BinaryIO,
    ) -> tuple[int, str]:
        directory = self._root / project_id
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise UploadRejectedError(
                "This machine's data directory is not writable, so the video "
                "was not kept."
            ) from error

        destination = directory / stored_filename
        try:
            with destination.open("wb") as handle:
                written, digest = self._consume(handle, stream)
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
        return written, digest

    def _remove(self, project_id: str, stored_filename: str) -> None:
        (self._root / project_id / stored_filename).unlink(missing_ok=True)


class GcsVideoStorage(VideoStorage):
    """Keep user-supplied video in the operator's own bucket, never in a model."""

    location: ClassVar[StorageLocation] = "your_bucket"
    storage_note: ClassVar[str] = BUCKET_STORAGE_NOTE

    def __init__(
        self,
        bucket_name: str,
        prefix: str = "uploads",
        store: RecordStore | None = None,
        max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
        client: Any | None = None,
    ) -> None:
        self._bucket_name = bucket_name
        self._prefix = prefix.strip("/")
        self._client = client
        super().__init__(store=store, max_upload_bytes=max_upload_bytes)

    def object_for(self, record: UploadedVideoRecord) -> str:
        """Return the object name one retained upload occupies."""
        return self._object_name(record.project_id, record.stored_filename)

    def _object_name(self, project_id: str, stored_filename: str) -> str:
        return f"{self._prefix}/{project_id}/{stored_filename}"

    def _bucket(self) -> Any:
        if self._client is None:
            from google.cloud import storage

            self._client = storage.Client()
        return self._client.bucket(self._bucket_name)

    def _write(
        self,
        project_id: str,
        stored_filename: str,
        stream: BinaryIO,
    ) -> tuple[int, str]:
        name = self._object_name(project_id, stored_filename)
        try:
            blob = self._bucket().blob(name)
        except Exception as error:  # noqa: BLE001 - an unreachable bucket keeps nothing
            raise UploadRejectedError(
                "The storage bucket is not reachable, so the video was not kept."
            ) from error

        try:
            with blob.open("wb") as handle:
                written, digest = self._consume(handle, stream)
        except UploadRejectedError:
            self._delete_object(blob)
            raise
        except Exception as error:  # noqa: BLE001
            self._delete_object(blob)
            raise UploadRejectedError(
                "The video could not be written to the storage bucket."
            ) from error
        return written, digest

    def _remove(self, project_id: str, stored_filename: str) -> None:
        name = self._object_name(project_id, stored_filename)
        try:
            self._delete_object(self._bucket().blob(name))
        except Exception as error:  # noqa: BLE001
            logger.warning("Upload %s could not be deleted: %s", name, error)

    @staticmethod
    def _delete_object(blob: Any) -> None:
        try:
            blob.delete()
        except Exception as error:  # noqa: BLE001 - a missing object is not news
            logger.debug(
                "Nothing to delete for %s: %s", getattr(blob, "name", "?"), error
            )

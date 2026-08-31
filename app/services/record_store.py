"""Durable JSON storage for typed workflow records.

Each record is written to its own file, so an interrupted write can never
corrupt more than the record being saved, and every write is atomic. When the
target directory cannot be created or written, the store degrades to memory
only and reports that it is not durable rather than failing the request that
produced the record. Callers must therefore treat `is_durable` as visible
state, not assume persistence succeeded.

Only paid or human-reviewed workflow evidence belongs here. Secrets, uploaded
media, and credentials must never be written through this store.
"""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError


logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT", bound=BaseModel)

_SAFE_RECORD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class RecordIdError(ValueError):
    """Raised when a record identifier cannot be used as a file name."""


class JsonRecordStore:
    """Persist Pydantic records as one JSON file per identifier."""

    def __init__(self, directory: Path | str) -> None:
        self._directory = Path(directory)
        self._durable = self._prepare()

    @property
    def directory(self) -> Path:
        """Return the directory this store writes to."""
        return self._directory

    @property
    def is_durable(self) -> bool:
        """Report whether records actually survive a restart."""
        return self._durable

    def save(self, record_id: str, record: BaseModel) -> bool:
        """Write one record atomically; return whether it was persisted."""
        path = self._path_for(record_id)
        if not self._durable:
            return False
        payload = record.model_dump_json(indent=2)
        try:
            handle = tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._directory,
                prefix=f".{record_id}.",
                suffix=".tmp",
                delete=False,
            )
            try:
                with handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(handle.name, path)
            except BaseException:
                Path(handle.name).unlink(missing_ok=True)
                raise
        except OSError as error:
            self._durable = False
            logger.warning(
                "Record %s could not be persisted; continuing in memory: %s",
                record_id,
                error,
            )
            return False
        return True

    def load_all(self, model_type: type[ModelT]) -> dict[str, ModelT]:
        """Return every readable record, skipping unusable files."""
        records: dict[str, ModelT] = {}
        if not self._directory.is_dir():
            return records
        for path in sorted(self._directory.glob("*.json")):
            try:
                record = model_type.model_validate_json(
                    path.read_text(encoding="utf-8"),
                )
            except (OSError, ValidationError, json.JSONDecodeError) as error:
                logger.warning("Skipping unreadable record %s: %s", path.name, error)
                continue
            records[path.stem] = record
        return records

    def delete(self, record_id: str) -> None:
        """Remove one stored record if it exists."""
        try:
            self._path_for(record_id).unlink(missing_ok=True)
        except OSError as error:
            logger.warning("Record %s could not be deleted: %s", record_id, error)

    def _prepare(self) -> bool:
        try:
            self._directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            logger.warning(
                "Durable storage is unavailable at %s; records stay in memory "
                "for this process only: %s",
                self._directory,
                error,
            )
            return False
        return os.access(self._directory, os.W_OK)

    def _path_for(self, record_id: str) -> Path:
        if not _SAFE_RECORD_ID.fullmatch(record_id):
            raise RecordIdError(record_id)
        return self._directory / f"{record_id}.json"

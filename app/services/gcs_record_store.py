"""Bucket-backed storage for typed workflow records.

Cloud Run gives a container no disk that survives it, so `JsonRecordStore`'s
directory has nowhere to live there. This implements the same `RecordStore`
contract against a Cloud Storage bucket, which means the services that hold a
store keep their code: only the object handed to them at startup changes.

Two differences from the local store are worth stating rather than discovering:

- **No temporary object is needed.** A local file must be written aside and
  renamed so a crash cannot leave a half-written record. An object upload is
  already atomic — readers see the previous object until the new one is complete
  — so the write here is a single call, and that is not a shortcut.
- **A failed write does not condemn the store.** A local directory that stops
  accepting writes has usually become read-only and will stay that way, so
  `JsonRecordStore` gives up on durability. One failed request to a bucket is
  more often a transient network fault, and the next write may well succeed, so
  a failure here is reported for that record without declaring the bucket lost.

Durability is checked once, lazily, on first use. Startup wires several stores
at import time and must not pay a network round trip per store to do it.

Record identifiers go through the same `validate_record_id` the local store
uses, so a key that is safe on a disk is safe as an object name: no traversal,
no separators, no leading dot.

Only paid or human-reviewed workflow evidence belongs here. Secrets and
credentials must never be written through this store.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from app.services.record_store import ModelT, validate_record_id


logger = logging.getLogger(__name__)

CONTENT_TYPE = "application/json"


class GcsRecordStore:
    """Persist Pydantic records as one JSON object per identifier."""

    def __init__(
        self,
        bucket_name: str | None,
        prefix: str,
        client: Any | None = None,
    ) -> None:
        self._bucket_name = bucket_name
        self._prefix = prefix.strip("/")
        self._client = client
        self._bucket: Any | None = None
        self._checked = False
        self._durable = False

    @property
    def prefix(self) -> str:
        """Return the object-name prefix that namespaces this store."""
        return self._prefix

    @property
    def is_durable(self) -> bool:
        """Report whether records actually survive a restart."""
        return self._resolve_bucket() is not None

    def save(self, record_id: str, record: BaseModel) -> bool:
        """Write one record; return whether it was persisted."""
        name = self._object_for(record_id)
        bucket = self._resolve_bucket()
        if bucket is None:
            return False
        try:
            bucket.blob(name).upload_from_string(
                record.model_dump_json(indent=2),
                content_type=CONTENT_TYPE,
            )
        except Exception as error:  # noqa: BLE001 - any client failure degrades
            logger.warning(
                "Record %s could not be persisted; continuing in memory: %s",
                record_id,
                error,
            )
            return False
        return True

    def load_all(self, model_type: type[ModelT]) -> dict[str, ModelT]:
        """Return every readable record, skipping unusable objects."""
        records: dict[str, ModelT] = {}
        bucket = self._resolve_bucket()
        if bucket is None:
            return records
        try:
            blobs = list(bucket.list_blobs(prefix=f"{self._prefix}/"))
        except Exception as error:  # noqa: BLE001
            logger.warning("Stored records could not be listed: %s", error)
            return records
        for blob in blobs:
            record_id = self._record_id_for(blob.name)
            if record_id is None:
                continue
            try:
                record = model_type.model_validate_json(blob.download_as_bytes())
            except (ValidationError, json.JSONDecodeError) as error:
                logger.warning("Skipping unreadable record %s: %s", blob.name, error)
                continue
            except Exception as error:  # noqa: BLE001
                logger.warning("Record %s could not be read: %s", blob.name, error)
                continue
            records[record_id] = record
        return dict(sorted(records.items()))

    def delete(self, record_id: str) -> None:
        """Remove one stored record if it exists."""
        bucket = self._resolve_bucket()
        if bucket is None:
            return
        try:
            bucket.blob(self._object_for(record_id)).delete()
        except Exception as error:  # noqa: BLE001 - a missing object is not news
            logger.debug("Record %s was not deleted: %s", record_id, error)

    # --- connection -------------------------------------------------------

    def _resolve_bucket(self) -> Any | None:
        if self._checked:
            return self._bucket
        self._checked = True
        if not self._bucket_name:
            return None
        client = self._client
        if client is None:
            try:
                from google.cloud import storage
            except ImportError:
                logger.warning(
                    "google-cloud-storage is not installed; records stay in "
                    "memory for this process only."
                )
                return None
            try:
                client = storage.Client()
            except Exception as error:  # noqa: BLE001
                logger.warning(
                    "Cloud Storage credentials are unavailable; records stay "
                    "in memory for this process only: %s",
                    error,
                )
                return None
            self._client = client
        try:
            bucket = client.bucket(self._bucket_name)
            # Probe with an object listing rather than bucket.exists(). This
            # store reads and writes objects and never touches the bucket's own
            # metadata, but exists() calls buckets.get, which roles/storage.
            # objectAdmin does not grant. Checking with the permission the
            # store actually uses keeps the deployment from having to widen the
            # grant to satisfy a check for something it never needs.
            next(iter(bucket.list_blobs(prefix=self._prefix, max_results=1)), None)
        except Exception as error:  # noqa: BLE001
            logger.warning(
                "Bucket %s could not be opened; records stay in memory for "
                "this process only: %s",
                self._bucket_name,
                error,
            )
            return None
        self._bucket = bucket
        self._durable = True
        return bucket

    # --- naming -----------------------------------------------------------

    def _object_for(self, record_id: str) -> str:
        return f"{self._prefix}/{validate_record_id(record_id)}.json"

    def _record_id_for(self, name: str) -> str | None:
        """Return the identifier an object name carries, if it is one of ours."""
        if not name.startswith(f"{self._prefix}/") or not name.endswith(".json"):
            return None
        record_id = name[len(self._prefix) + 1 : -len(".json")]
        try:
            return validate_record_id(record_id)
        except ValueError:
            logger.warning("Skipping record with an unusable name: %s", name)
            return None

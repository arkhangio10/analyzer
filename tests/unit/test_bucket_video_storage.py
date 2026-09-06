"""Tests for keeping a person's own video in the operator's own bucket.

The bucket destination exists because Cloud Run has no disk, and it must give
away nothing the local one does not. So these tests assert two things: that the
bucket backend does what it claims, and that a record it produces differs from
a local one in exactly one field -- where the bytes went. Anything else drifting
apart would be a guarantee weakening on the way to the cloud, which is the
failure this file is here to catch.

The double implements only the calls the storage makes. It deliberately commits
a partial write when the stream is cut off mid-upload, so the cleanup path is
tested rather than assumed away.
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

import pytest

from app.services.record_store import JsonRecordStore
from app.services.storage_service import (
    GcsVideoStorage,
    LocalVideoStorage,
    UploadRejectedError,
)


class FakeWriter:
    """The handle `blob.open("wb")` hands back."""

    def __init__(self, blob: "FakeBlob") -> None:
        self._blob = blob
        self._chunks: list[bytes] = []

    def write(self, chunk: bytes) -> int:
        self._chunks.append(chunk)
        return len(chunk)

    def __enter__(self) -> "FakeWriter":
        return self

    def __exit__(self, *exc: object) -> None:
        # Commit even when the caller left through an exception: a real
        # resumable upload may already have persisted, so the storage must not
        # rely on an aborted write leaving nothing behind.
        self._blob.bucket.objects[self._blob.name] = b"".join(self._chunks)


class FakeBlob:
    def __init__(self, bucket: "FakeBucket", name: str) -> None:
        self.bucket = bucket
        self.name = name

    def open(self, mode: str = "r") -> FakeWriter:
        assert mode == "wb"
        if self.bucket.write_error is not None:
            raise self.bucket.write_error
        return FakeWriter(self)

    def delete(self) -> None:
        if self.name not in self.bucket.objects:
            raise KeyError(self.name)
        del self.bucket.objects[self.name]


class FakeBucket:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.write_error: Exception | None = None

    def blob(self, name: str) -> FakeBlob:
        return FakeBlob(self, name)

    def list_blobs(self, prefix: str | None = None) -> list[FakeBlob]:
        return [
            FakeBlob(self, name)
            for name in sorted(self.objects)
            if prefix is None or name.startswith(prefix)
        ]

    def exists(self) -> bool:
        return True


class FakeClient:
    def __init__(self, bucket: FakeBucket) -> None:
        self._bucket = bucket

    def bucket(self, name: str) -> FakeBucket:
        return self._bucket


@pytest.fixture
def bucket() -> FakeBucket:
    return FakeBucket()


def bucket_storage(
    bucket: FakeBucket,
    tmp_path: Path,
    max_bytes: int = 1024,
) -> GcsVideoStorage:
    return GcsVideoStorage(
        "aprendiz-media",
        "uploads",
        store=JsonRecordStore(tmp_path / "index"),
        max_upload_bytes=max_bytes,
        client=FakeClient(bucket),
    )


# --- what the bucket destination does -------------------------------------


def test_a_video_goes_to_the_bucket_and_says_so(bucket, tmp_path) -> None:
    store = bucket_storage(bucket, tmp_path)
    payload = b"fake mp4 bytes"

    record = store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(payload))

    assert record.storage_location == "your_bucket"
    assert record.sent_to_provider is False
    assert record.analysis_available is False
    assert record.size_bytes == len(payload)
    assert record.sha256 == hashlib.sha256(payload).hexdigest()
    assert bucket.objects[store.object_for(record)] == payload


def test_the_object_name_carries_the_project_but_not_the_supplied_name(
    bucket, tmp_path
) -> None:
    store = bucket_storage(bucket, tmp_path)

    record = store.save(
        "prj_test01", "my holiday.mp4", "video/mp4", io.BytesIO(b"bytes")
    )

    name = store.object_for(record)
    assert name.startswith("uploads/prj_test01/upl_")
    assert name.endswith(".mp4")
    assert "holiday" not in name
    assert record.original_filename == "my holiday.mp4"


def test_deleting_an_upload_removes_the_object_too(bucket, tmp_path) -> None:
    store = bucket_storage(bucket, tmp_path)
    record = store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))

    assert store.delete("prj_test01", record.upload_id) is True

    assert bucket.objects == {}
    assert store.list_for_project("prj_test01") == []


def test_an_upload_belongs_only_to_its_own_project(bucket, tmp_path) -> None:
    store = bucket_storage(bucket, tmp_path)
    record = store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))

    assert store.delete("prj_other1", record.upload_id) is False
    assert bucket.objects != {}


def test_uploads_survive_a_new_storage_instance(bucket, tmp_path) -> None:
    first = bucket_storage(bucket, tmp_path)
    record = first.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))

    reopened = bucket_storage(bucket, tmp_path)

    assert [r.upload_id for r in reopened.list_for_project("prj_test01")] == [
        record.upload_id
    ]


# --- refusals leave nothing behind ----------------------------------------


def test_an_oversized_file_is_refused_and_leaves_nothing_in_the_bucket(
    bucket, tmp_path
) -> None:
    store = bucket_storage(bucket, tmp_path, max_bytes=64)

    with pytest.raises(UploadRejectedError) as error:
        store.save("prj_test01", "big.mp4", "video/mp4", io.BytesIO(b"x" * 500))

    assert "larger than this deployment accepts" in str(error.value)
    assert bucket.objects == {}
    assert store.list_for_project("prj_test01") == []


def test_an_empty_file_is_refused_and_leaves_nothing_in_the_bucket(
    bucket, tmp_path
) -> None:
    store = bucket_storage(bucket, tmp_path)

    with pytest.raises(UploadRejectedError):
        store.save("prj_test01", "empty.mp4", "video/mp4", io.BytesIO(b""))

    assert bucket.objects == {}


def test_a_file_that_is_not_video_never_reaches_the_bucket(bucket, tmp_path) -> None:
    store = bucket_storage(bucket, tmp_path)

    with pytest.raises(UploadRejectedError):
        store.save("prj_test01", "notes.txt", "text/plain", io.BytesIO(b"bytes"))

    assert bucket.objects == {}


def test_an_unreachable_bucket_refuses_with_a_reason(bucket, tmp_path) -> None:
    store = bucket_storage(bucket, tmp_path)
    bucket.write_error = ConnectionError("no route")

    with pytest.raises(UploadRejectedError) as error:
        store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))

    assert "could not be written to the storage bucket" in str(error.value)
    assert store.list_for_project("prj_test01") == []


# --- the two destinations must not drift apart ----------------------------


def test_both_destinations_describe_the_same_file_identically(
    bucket, tmp_path
) -> None:
    """Only the location may differ; every other claim is the same file's."""
    payload = b"fake mp4 bytes"
    local = LocalVideoStorage(
        tmp_path / "uploads", store=JsonRecordStore(tmp_path / "local-index")
    )
    remote = bucket_storage(bucket, tmp_path / "remote")

    on_disk = local.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(payload))
    in_bucket = remote.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(payload))

    varies = {"upload_id", "stored_filename", "created_at", "storage_location"}
    on_disk_fields = on_disk.model_dump()
    in_bucket_fields = in_bucket.model_dump()
    assert {k: v for k, v in on_disk_fields.items() if k not in varies} == {
        k: v for k, v in in_bucket_fields.items() if k not in varies
    }
    assert on_disk.storage_location == "this_machine"
    assert in_bucket.storage_location == "your_bucket"
    assert on_disk.sha256 == in_bucket.sha256


def test_the_bucket_note_names_the_bucket_and_still_rules_out_the_model() -> None:
    assert "your own Cloud Storage bucket" in GcsVideoStorage.storage_note
    assert "never sent to a cloud model" in GcsVideoStorage.storage_note
    assert "never sent to a cloud model" in LocalVideoStorage.storage_note

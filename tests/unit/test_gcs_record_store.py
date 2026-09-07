"""Tests for bucket-backed record storage and its honest degradation.

These run against a double rather than a bucket. The double implements only the
four calls the store makes, with the signatures the real client has, so a test
passing here means the store uses the client correctly — not that Cloud Storage
behaves as imagined. What a double cannot prove is left to the deploy.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.models.project import ProjectClarificationRequest
from app.services.gcs_record_store import GcsRecordStore
from google.api_core.exceptions import NotFound

from app.services.record_store import RecordIdError, RecordStore


class FakeBlob:
    """One stored object, holding the bytes a real blob would hold."""

    def __init__(self, bucket: "FakeBucket", name: str) -> None:
        self._bucket = bucket
        self.name = name

    def upload_from_string(self, data: Any, content_type: str = "text/plain") -> None:
        if self._bucket.write_error is not None:
            raise self._bucket.write_error
        payload = data.encode("utf-8") if isinstance(data, str) else data
        self._bucket.objects[self.name] = payload
        self._bucket.content_types[self.name] = content_type

    def download_as_bytes(self) -> bytes:
        return self._bucket.objects[self.name]

    def delete(self) -> None:
        if self.name not in self._bucket.objects:
            raise KeyError(self.name)
        del self._bucket.objects[self.name]


class FakeBucket:
    """A bucket that may or may not exist, and may refuse writes."""

    def __init__(self, name: str, *, exists: bool = True) -> None:
        self.name = name
        self.objects: dict[str, bytes] = {}
        self.content_types: dict[str, str] = {}
        self.write_error: Exception | None = None
        self.list_error: Exception | None = None if exists else NotFound("absent")
        self.probe_calls = 0

    def exists(self) -> bool:
        # roles/storage.objectAdmin does not grant storage.buckets.get, so a
        # store that calls this is unusable with the permissions the
        # deployment grants. Failing here is the point.
        raise AssertionError(
            "bucket.exists() needs storage.buckets.get, which the runtime "
            "service account deliberately does not have."
        )

    def blob(self, name: str) -> FakeBlob:
        return FakeBlob(self, name)

    def list_blobs(
        self,
        prefix: str | None = None,
        max_results: int | None = None,
    ) -> list[FakeBlob]:
        if self.list_error is not None:
            raise self.list_error
        # Only the durability probe caps its results; a real listing does not.
        if max_results is not None:
            self.probe_calls += 1
        found = [
            FakeBlob(self, name)
            for name in sorted(self.objects)
            if prefix is None or name.startswith(prefix)
        ]
        return found[:max_results] if max_results else found


class FakeClient:
    """The one client call the store makes."""

    def __init__(self, bucket: FakeBucket) -> None:
        self._bucket = bucket

    def bucket(self, name: str) -> FakeBucket:
        return self._bucket


@pytest.fixture
def bucket() -> FakeBucket:
    return FakeBucket("aprendiz-records")


def store_over(bucket: FakeBucket, prefix: str = "projects") -> GcsRecordStore:
    return GcsRecordStore("aprendiz-records", prefix, client=FakeClient(bucket))


def clarification() -> ProjectClarificationRequest:
    return ProjectClarificationRequest(
        task_description="Teach a robot arm to place a fragile component safely.",
        destination="robot",
        robot_model="APRENDIZ SimArm-6",
        language="en",
    )


# --- the contract ---------------------------------------------------------


def test_it_satisfies_the_record_store_contract() -> None:
    assert isinstance(GcsRecordStore(None, "projects"), RecordStore)


def test_records_survive_a_new_store_over_the_same_bucket(
    bucket: FakeBucket,
) -> None:
    assert store_over(bucket).save("prj_abc123", clarification()) is True

    reopened = store_over(bucket).load_all(ProjectClarificationRequest)

    assert list(reopened) == ["prj_abc123"]
    assert reopened["prj_abc123"].robot_model == "APRENDIZ SimArm-6"


def test_a_record_is_stored_as_json_under_its_prefix(bucket: FakeBucket) -> None:
    store_over(bucket).save("prj_abc123", clarification())

    assert list(bucket.objects) == ["projects/prj_abc123.json"]
    assert bucket.content_types["projects/prj_abc123.json"] == "application/json"


def test_deleting_removes_only_that_record(bucket: FakeBucket) -> None:
    store = store_over(bucket)
    store.save("prj_abc123", clarification())
    store.save("prj_def456", clarification())

    store.delete("prj_abc123")

    assert list(store.load_all(ProjectClarificationRequest)) == ["prj_def456"]


def test_deleting_a_record_that_is_not_there_is_not_an_error(
    bucket: FakeBucket,
) -> None:
    store_over(bucket).delete("prj_absent")


# --- namespacing ----------------------------------------------------------


def test_one_bucket_holds_several_kinds_of_record_without_mixing_them(
    bucket: FakeBucket,
) -> None:
    store_over(bucket, "projects").save("rec_000001", clarification())
    store_over(bucket, "motion-analyses").save("rec_000002", clarification())

    projects = store_over(bucket, "projects").load_all(ProjectClarificationRequest)
    motion = store_over(bucket, "motion-analyses").load_all(
        ProjectClarificationRequest
    )

    assert list(projects) == ["rec_000001"]
    assert list(motion) == ["rec_000002"]


def test_objects_that_are_not_records_are_ignored(bucket: FakeBucket) -> None:
    store = store_over(bucket)
    store.save("prj_abc123", clarification())
    bucket.objects["projects/notes.txt"] = b"not a record"
    bucket.objects["projects/nested/prj_deep.json"] = b"{}"

    assert list(store.load_all(ProjectClarificationRequest)) == ["prj_abc123"]


def test_record_identifier_cannot_escape_the_prefix(bucket: FakeBucket) -> None:
    store = store_over(bucket)

    with pytest.raises(RecordIdError):
        store.save("../../etc/passwd", clarification())

    assert bucket.objects == {}


# --- degradation ----------------------------------------------------------


def test_a_store_without_a_bucket_name_degrades_to_memory() -> None:
    store = GcsRecordStore(None, "projects")

    assert store.is_durable is False
    assert store.save("prj_abc123", clarification()) is False
    assert store.load_all(ProjectClarificationRequest) == {}
    store.delete("prj_abc123")


def test_a_bucket_that_is_not_there_degrades_to_memory() -> None:
    missing = FakeBucket("absent", exists=False)
    store = GcsRecordStore("absent", "projects", client=FakeClient(missing))

    assert store.is_durable is False
    assert store.save("prj_abc123", clarification()) is False
    assert missing.objects == {}


def test_an_unreadable_record_is_skipped_rather_than_failing_startup(
    bucket: FakeBucket,
) -> None:
    store = store_over(bucket)
    store.save("prj_good001", clarification())
    bucket.objects["projects/prj_broken.json"] = b"{ not json"

    assert list(store.load_all(ProjectClarificationRequest)) == ["prj_good001"]


def test_a_failed_write_is_reported_without_condemning_the_bucket(
    bucket: FakeBucket,
) -> None:
    store = store_over(bucket)
    bucket.write_error = ConnectionError("transient")

    assert store.save("prj_abc123", clarification()) is False

    bucket.write_error = None
    assert store.is_durable is True
    assert store.save("prj_abc123", clarification()) is True


def test_durability_is_checked_once_rather_than_per_call(
    bucket: FakeBucket,
) -> None:
    """Startup wires several stores; none may cost a round trip to construct."""
    store = GcsRecordStore("aprendiz-records", "projects", client=FakeClient(bucket))
    assert bucket.probe_calls == 0

    store.save("prj_abc123", clarification())
    store.load_all(ProjectClarificationRequest)
    assert store.is_durable is True

    assert bucket.probe_calls == 1


def test_availability_asks_for_object_access_not_bucket_metadata(
    bucket: FakeBucket,
) -> None:
    """Found on Cloud Run: objectAdmin does not grant storage.buckets.get.

    The first deployment logged 403 on every call and degraded to memory, with
    `durable_storage` false, because availability was checked with
    `bucket.exists()`. This store reads and writes objects and never touches
    the bucket's own configuration, so it must not need a permission for
    something it does not use. `FakeBucket.exists` raises, so a store that
    reaches for it again fails here rather than in production.
    """
    store = store_over(bucket)

    assert store.is_durable is True
    assert bucket.probe_calls == 1

"""Tests for keeping a person's own video on their own machine."""

import hashlib
import io

import pytest
from fastapi.testclient import TestClient

from app.api.runtime import video_storage
from app.main import app
from app.services.record_store import JsonRecordStore
from app.services.storage_service import (
    LocalVideoStorage,
    UploadRejectedError,
    sanitize_filename,
)


client = TestClient(app)


def storage(tmp_path, max_bytes: int = 1024) -> LocalVideoStorage:
    return LocalVideoStorage(
        tmp_path / "uploads",
        store=JsonRecordStore(tmp_path / "index"),
        max_upload_bytes=max_bytes,
    )


def create_project() -> str:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Learn the walking mechanics demonstrated in the video.",
            "destination": "robot",
            "language": "en",
            "robot_model": "APRENDIZ SimArm-6",
            "robot_class": "humanoid",
        },
    )
    assert response.status_code == 201
    return response.json()["project_id"]


def test_a_video_is_written_to_this_machine_and_described_by_its_hash(tmp_path) -> None:
    store = storage(tmp_path)
    payload = b"fake mp4 bytes"

    record = store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(payload))

    assert record.size_bytes == len(payload)
    assert record.sha256 == hashlib.sha256(payload).hexdigest()
    assert store.path_for(record).read_bytes() == payload
    assert record.stored_locally is True
    assert record.sent_to_provider is False
    assert record.analysis_available is False


def test_the_stored_name_never_carries_the_supplied_one(tmp_path) -> None:
    store = storage(tmp_path)

    record = store.save(
        "prj_test01",
        "../../etc/passwd.mp4",
        "video/mp4",
        io.BytesIO(b"bytes"),
    )

    assert record.original_filename == "passwd.mp4"
    assert record.stored_filename.startswith("upl_")
    assert record.stored_filename.endswith(".mp4")
    assert ".." not in record.stored_filename
    assert store.path_for(record).parent.name == "prj_test01"


@pytest.mark.parametrize(
    "name",
    ["../../evil", "C:\\Windows\\system32\\cmd.exe", "a/b/c.mp4", ""],
)
def test_supplied_names_are_reduced_to_something_safe(name: str) -> None:
    safe = sanitize_filename(name)

    assert "/" not in safe
    assert "\\" not in safe
    assert not safe.startswith(".")
    assert safe


def test_a_file_that_is_not_video_is_refused(tmp_path) -> None:
    store = storage(tmp_path)

    with pytest.raises(UploadRejectedError) as error:
        store.save("prj_test01", "notes.txt", "text/plain", io.BytesIO(b"hello"))

    assert "video files are accepted" in str(error.value)
    assert store.list_for_project("prj_test01") == []


def test_an_oversized_file_is_refused_and_leaves_nothing_behind(tmp_path) -> None:
    store = storage(tmp_path, max_bytes=64)

    with pytest.raises(UploadRejectedError) as error:
        store.save("prj_test01", "big.mp4", "video/mp4", io.BytesIO(b"x" * 500))

    assert "larger than this machine accepts" in str(error.value)
    assert store.list_for_project("prj_test01") == []
    written = list((tmp_path / "uploads" / "prj_test01").glob("*"))
    assert written == []


def test_an_empty_file_is_refused(tmp_path) -> None:
    store = storage(tmp_path)

    with pytest.raises(UploadRejectedError) as error:
        store.save("prj_test01", "empty.mp4", "video/mp4", io.BytesIO(b""))

    assert "empty" in str(error.value)
    assert list((tmp_path / "uploads" / "prj_test01").glob("*")) == []


def test_a_trusted_extension_is_accepted_when_the_browser_sends_no_type(tmp_path) -> None:
    store = storage(tmp_path)

    record = store.save("prj_test01", "clip.webm", None, io.BytesIO(b"bytes"))

    assert record.content_type == "video/webm"
    assert record.stored_filename.endswith(".webm")


def test_uploads_survive_a_new_storage_instance(tmp_path) -> None:
    first = storage(tmp_path)
    record = first.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))

    reopened = storage(tmp_path)

    assert [item.upload_id for item in reopened.list_for_project("prj_test01")] == [
        record.upload_id
    ]
    assert reopened.total_bytes("prj_test01") == len(b"bytes")


def test_deleting_an_upload_removes_the_file_too(tmp_path) -> None:
    store = storage(tmp_path)
    record = store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))
    path = store.path_for(record)

    assert store.delete("prj_test01", record.upload_id) is True

    assert not path.exists()
    assert store.list_for_project("prj_test01") == []
    assert store.delete("prj_test01", record.upload_id) is False


def test_an_upload_belongs_only_to_its_own_project(tmp_path) -> None:
    store = storage(tmp_path)
    record = store.save("prj_test01", "walk.mp4", "video/mp4", io.BytesIO(b"bytes"))

    assert store.delete("prj_other", record.upload_id) is False
    assert store.list_for_project("prj_other") == []


def test_the_endpoint_keeps_the_file_and_reports_it_was_not_sent() -> None:
    project_id = create_project()

    created = client.post(
        f"/api/projects/{project_id}/uploads",
        files={"file": ("walk.mp4", b"fake mp4 bytes", "video/mp4")},
    )

    assert created.status_code == 201
    body = created.json()
    assert body["sent_to_provider"] is False
    assert body["stored_locally"] is True
    assert body["analysis_available"] is False
    assert body["size_bytes"] == len(b"fake mp4 bytes")
    assert len(body["sha256"]) == 64

    listing = client.get(f"/api/projects/{project_id}/uploads")
    assert listing.status_code == 200
    assert listing.json()["total_bytes"] == len(b"fake mp4 bytes")
    assert "never sent to a cloud model" in listing.json()["storage_note"]
    assert "video/mp4" in listing.json()["accepted_types"]

    video_storage.remove_project(project_id)


def test_the_endpoint_refuses_a_non_video_and_an_unknown_project() -> None:
    project_id = create_project()

    refused = client.post(
        f"/api/projects/{project_id}/uploads",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    missing = client.post(
        "/api/projects/prj_missing/uploads",
        files={"file": ("walk.mp4", b"bytes", "video/mp4")},
    )

    assert refused.status_code == 422
    assert "video files are accepted" in refused.json()["detail"]
    assert missing.status_code == 404


def test_the_endpoint_deletes_an_upload_and_returns_the_remaining_list() -> None:
    project_id = create_project()
    created = client.post(
        f"/api/projects/{project_id}/uploads",
        files={"file": ("walk.mp4", b"bytes", "video/mp4")},
    )
    upload_id = created.json()["upload_id"]

    removed = client.delete(f"/api/projects/{project_id}/uploads/{upload_id}")
    again = client.delete(f"/api/projects/{project_id}/uploads/{upload_id}")

    assert removed.status_code == 200
    assert removed.json()["uploads"] == []
    assert removed.json()["total_bytes"] == 0
    assert again.status_code == 404

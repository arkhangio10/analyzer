"""Tests for the local pose-measurement endpoints.

These are mostly about refusing well: the right status, a sentence that names
the missing thing, and no pretence that an unmeasured video was measured.

Whether the machine running them has a pose model is not allowed to change
what they assert. An earlier version of this file encoded "there is no model
here" as a fact, and two tests broke the moment one was fetched -- so the ones
that care point the service at a path they control.
"""

from __future__ import annotations

import io
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import pose_measurement_routes
from app.api.runtime import pose_measurement_service
from app.main import app
from app.models.pose_measurement import PoseMeasurementRequest
from app.services.pose_measurement import build_pose_measurement


client = TestClient(app)


def create_project() -> str:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Learn the walking technique demonstrated here.",
            "destination": "robot",
            "language": "en",
            "robot_model": "APRENDIZ SimArm-6",
            "robot_class": "humanoid",
        },
    )
    assert response.status_code == 201
    return response.json()["project_id"]


def upload_video(project_id: str) -> dict:
    response = client.post(
        f"/api/projects/{project_id}/uploads",
        files={"file": ("walk.mp4", io.BytesIO(b"0" * 2048), "video/mp4")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def measurement_body(**overrides: object) -> dict:
    body: dict = {"subject_is_human": True, "window_seconds": 4.0}
    body.update(overrides)
    return body


def measurement_url(project_id: str, upload_id: str) -> str:
    return f"/api/projects/{project_id}/uploads/{upload_id}/pose-measurement"


# --- what has to be present ------------------------------------------------


def test_an_unknown_project_or_upload_is_not_found() -> None:
    project_id = create_project()

    assert client.post(
        measurement_url("prj_missing", "upl_missing"), json=measurement_body()
    ).status_code == 404
    assert client.post(
        measurement_url(project_id, "upl_missing"), json=measurement_body()
    ).status_code == 404


def test_measuring_requires_saying_the_subject_is_a_person() -> None:
    """The landmark model assumes a human body, so a person has to assert one."""
    project_id = create_project()
    upload = upload_video(project_id)

    response = client.post(
        measurement_url(project_id, upload["upload_id"]), json={"window_seconds": 4.0}
    )

    assert response.status_code == 422


def test_claiming_a_non_human_subject_is_rejected_by_the_contract() -> None:
    project_id = create_project()
    upload = upload_video(project_id)

    response = client.post(
        measurement_url(project_id, upload["upload_id"]),
        json=measurement_body(subject_is_human=False),
    )

    assert response.status_code == 422


# --- refusing when the model is not installed ------------------------------


def test_a_deployment_without_the_model_says_so_rather_than_failing_oddly(
    monkeypatch, tmp_path: Path
) -> None:
    """Pointed at a machine with no model, whether or not this one has one."""
    project_id = create_project()
    upload = upload_video(project_id)
    monkeypatch.setattr(
        pose_measurement_service, "_model_path", tmp_path / "absent.task"
    )

    response = client.post(
        measurement_url(project_id, upload["upload_id"]), json=measurement_body()
    )

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "pose model file is not present" in detail
    assert "fetch_pose_model" in detail


def test_availability_follows_the_file_rather_than_being_assumed(
    monkeypatch, tmp_path: Path
) -> None:
    """Whether this deployment can measure is one question: is the file there."""
    assert pose_measurement_service.model_path.name.endswith(".task")

    monkeypatch.setattr(
        pose_measurement_service, "_model_path", tmp_path / "absent.task"
    )
    assert pose_measurement_service.is_available is False

    present = tmp_path / "present.task"
    present.write_bytes(b"not a real model, but a real file")
    monkeypatch.setattr(pose_measurement_service, "_model_path", present)
    assert pose_measurement_service.is_available is True


# --- reading a measurement back --------------------------------------------


def test_an_unmeasured_upload_reports_that_rather_than_an_empty_result() -> None:
    project_id = create_project()
    upload = upload_video(project_id)

    response = client.get(measurement_url(project_id, upload["upload_id"]))

    assert response.status_code == 404
    assert "not been measured" in response.json()["detail"]


def test_a_benchmark_for_an_unmeasured_upload_is_not_a_pass() -> None:
    project_id = create_project()
    upload = upload_video(project_id)

    response = client.get(
        f"{measurement_url(project_id, upload['upload_id'])}/benchmark"
    )

    assert response.status_code == 404


def test_a_retained_measurement_is_read_back_and_benchmarked(monkeypatch) -> None:
    """With a record in hand, the read and benchmark paths are exercised."""
    project_id = create_project()
    upload = upload_video(project_id)
    record = build_pose_measurement(
        project_id=project_id,
        upload_id=upload["upload_id"],
        source_sha256=upload["sha256"],
        model_name="pose_landmarker_lite",
        model_sha256="b" * 64,
        request=PoseMeasurementRequest(subject_is_human=True),
        frames=[],
        video_fps=30.0,
        video_duration_seconds=4.0,
        frames_sampled=0,
        elapsed_seconds=0.1,
    )
    pose_measurement_service._retain(record)

    fetched = client.get(measurement_url(project_id, upload["upload_id"]))
    benchmark = client.get(
        f"{measurement_url(project_id, upload['upload_id'])}/benchmark"
    )

    assert fetched.status_code == 200
    body = fetched.json()
    assert body["cloud_calls_made"] == 0
    assert body["sent_to_provider"] is False
    assert body["physically_measured"] is False
    assert body["measured_in_image_plane"] is True
    # Nothing was measured, so nothing may be called a human reading.
    assert body["range_audit"]["within_human_range"] is False

    assert benchmark.status_code == 200
    assert benchmark.json()["verdict"] == "unvalidated"
    assert benchmark.json()["counts_as_external_validation"] is False


def test_this_path_never_asks_for_a_spend_token() -> None:
    """A local measurement costs nothing, so no route here is spend-guarded."""
    for route in pose_measurement_routes.router.routes:
        assert not getattr(route, "dependencies", [])

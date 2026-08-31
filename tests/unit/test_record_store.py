"""Tests for durable JSON record storage and its honest degradation."""

from pathlib import Path

import pytest

from app.models.project import ProjectClarificationRequest
from app.services.project_service import ProjectService
from app.services.record_store import JsonRecordStore, RecordIdError


class Sample(ProjectClarificationRequest):
    """Reuse an existing typed contract as the stored record shape."""


def clarification() -> ProjectClarificationRequest:
    return ProjectClarificationRequest(
        task_description="Teach a robot arm to place a fragile component safely.",
        destination="robot",
        robot_model="APRENDIZ SimArm-6",
        language="en",
    )


def test_records_survive_a_new_store_over_the_same_directory(tmp_path: Path) -> None:
    store = JsonRecordStore(tmp_path / "records")
    assert store.is_durable is True
    assert store.save("prj_abc123", clarification()) is True

    reopened = JsonRecordStore(tmp_path / "records").load_all(
        ProjectClarificationRequest
    )

    assert list(reopened) == ["prj_abc123"]
    assert reopened["prj_abc123"].robot_model == "APRENDIZ SimArm-6"


def test_writes_leave_no_temporary_files_behind(tmp_path: Path) -> None:
    store = JsonRecordStore(tmp_path)

    store.save("prj_abc123", clarification())
    store.save("prj_abc123", clarification())

    assert [path.name for path in sorted(tmp_path.iterdir())] == ["prj_abc123.json"]


def test_unreadable_record_is_skipped_rather_than_failing_startup(
    tmp_path: Path,
) -> None:
    store = JsonRecordStore(tmp_path)
    store.save("prj_good001", clarification())
    (tmp_path / "prj_broken.json").write_text("{ not json", encoding="utf-8")

    loaded = store.load_all(ProjectClarificationRequest)

    assert list(loaded) == ["prj_good001"]


def test_record_identifier_cannot_escape_the_directory(tmp_path: Path) -> None:
    store = JsonRecordStore(tmp_path)

    for unsafe in ["../escape", "nested/id", "", ".hidden"]:
        with pytest.raises(RecordIdError):
            store.save(unsafe, clarification())


def test_unwritable_directory_degrades_to_memory(tmp_path: Path) -> None:
    blocker = tmp_path / "records"
    blocker.write_text("not a directory", encoding="utf-8")

    store = JsonRecordStore(blocker)

    assert store.is_durable is False
    assert store.save("prj_abc123", clarification()) is False
    assert store.load_all(ProjectClarificationRequest) == {}


def test_project_service_reloads_projects_from_disk(tmp_path: Path) -> None:
    store = JsonRecordStore(tmp_path / "projects")
    service = ProjectService(store=store)
    created = service.create(clarification())
    assert service.is_durable is True

    restarted = ProjectService(store=JsonRecordStore(tmp_path / "projects"))

    assert restarted.get(created.project_id).project_id == created.project_id
    assert [project.project_id for project in restarted.list_projects()] == [
        created.project_id
    ]


def test_project_service_without_a_store_stays_in_memory() -> None:
    service = ProjectService()

    created = service.create(clarification())

    assert service.is_durable is False
    assert service.get(created.project_id).project_id == created.project_id


def video_service(directory: Path):
    """Build the extraction service over stores that may already hold data."""
    from app.services.gemini_service import GeminiService
    from app.services.project_video_procedure_service import (
        ProjectVideoProcedureService,
    )

    return ProjectVideoProcedureService(
        ProjectService(store=JsonRecordStore(directory / "projects")),
        GeminiService(),
        store=JsonRecordStore(directory / "video-procedures"),
    )


def test_extraction_evidence_survives_a_restart(tmp_path: Path) -> None:
    """A disabled provider still produces evidence that must not be lost."""
    import asyncio

    from app.models.project_video_procedure import (
        ProjectVideoProcedureExtractionRequest,
    )

    project = ProjectService(
        store=JsonRecordStore(tmp_path / "projects"),
    ).create(clarification())

    service = video_service(tmp_path)
    record = asyncio.run(
        service.extract(
            project.project_id,
            ProjectVideoProcedureExtractionRequest(
                video_url="https://youtu.be/-fD2TSL2s7I",
                acknowledge_source_approved=True,
                acknowledge_cloud_cost=True,
                output_language="en",
            ),
        )
    )

    assert record.status == "extraction_failed"
    assert record.cloud_calls_made == 0

    restarted = video_service(tmp_path)
    reloaded = restarted.get(project.project_id, record.extraction_id)

    assert reloaded.extraction_id == record.extraction_id
    assert reloaded.failure_code == record.failure_code
    assert restarted.is_durable is True
    assert [
        item.extraction_id
        for item in restarted.list_for_project(project.project_id)
    ] == [record.extraction_id]

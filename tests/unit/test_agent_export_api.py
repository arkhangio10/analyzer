"""Tests for building and downloading an agent package through the API, and
for the exported agent's own routes.

The provider is faked, exactly as the extraction tests fake it, so an approved
procedure exists without a paid call. Everything downstream is real: the
adaptation, the packaging, the zip, and the agent-mode routes that read the
skill back.
"""

from __future__ import annotations

from hashlib import sha256
import io
from pathlib import Path
import zipfile

from fastapi.testclient import TestClient

from app.api import agent_routes
from app.api import routes as root_routes
from app.api.runtime import agent_export_service, evaluator, project_video_procedure_service
from app.core.config import Settings
from app.main import app
from app.models.agent_package import ExportedAgentSkill
from app.models.procedure import Procedure, ProcedureStep
from app.models.video_extraction import GeminiUsage, VideoExtractionResult


client = TestClient(app)


class SuccessfulGeminiService:
    async def extract_procedure(self, request: object) -> VideoExtractionResult:
        return VideoExtractionResult(
            source_url="https://youtube.com/shorts/P-7Mfa5a8Uk",
            procedure=Procedure(
                task="Supinate the forearm",
                objective="Demonstrate supination and pronation.",
                steps=[
                    ProcedureStep(step=1, action="Rotate the palm upward.", source_timestamps=["00:05"]),
                    ProcedureStep(step=2, action="Rotate the palm downward.", source_timestamps=["00:11"]),
                ],
                uncertainties=["Speed is not stated."],
            ),
            provider="vertex_ai",
            requested_model="gemini-2.5-flash-lite",
            model_version=None,
            elapsed_seconds=4.4,
            usage=GeminiUsage(prompt_tokens=100, candidate_tokens=25, total_tokens=125),
        )


def create_project(destination: str) -> dict:
    payload = {
        "task_description": "Learn the observable technique demonstrated in the video.",
        "destination": destination,
        "language": "en",
    }
    if destination == "computer":
        payload["computer_application"] = "Training viewer"
    else:
        payload["robot_model"] = "APRENDIZ SimArm-6"
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 201
    return response.json()


def extraction_payload() -> dict:
    return {
        "video_url": "https://youtube.com/shorts/P-7Mfa5a8Uk",
        "task_hint": "Extract only observable actions.",
        "output_language": "en",
        "acknowledge_cloud_cost": True,
        "acknowledge_source_approved": True,
    }


def extract_and_approve(project: dict) -> dict:
    extracted = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/extract",
        json=extraction_payload(),
    )
    assert extracted.status_code == 201
    review = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{extracted.json()['extraction_id']}/review",
        json={"decision": "approve", "notes": "Steps reviewed."},
    )
    assert review.status_code == 200
    return review.json()


def approved_project(monkeypatch, destination: str) -> dict:
    project = create_project(destination)
    monkeypatch.setattr(project_video_procedure_service, "_gemini_service", SuccessfulGeminiService())
    extract_and_approve(project)
    return project


def packages_url(project: dict) -> str:
    return f"/api/projects/{project['project_id']}/agent-packages"


def read_zip(content: bytes) -> tuple[zipfile.ZipFile, str]:
    archive = zipfile.ZipFile(io.BytesIO(content))
    root = archive.namelist()[0].split("/", 1)[0]
    return archive, root


# --- building --------------------------------------------------------------


def test_a_project_without_an_approved_procedure_has_nothing_to_export() -> None:
    project = create_project("computer")

    response = client.post(packages_url(project), json={"language": "es"})

    assert response.status_code == 409
    assert "no approved procedure" in response.json()["detail"]


def test_an_unknown_project_is_404() -> None:
    assert client.post("/api/projects/prj_missing/agent-packages", json={}).status_code == 404
    assert client.get("/api/projects/prj_missing/agent-packages").status_code == 404


def test_an_approved_computer_project_exports_a_downloadable_package(monkeypatch) -> None:
    project = approved_project(monkeypatch, "computer")

    built = client.post(packages_url(project), json={"language": "es"})
    assert built.status_code == 201
    manifest = built.json()
    assert manifest["destination"] == "computer"
    assert manifest["procedure_version"] == 1
    assert manifest["launcher"] == ["start.sh", "start.ps1"]
    assert manifest["files"]
    # The exporter packaged the same protected cases the evaluator loaded.
    assert manifest["frozen_case_count"] == evaluator.case_count
    assert all(value is False for value in manifest["guarantees"].values())

    listed = client.get(packages_url(project))
    assert [m["package_id"] for m in listed.json()] == [manifest["package_id"]]
    assert client.get(f"{packages_url(project)}/{manifest['package_id']}").json() == manifest

    download = client.get(f"{packages_url(project)}/{manifest['package_id']}/download")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/zip"
    assert download.headers["content-disposition"].endswith('.zip"')

    archive, root = read_zip(download.content)
    assert root == manifest["directory_name"]
    skill_bytes = archive.read(f"{root}/skill/skill.json")
    listed_digest = next(f["sha256"] for f in manifest["files"] if f["path"] == "skill/skill.json")
    assert sha256(skill_bytes).hexdigest() == listed_digest

    skill = ExportedAgentSkill.model_validate_json(skill_bytes)
    assert skill.project_id == project["project_id"]
    assert skill.language == "es"
    assert skill.practices == []
    assert skill.lineage.usage.total_tokens == 125
    assert skill.adaptation is not None
    assert skill.adaptation.approved_for_execution is False
    assert skill.adaptation.destination.value == "computer"
    assert archive.read(f"{root}/README.md").decode("utf-8").startswith("# Agente APRENDIZ")


def test_a_robot_project_exports_without_motion_evidence(monkeypatch) -> None:
    project = approved_project(monkeypatch, "robot")

    manifest = client.post(packages_url(project), json={"language": "en"}).json()
    archive, root = read_zip(
        client.get(f"{packages_url(project)}/{manifest['package_id']}/download").content
    )

    skill = ExportedAgentSkill.model_validate_json(archive.read(f"{root}/skill/skill.json"))
    assert skill.destination.value == "robot"
    assert skill.motion_evidence is None
    assert skill.retarget is None
    assert skill.adaptation is not None and skill.adaptation.destination.value == "robot"
    assert "ARG INSTALL_BROWSER=false" in archive.read(f"{root}/Dockerfile").decode("utf-8")
    assert archive.read(f"{root}/README.md").decode("utf-8").startswith("# APRENDIZ agent")


def test_a_package_is_rebuilt_after_a_restart_and_verified(monkeypatch) -> None:
    """Bytes are not retained; a download after restart rebuilds and checks."""
    project = approved_project(monkeypatch, "computer")
    manifest = client.post(packages_url(project), json={}).json()
    url = f"{packages_url(project)}/{manifest['package_id']}/download"
    first = client.get(url).content

    agent_export_service._built.clear()

    second = client.get(url)
    assert second.status_code == 200
    assert second.content == first


def test_an_older_package_survives_a_newer_approved_version(monkeypatch) -> None:
    """A rebuild uses its own extraction, not whatever is newest."""
    project = approved_project(monkeypatch, "computer")
    manifest = client.post(packages_url(project), json={}).json()
    assert manifest["procedure_version"] == 1
    url = f"{packages_url(project)}/{manifest['package_id']}/download"
    first = client.get(url).content

    second_version = extract_and_approve(project)
    assert second_version["procedure_version"] == 2

    agent_export_service._built.clear()
    rebuilt = client.get(url)
    assert rebuilt.status_code == 200
    assert rebuilt.content == first
    archive, root = read_zip(rebuilt.content)
    skill = ExportedAgentSkill.model_validate_json(archive.read(f"{root}/skill/skill.json"))
    assert skill.procedure_version == 1

    # A new package, by contrast, takes the newest approved version.
    assert client.post(packages_url(project), json={}).json()["procedure_version"] == 2


def test_a_package_belongs_to_its_project_only(monkeypatch) -> None:
    owner = approved_project(monkeypatch, "computer")
    other = create_project("computer")
    manifest = client.post(packages_url(owner), json={}).json()

    assert client.get(f"{packages_url(other)}/{manifest['package_id']}").status_code == 404
    assert client.get(f"{packages_url(other)}/{manifest['package_id']}/download").status_code == 404


# --- the exported agent's own routes ---------------------------------------


def test_outside_agent_mode_there_is_no_skill() -> None:
    assert client.get("/api/skill").status_code == 404
    status = client.get("/api/agent").json()
    assert status["agent_mode"] is False
    assert status["skill_loaded"] is False
    assert status["frozen_case_count"] == evaluator.case_count


def _agent_mode(monkeypatch, skill_path: Path) -> None:
    settings = Settings(agent_mode=True, skill_path=str(skill_path))
    monkeypatch.setattr(agent_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(root_routes, "get_settings", lambda: settings)


def test_agent_mode_serves_the_skill_and_its_own_page(monkeypatch, tmp_path: Path) -> None:
    project = approved_project(monkeypatch, "computer")
    manifest = client.post(packages_url(project), json={"language": "en"}).json()
    archive, root = read_zip(
        client.get(f"{packages_url(project)}/{manifest['package_id']}/download").content
    )
    skill_path = tmp_path / "skill.json"
    skill_path.write_bytes(archive.read(f"{root}/skill/skill.json"))
    _agent_mode(monkeypatch, skill_path)

    skill = client.get("/api/skill")
    assert skill.status_code == 200
    assert skill.json()["project_id"] == project["project_id"]

    status = client.get("/api/agent").json()
    assert status["agent_mode"] is True
    assert status["skill_loaded"] is True
    assert status["step_count"] == 2
    assert status["destination"] == "computer"

    page = client.get("/")
    assert page.status_code == 200
    assert "agent.js" in page.text
    assert client.get("/static/agent.js").status_code == 200


def test_a_skill_that_breaks_its_guarantees_is_refused(monkeypatch, tmp_path: Path) -> None:
    project = approved_project(monkeypatch, "computer")
    manifest = client.post(packages_url(project), json={}).json()
    archive, root = read_zip(
        client.get(f"{packages_url(project)}/{manifest['package_id']}/download").content
    )
    tampered = archive.read(f"{root}/skill/skill.json").decode("utf-8").replace(
        '"approved_for_execution": false', '"approved_for_execution": true'
    )
    assert '"approved_for_execution": true' in tampered
    skill_path = tmp_path / "skill.json"
    skill_path.write_text(tampered, encoding="utf-8")
    _agent_mode(monkeypatch, skill_path)

    response = client.get("/api/skill")

    assert response.status_code == 503
    assert "contract" in response.json()["detail"]
    assert client.get("/api/agent").json()["skill_loaded"] is False


def test_a_missing_skill_file_is_reported_not_faked(monkeypatch, tmp_path: Path) -> None:
    _agent_mode(monkeypatch, tmp_path / "nowhere.json")

    assert client.get("/api/skill").status_code == 503
    assert "skill_error" in client.get("/api/agent").json()

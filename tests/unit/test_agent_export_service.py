"""Tests for the exported agent package builder.

A package is the one artefact that leaves the review gate behind, so these
tests hold the properties that make it trustworthy once it is out of reach:

- only a person-approved procedure can become one;
- nothing private enters the tree, whatever is lying around the source root;
- the protected evaluation cases are copied exactly, never rewritten;
- the guarantees are types, so a package cannot claim more than it is;
- the same records produce the same bytes, so a rebuild can be checked
  against the manifest it was first written with.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile

import pytest
from pydantic import ValidationError

from app.models.agent_package import AgentGuarantees, ExportedAgentSkill
from app.models.procedure import Procedure, ProcedureStep
from app.models.project import (
    ComputerExecutionContract,
    ProjectDraft,
    RobotExecutionContract,
)
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.models.task import TaskDefinition
from app.services.adaptation_service import DestinationAdaptationService
from app.services.agent_export_service import (
    AgentExportRefused,
    AgentExportService,
    AgentPackageNotFoundError,
)
from app.services.record_store import JsonRecordStore


EXPORTED_AT = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)


# --- fixtures --------------------------------------------------------------


@pytest.fixture
def app_root(tmp_path: Path) -> Path:
    """A source root with things that must ship and things that must not."""
    root = tmp_path / "repo"
    (root / "app" / "static").mkdir(parents=True)
    (root / "app" / "main.py").write_text("# the application\n", encoding="utf-8")
    (root / "app" / "static" / "agent.js").write_text("// ui\n", encoding="utf-8")
    # Must never ship: bytecode, a stray env file, and uploaded media.
    (root / "app" / "__pycache__").mkdir()
    (root / "app" / "__pycache__" / "main.cpython-312.pyc").write_bytes(b"\x00")
    (root / "app" / ".env").write_text("GOOGLE_API_KEY=leak\n", encoding="utf-8")
    (root / "app" / "uploads").mkdir()
    (root / "app" / "uploads" / "video.mp4").write_bytes(b"\x00\x01")
    (root / "requirements.txt").write_text(
        "fastapi\npydantic\nnot-a-real-distribution-xyz\n", encoding="utf-8"
    )
    return root


@pytest.fixture
def evaluations(tmp_path: Path) -> Path:
    directory = tmp_path / "evaluations"
    directory.mkdir()
    (directory / "case-a.json").write_bytes(b'{"case_id": "a", "expected": {"x": 1}}\n')
    (directory / "case-b.json").write_bytes(b'{"case_id": "b",\n  "expected": {"y": 2}}')
    # Documentation sits beside the cases and is not a case.
    (directory / "README.md").write_text("# not a case\n", encoding="utf-8")
    return directory


@pytest.fixture
def store(tmp_path: Path) -> JsonRecordStore:
    return JsonRecordStore(tmp_path / "agent-packages")


@pytest.fixture
def service(app_root: Path, evaluations: Path, store: JsonRecordStore) -> AgentExportService:
    return AgentExportService(
        app_root=app_root,
        evaluations_dir=evaluations,
        app_version="0.1.0-test",
        store=store,
    )


def procedure(actions: list[str]) -> Procedure:
    return Procedure(
        task="Supinate the forearm",
        objective="Demonstrate supination and pronation.",
        inputs=["A visible forearm"],
        outputs=["Palm facing up"],
        steps=[
            ProcedureStep(step=i + 1, action=action, source_timestamps=["00:05"], evidence="Seen.")
            for i, action in enumerate(actions)
        ],
        rules=["Keep the elbow still."],
        uncertainties=["Speed is not stated."],
    )


def project(destination: str, project_id: str = "prj_test00000001") -> ProjectDraft:
    contract = (
        RobotExecutionContract(robot_model="APRENDIZ SimArm-6")
        if destination == "robot"
        else ComputerExecutionContract(application="Google Chrome")
    )
    return ProjectDraft(
        project_id=project_id,
        task_definition=TaskDefinition(
            task_name="Forearm supination",
            objective="Demonstrate supination and pronation.",
        ),
        destination_contract=contract,
        is_sufficiently_clear=True,
        next_action="choose_source",
    )


def record(
    actions: list[str] | None = None,
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
    project_id: str = "prj_test00000001",
) -> ProjectVideoProcedureRecord:
    actions = ["Rotate the palm upward."] if actions is None else actions
    return ProjectVideoProcedureRecord(
        extraction_id="vpr_test00000001",
        project_id=project_id,
        procedure_version=1,
        source_url="https://youtube.com/shorts/P-7Mfa5a8Uk",
        status=status,
        procedure=procedure(actions) if actions else None,
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=4.4,
        created_at=datetime(2026, 9, 7, 6, 30, tzinfo=timezone.utc),
        reviewed_at=datetime(2026, 9, 7, 6, 31, tzinfo=timezone.utc),
        review_notes="Steps reviewed.",
    )


def build(service: AgentExportService, destination: str = "robot", **overrides):
    return service.build(
        project=project(destination),
        record=record(),
        language=overrides.pop("language", "es"),
        exported_at=overrides.pop("exported_at", EXPORTED_AT),
        **overrides,
    )


# --- refusing --------------------------------------------------------------


def test_an_unapproved_procedure_cannot_be_exported(service) -> None:
    for status in [
        ProjectVideoProcedureStatus.AWAITING_REVIEW,
        ProjectVideoProcedureStatus.REJECTED,
        ProjectVideoProcedureStatus.EXTRACTION_FAILED,
    ]:
        with pytest.raises(AgentExportRefused):
            service.build(project=project("robot"), record=record(status=status))


def test_an_approved_record_without_a_procedure_is_refused(service) -> None:
    with pytest.raises(AgentExportRefused):
        service.build(project=project("robot"), record=record(actions=[]))


def test_a_record_from_another_project_is_refused(service) -> None:
    with pytest.raises(AgentExportRefused):
        service.build(project=project("robot", "prj_other"), record=record())


# --- what is inside --------------------------------------------------------


def test_the_package_carries_every_documented_file(service) -> None:
    package = build(service)

    assert {
        "skill/skill.json",
        "manifest.json",
        "Dockerfile",
        "compose.yaml",
        ".env.example",
        "agent.py",
        "start.sh",
        "start.ps1",
        "README.md",
        "requirements.lock",
        "evaluations/case-a.json",
        "evaluations/case-b.json",
        "app/main.py",
        "app/static/agent.js",
    } <= set(package.files)


def test_nothing_private_enters_the_package(service) -> None:
    """The source root deliberately contains things that must stay behind."""
    package = build(service)

    for path in package.files:
        parts = set(Path(path).parts)
        assert ".env" not in parts
        assert "uploads" not in parts
        assert "__pycache__" not in parts
        assert not path.endswith(".pyc")
    # The runtime template ships; it holds no secret and is documented.
    assert ".env.example" in package.files
    assert "evaluations/README.md" not in package.files
    assert b"GOOGLE_API_KEY" not in b"".join(package.files.values())


def test_frozen_cases_are_copied_byte_for_byte(service, evaluations) -> None:
    package = build(service)

    for name in ("case-a.json", "case-b.json"):
        assert package.files[f"evaluations/{name}"] == (evaluations / name).read_bytes()
    assert package.manifest.frozen_case_count == 2


def test_the_skill_is_built_on_the_shared_skill_contract(service) -> None:
    package = build(service, "robot")

    skill = ExportedAgentSkill.model_validate_json(package.files["skill/skill.json"])
    assert skill.skill.version == 1
    assert skill.skill.name == "Forearm supination"
    assert skill.skill.sources == ["https://youtube.com/shorts/P-7Mfa5a8Uk"]
    assert skill.skill.inputs == {"input_1": "A visible forearm"}
    # Instructor examples are not attached to an extraction yet; say so.
    assert skill.skill.examples == []
    assert skill.skill.evaluation["frozen_case_count"] == 2
    assert isinstance(skill.destination_contract, RobotExecutionContract)
    assert skill.lineage.review_notes == "Steps reviewed."
    assert skill.exported_at == EXPORTED_AT
    assert skill.guarantees.model_dump() == {
        "approved_for_execution": False,
        "physically_measured": False,
        "hardware_execution_approved": False,
        "model_weights_updated": False,
        "uploads_included": False,
        "secrets_included": False,
        "provider_calls_at_runtime": False,
    }


def test_guarantees_cannot_be_flipped() -> None:
    """They are types, not fields: a package claiming more fails validation."""
    with pytest.raises(ValidationError):
        AgentGuarantees(approved_for_execution=True)  # type: ignore[arg-type]


def test_evidence_that_does_not_fit_the_destination_is_dropped(service) -> None:
    """A computer agent carries no robot motion; a robot agent no practices."""
    package = build(service, "computer")

    skill = ExportedAgentSkill.model_validate_json(package.files["skill/skill.json"])
    assert skill.destination.value == "computer"
    assert skill.motion_evidence is None
    assert skill.retarget is None
    assert isinstance(skill.destination_contract, ComputerExecutionContract)


# --- reproducibility -------------------------------------------------------


def test_the_same_inputs_produce_the_same_bytes_and_id(service) -> None:
    first = build(service)
    second = build(service)
    later = build(service, exported_at=EXPORTED_AT.replace(minute=1))

    assert first.manifest.package_id == second.manifest.package_id
    assert first.zip_bytes() == second.zip_bytes()
    assert later.manifest.package_id != first.manifest.package_id


def test_the_packaged_adaptation_is_reproducible_across_fresh_plans(service) -> None:
    """adapt() stamps a random plan id each call; the package must not care."""
    adapt = DestinationAdaptationService()
    first_plan = adapt.adapt(project("robot"), record(), None, "es")
    second_plan = adapt.adapt(project("robot"), record(), None, "es")
    assert first_plan.plan_id != second_plan.plan_id

    first = build(service, adaptation=first_plan)
    second = build(service, adaptation=second_plan)

    assert first.zip_bytes() == second.zip_bytes()
    skill = ExportedAgentSkill.model_validate_json(first.files["skill/skill.json"])
    assert skill.adaptation is not None
    assert skill.adaptation.plan_id.startswith("adp_")
    assert skill.adaptation.steps == first_plan.steps


def test_the_manifest_digests_match_the_files(service) -> None:
    package = build(service)

    listed = {entry.path for entry in package.manifest.files}
    # The manifest cannot list itself without circularity, and lists all else.
    assert listed == set(package.files) - {"manifest.json"}
    for entry in package.manifest.files:
        content = package.files[entry.path]
        assert entry.size_bytes == len(content)
        assert entry.sha256 == sha256(content).hexdigest()


def test_requirements_are_pinned_to_installed_versions(service) -> None:
    lock = build(service).files["requirements.lock"].decode("utf-8")

    assert any(line.startswith("fastapi==") for line in lock.splitlines())
    assert any(line.startswith("pydantic==") for line in lock.splitlines())
    # A name that is not installed is kept, and honestly marked unpinned.
    assert "not-a-real-distribution-xyz  # not installed" in lock


# --- the generated runtime -------------------------------------------------


def test_dockerfile_mirrors_the_application_discipline(service) -> None:
    robot = build(service, "robot").files["Dockerfile"].decode("utf-8")
    computer = build(service, "computer").files["Dockerfile"].decode("utf-8")

    for text in (robot, computer):
        assert text.startswith("# Exported APRENDIZ agent")
        assert "FROM python:3.12-slim" in text
        assert "USER 10001:10001" in text
        assert "HEALTHCHECK" in text and "/health" in text
        assert "COPY --chown=10001:10001 skill ./skill" in text
        assert "COPY --chown=10001:10001 evaluations ./evaluations" in text
        assert "requirements.lock" in text
        assert ".env" not in text
    # Chromium only earns its gigabyte where an approved rehearsal could run.
    assert "ARG INSTALL_BROWSER=false" in robot
    assert "ARG INSTALL_BROWSER=true" in computer


def test_compose_disables_every_provider_call_and_keeps_the_hardening(service) -> None:
    compose = build(service).files["compose.yaml"].decode("utf-8")

    assert 'AGENT_MODE: "true"' in compose
    assert "SKILL_PATH: /app/skill/skill.json" in compose
    assert "FROZEN_CASES_DIR: /app/evaluations" in compose
    assert 'GOOGLE_GENAI_ENABLED: "false"' in compose
    assert "read_only: true" in compose
    assert "cap_drop:" in compose and "- ALL" in compose
    assert "no-new-privileges:true" in compose


def test_the_readme_follows_the_requested_language(service) -> None:
    spanish = build(service, language="es").files["README.md"].decode("utf-8")
    english = build(service, language="en").files["README.md"].decode("utf-8")

    assert spanish.startswith("# Agente APRENDIZ")
    assert "## Qué no es" in spanish
    assert english.startswith("# APRENDIZ agent")
    assert "## What it is not" in english


def test_generated_text_carries_no_ai_attribution(service) -> None:
    """AGENTS.md forbids it in exported artefacts as much as in commits."""
    package = build(service)

    for path in ("README.md", "Dockerfile", "compose.yaml", "agent.py", "start.sh", "start.ps1", ".env.example"):
        text = package.files[path].decode("utf-8").lower()
        assert "claude" not in text
        assert "generated by" not in text
        assert "co-authored" not in text


def test_the_zip_is_rooted_in_its_directory_and_launchers_are_executable(service) -> None:
    package = build(service)

    with zipfile.ZipFile(io.BytesIO(package.zip_bytes())) as archive:
        names = archive.namelist()
        root = package.manifest.directory_name
        assert names and all(name.startswith(f"{root}/") for name in names)
        assert (archive.getinfo(f"{root}/start.sh").external_attr >> 16) & 0o777 == 0o755
        assert (archive.getinfo(f"{root}/README.md").external_attr >> 16) & 0o777 == 0o644
        manifest = json.loads(archive.read(f"{root}/manifest.json"))
        assert manifest["package_id"] == package.manifest.package_id


# --- retention -------------------------------------------------------------


def test_manifests_are_retained_and_scoped_to_their_project(service, app_root, evaluations, store) -> None:
    package = build(service)

    # A fresh process sees the manifest, but not the bytes.
    reloaded = AgentExportService(
        app_root=app_root, evaluations_dir=evaluations, app_version="0.1.0-test", store=store
    )
    assert [m.package_id for m in reloaded.list_for_project("prj_test00000001")] == [
        package.manifest.package_id
    ]
    assert reloaded.built(package.manifest.package_id) is None
    with pytest.raises(AgentPackageNotFoundError):
        reloaded.get("prj_someone_else", package.manifest.package_id)

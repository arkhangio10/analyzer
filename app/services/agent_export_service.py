"""Build the exported agent package: a self-contained, reproducible Docker
delivery of one approved procedure and the agent that serves it.

The shape is deliberate. The exported agent is *this application*, pinned to
the exact dependency versions that produced the export, with the approved
skill baked in and every provider call disabled. That gives three things at
once: a reproducible build, reuse of every typed guarantee the application
already makes, and no second runtime to keep honest.

What the package refuses to contain is as important as what it contains.
Uploaded video, `.env` contents, credentials, and workflow records other than
the one being exported never enter the tree; a test walks every path to hold
that line. Frozen evaluation cases are copied byte-for-byte, because a case
the learning loop can edit proves nothing.

Everything here is deterministic. Given the same records and the same
`exported_at`, `build` returns the same bytes and the same package id, which
is what lets a package be rebuilt after a restart and checked against the
digests in the manifest it was first written with.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata
import io
import json
from pathlib import Path
import re
from typing import Literal
import zipfile

from app.models.adaptation import DestinationAdaptationPlan
from app.models.agent_package import (
    AgentGuarantees,
    AgentPackageManifest,
    ExportedAgentSkill,
    ExtractionLineage,
    PackageFile,
)
from app.models.computer_practice import ComputerPractice
from app.models.motion_analysis import MotionAnalysisRecord, MotionRetargetVerdict
from app.models.project import ExecutionDestination, ProjectDraft
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.models.skill import Skill
from app.services.record_store import RecordStore


Language = Literal["es", "en"]

BASE_IMAGE = "python:3.12-slim"
RUNTIME_UID = 10001
DEFAULT_PORT = 8080

# Nothing under these names may enter a package, whatever the caller passes.
_EXCLUDED_DIR_NAMES = {"__pycache__", ".pytest_cache", ".git"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
_FORBIDDEN_PATH_PARTS = {".env", "uploads", "records", ".runtime", ".venv"}


class AgentExportRefused(ValueError):
    """Raised when the records cannot honestly become a package."""


class AgentPackageNotFoundError(LookupError):
    """Raised when a package does not belong to the requested project."""


class AgentPackage:
    """One built package: its manifest and every file's bytes."""

    def __init__(self, manifest: AgentPackageManifest, files: dict[str, bytes]) -> None:
        self.manifest = manifest
        self.files = files

    def zip_bytes(self) -> bytes:
        """Return the package as one zip, byte-identical for identical inputs.

        Zip entries carry the package's own `created_at` rather than the wall
        clock, so two builds of the same package produce the same archive.
        """
        stamp = self.manifest.created_at.astimezone(timezone.utc)
        date_time = (
            stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second,
        )
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(self.files):
                info = zipfile.ZipInfo(f"{self.manifest.directory_name}/{path}", date_time)
                info.compress_type = zipfile.ZIP_DEFLATED
                # Launchers must be executable when unzipped on a POSIX host.
                info.external_attr = (0o755 if path.endswith(".sh") else 0o644) << 16
                archive.writestr(info, self.files[path])
        return buffer.getvalue()


class AgentExportService:
    """Assemble, retain, list and rebuild exported agent packages."""

    def __init__(
        self,
        *,
        app_root: Path | str,
        evaluations_dir: Path | str,
        app_version: str,
        store: RecordStore | None = None,
    ) -> None:
        self._app_root = Path(app_root)
        self._evaluations_dir = Path(evaluations_dir)
        self._app_version = app_version
        self._store = store
        self._manifests: dict[str, AgentPackageManifest] = (
            store.load_all(AgentPackageManifest) if store else {}
        )
        # Built bytes are kept only for this process; a restart rebuilds them
        # from the records, and the manifest's digests say whether it matched.
        self._built: dict[str, AgentPackage] = {}

    @property
    def is_durable(self) -> bool:
        """Report whether package manifests survive a restart."""
        return bool(self._store and self._store.is_durable)

    # --- reading -----------------------------------------------------------

    def list_for_project(self, project_id: str) -> list[AgentPackageManifest]:
        """Return one project's packages, newest first."""
        matches = [m for m in self._manifests.values() if m.project_id == project_id]
        return sorted(matches, key=lambda m: m.created_at, reverse=True)

    def get(self, project_id: str, package_id: str) -> AgentPackageManifest:
        """Return one manifest, refusing to reveal another project's."""
        manifest = self._manifests.get(package_id)
        if manifest is None or manifest.project_id != project_id:
            raise AgentPackageNotFoundError(package_id)
        return manifest

    def built(self, package_id: str) -> AgentPackage | None:
        """Return the package bytes if this process still holds them."""
        return self._built.get(package_id)

    # --- building ----------------------------------------------------------

    def build(
        self,
        *,
        project: ProjectDraft,
        record: ProjectVideoProcedureRecord,
        adaptation: DestinationAdaptationPlan | None = None,
        motion: MotionAnalysisRecord | None = None,
        practices: Sequence[ComputerPractice] = (),
        language: Language = "es",
        exported_at: datetime | None = None,
    ) -> AgentPackage:
        """Turn one approved procedure and its evidence into a package.

        Refuses anything a person has not approved, in the same words the
        adaptation service uses, because a package is the one artefact that
        leaves the review gate behind.
        """
        if record.project_id != project.project_id:
            raise AgentExportRefused("The extraction belongs to a different project.")
        if record.status is not ProjectVideoProcedureStatus.APPROVED:
            raise AgentExportRefused(
                "Only a procedure approved by a person can be exported."
            )
        if record.procedure is None or record.procedure_version is None:
            raise AgentExportRefused(
                "The approved record carries no structured procedure to export."
            )
        for practice in practices:
            if practice.project_id != project.project_id:
                raise AgentExportRefused("A practice belongs to a different project.")

        created_at = (exported_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        destination = project.destination_contract.destination
        # The retarget verdict is decided when the analysis is made, so it is
        # carried from there rather than recomputed with possibly new inputs.
        retarget: MotionRetargetVerdict | None = motion.retarget if motion else None
        version = record.procedure_version
        # The adaptation plan is recomputed on demand and stamped with a fresh
        # random id each time, while everything else in it follows from the
        # record. A package must be reproducible from its records, so the
        # packaged copy is identified by what it was built from instead.
        if adaptation is not None:
            adaptation = adaptation.model_copy(
                update={"plan_id": self._plan_id(record.extraction_id, version, destination)}
            )
        frozen_cases = self._frozen_case_files()

        skill = ExportedAgentSkill(
            language=language,
            skill=self._skill(project, record, frozen_cases),
            project_id=project.project_id,
            extraction_id=record.extraction_id,
            procedure_version=version,
            destination=destination,
            destination_contract=project.destination_contract,
            adaptation=adaptation,
            motion_evidence=motion if destination is ExecutionDestination.ROBOT else None,
            retarget=retarget if destination is ExecutionDestination.ROBOT else None,
            practices=list(practices) if destination is ExecutionDestination.COMPUTER else [],
            lineage=ExtractionLineage(
                source_url=record.source_url,
                provider=record.provider,
                requested_model=record.requested_model,
                model_version=record.model_version,
                usage=record.usage,
                elapsed_seconds=record.elapsed_seconds,
                extracted_at=record.created_at,
                reviewed_at=record.reviewed_at,
                review_notes=record.review_notes,
            ),
            exported_at=created_at,
        )

        package_id = self._package_id(project.project_id, record.extraction_id, version, created_at)
        directory_name = f"aprendiz-agent-{_slug(project.project_id)}-v{version}"
        install_browser = destination is ExecutionDestination.COMPUTER

        files: dict[str, bytes] = {}
        files["skill/skill.json"] = _json_bytes(skill.model_dump(mode="json"))
        files["requirements.lock"] = self._requirements_lock().encode("utf-8")
        files["Dockerfile"] = _dockerfile(install_browser).encode("utf-8")
        files["compose.yaml"] = _compose(destination, install_browser).encode("utf-8")
        files[".env.example"] = _env_example(destination, language).encode("utf-8")
        files["agent.py"] = _agent_py().encode("utf-8")
        files["start.sh"] = _start_sh().encode("utf-8")
        files["start.ps1"] = _start_ps1().encode("utf-8")
        files["README.md"] = _readme(skill, project, language, frozen_cases).encode("utf-8")
        for name, content in frozen_cases:
            files[f"evaluations/{name}"] = content
        for relative, content in self._app_snapshot():
            files[f"app/{relative}"] = content

        self._assert_clean(files)

        manifest = AgentPackageManifest(
            package_id=package_id,
            project_id=project.project_id,
            extraction_id=record.extraction_id,
            procedure_version=version,
            destination=destination,
            language=language,
            app_version=self._app_version,
            base_image=BASE_IMAGE,
            created_at=created_at,
            directory_name=directory_name,
            files=[
                PackageFile(path=path, size_bytes=len(content), sha256=sha256(content).hexdigest())
                for path, content in sorted(files.items())
            ],
            launcher=["start.sh", "start.ps1"],
            frozen_case_count=len(frozen_cases),
            guarantees=AgentGuarantees(),
        )
        files["manifest.json"] = _json_bytes(manifest.model_dump(mode="json"))

        package = AgentPackage(manifest, files)
        self._manifests[package_id] = manifest
        self._built[package_id] = package
        if self._store:
            self._store.save(package_id, manifest)
        return package

    # --- the pieces --------------------------------------------------------

    @staticmethod
    def _plan_id(extraction_id: str, version: int, destination: ExecutionDestination) -> str:
        digest = sha256(f"{extraction_id}|{version}|{destination.value}".encode("utf-8")).hexdigest()
        return f"adp_{digest[:12]}"

    @staticmethod
    def _package_id(project_id: str, extraction_id: str, version: int, created_at: datetime) -> str:
        digest = sha256(
            f"{project_id}|{extraction_id}|{version}|{created_at.isoformat()}".encode("utf-8")
        ).hexdigest()
        return f"agpk_{digest[:12]}"

    def _skill(
        self,
        project: ProjectDraft,
        record: ProjectVideoProcedureRecord,
        frozen_cases: list[tuple[str, bytes]],
    ) -> Skill:
        procedure = record.procedure
        assert procedure is not None and record.procedure_version is not None
        return Skill(
            skill_id=f"{project.project_id}:{record.extraction_id}:v{record.procedure_version}",
            name=project.task_definition.task_name,
            version=record.procedure_version,
            objective=procedure.objective,
            inputs={f"input_{i}": value for i, value in enumerate(procedure.inputs, start=1)},
            outputs={f"output_{i}": value for i, value in enumerate(procedure.outputs, start=1)},
            procedure=procedure,
            # Instructor examples are not yet attached to an extraction, and an
            # empty list says so more honestly than a fabricated one would.
            examples=[],
            sources=[record.source_url],
            confidence=None,
            evaluation={
                "frozen_case_count": len(frozen_cases),
                "frozen_case_files": [name for name, _ in frozen_cases],
                "note": (
                    "Cases are graded by the shipped evaluator without disclosing "
                    "expected answers. A pass on a generated case is not external "
                    "validation."
                ),
            },
        )

    def _frozen_case_files(self) -> list[tuple[str, bytes]]:
        """Copy the protected cases exactly as they are on disk."""
        if not self._evaluations_dir.is_dir():
            return []
        return sorted(
            (path.name, path.read_bytes())
            for path in self._evaluations_dir.iterdir()
            if path.is_file() and path.suffix == ".json"
        )

    def _app_snapshot(self) -> Iterable[tuple[str, bytes]]:
        """Yield the application source the image is built from."""
        root = self._app_root / "app"
        if not root.is_dir():
            raise AgentExportRefused(f"Application source was not found at {root}.")
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in _EXCLUDED_DIR_NAMES for part in relative.parts):
                continue
            if any(part in _FORBIDDEN_PATH_PARTS for part in relative.parts):
                continue
            if path.suffix in _EXCLUDED_SUFFIXES:
                continue
            yield relative.as_posix(), path.read_bytes()

    def _requirements_lock(self) -> str:
        """Pin every dependency to the version that produced this export."""
        source = self._app_root / "requirements.txt"
        if not source.is_file():
            source = self._app_root / "requirements.lock"
        names = [
            line.strip()
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ] if source.is_file() else []
        lines = [
            "# Exact versions installed when this agent was exported. Installing",
            "# from this file rebuilds the same image; do not loosen it casually.",
        ]
        for requirement in names:
            name = re.split(r"[=<>!~\[;\s]", requirement, maxsplit=1)[0]
            try:
                lines.append(f"{name}=={metadata.version(name)}")
            except metadata.PackageNotFoundError:
                lines.append(f"{requirement}  # not installed at export time; unpinned")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _assert_clean(files: dict[str, bytes]) -> None:
        """Refuse a tree that would carry something it must not."""
        for path in files:
            parts = set(Path(path).parts)
            if parts & _FORBIDDEN_PATH_PARTS:
                raise AgentExportRefused(f"Refusing to package {path}.")


# --- generated files --------------------------------------------------------


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-") or "agent"


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _dockerfile(install_browser: bool) -> str:
    return f"""# Exported APRENDIZ agent. Same discipline as the application image it came
# from: pinned base, non-root runtime, no secrets, a health check the launcher
# and Compose can trust.
FROM {BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \\
    PORT={DEFAULT_PORT}

WORKDIR /app

COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

# Chromium is only useful to an agent that can run an approved browser
# rehearsal, so a robot agent leaves it out and stays about a gigabyte smaller.
ARG INSTALL_BROWSER={"true" if install_browser else "false"}
RUN if [ "$INSTALL_BROWSER" = "true" ]; then \\
        playwright install --with-deps --only-shell chromium \\
        && chmod -R a+rX /ms-playwright; \\
    else \\
        echo "Skipping Chromium; browser execution is unavailable in this agent."; \\
    fi

RUN groupadd --system --gid {RUNTIME_UID} aprendiz \\
    && useradd --system --uid {RUNTIME_UID} --gid {RUNTIME_UID} --no-create-home aprendiz \\
    && mkdir -p /app/.runtime /data \\
    && chown -R {RUNTIME_UID}:{RUNTIME_UID} /app/.runtime /data

COPY --chown={RUNTIME_UID}:{RUNTIME_UID} app ./app
# The skill and the protected evaluation cases are part of the image, so a
# mounted volume can neither swap what the agent learned nor edit the answers
# it is graded against.
COPY --chown={RUNTIME_UID}:{RUNTIME_UID} skill ./skill
COPY --chown={RUNTIME_UID}:{RUNTIME_UID} evaluations ./evaluations

USER {RUNTIME_UID}:{RUNTIME_UID}

EXPOSE {DEFAULT_PORT}

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \\
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:{DEFAULT_PORT}/health', timeout=2).read()"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${{PORT}}"]
"""


def _compose(destination: ExecutionDestination, install_browser: bool) -> str:
    browser = "true" if install_browser else "false"
    return f"""# Runs the exported agent with the same hardening as the application it came
# from. Nothing here is a secret; runtime configuration comes from .env.
services:
  agent:
    build:
      context: .
      args:
        INSTALL_BROWSER: "{browser}"
    ports:
      - "${{AGENT_PORT:-{DEFAULT_PORT}}}:{DEFAULT_PORT}"
    environment:
      APP_ENV: agent
      AGENT_MODE: "true"
      SKILL_PATH: /app/skill/skill.json
      FROZEN_CASES_DIR: /app/evaluations
      DATA_DIR: /data
      # The agent serves what it learned. It makes no provider call.
      GOOGLE_GENAI_ENABLED: "false"
      GOOGLE_GENAI_USE_VERTEXAI: "false"
      COMPUTER_EXECUTION_BOUNDARY: application_container
      COMPUTER_BROWSER_ENABLED: "{browser}"
    volumes:
      - agent-data:/data
    read_only: true
    tmpfs:
      - /app/.runtime:rw,noexec,nosuid,nodev,size=64m,uid={RUNTIME_UID},gid={RUNTIME_UID},mode=0700
      - /tmp:rw,noexec,nosuid,nodev,size=128m,uid={RUNTIME_UID},gid={RUNTIME_UID},mode=0700
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    pids_limit: 128
    shm_size: 256mb
    init: true
    restart: unless-stopped

volumes:
  agent-data:
"""


def _env_example(destination: ExecutionDestination, language: Language) -> str:
    if language == "es":
        head = (
            "# Configuración de ejecución del agente exportado. Copia este archivo a\n"
            "# `.env` y ajústalo. No hace falta ninguna clave ni credencial para\n"
            "# ejecutar el agente: sirve lo que aprendió sin llamar a ningún proveedor.\n"
            "# Nada de este archivo se hornea en la imagen; se lee al arrancar.\n"
        )
    else:
        head = (
            "# Runtime configuration for the exported agent. Copy this file to `.env`\n"
            "# and adjust it. No key or credential is needed to run the agent: it\n"
            "# serves what it learned without calling any provider. Nothing in this\n"
            "# file is baked into the image; it is read at start-up.\n"
        )
    body = f"AGENT_PORT={DEFAULT_PORT}\n"
    if destination is ExecutionDestination.COMPUTER:
        body += (
            "\n# Approved browser rehearsals run inside the container's own Chromium.\n"
            "COMPUTER_BROWSER_ENABLED=true\n"
        )
    return head + "\n" + body


def _agent_py() -> str:
    return '''"""Entrypoint for the exported APRENDIZ agent.

Docker runs this for you; `start.sh` or `start.ps1` runs Docker for you. If
you happen to have Python and the pinned dependencies installed, this file
starts the same agent directly.
"""

import os

import uvicorn


def main() -> None:
    os.environ.setdefault("AGENT_MODE", "true")
    os.environ.setdefault("SKILL_PATH", os.path.join(os.path.dirname(__file__), "skill", "skill.json"))
    os.environ.setdefault("FROZEN_CASES_DIR", os.path.join(os.path.dirname(__file__), "evaluations"))
    os.environ.setdefault("GOOGLE_GENAI_ENABLED", "false")
    port = int(os.environ.get("PORT", os.environ.get("AGENT_PORT", "8080")))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
'''


def _start_sh() -> str:
    return f"""#!/usr/bin/env sh
# Start the exported agent and open its local interface. Needs Docker only.
set -eu
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
PORT_VALUE="$(grep -E '^AGENT_PORT=' .env | cut -d= -f2)"
PORT_VALUE="${{PORT_VALUE:-{DEFAULT_PORT}}}"
docker compose up -d --build
echo "Agent is starting at http://localhost:${{PORT_VALUE}}"
if command -v xdg-open >/dev/null 2>&1; then xdg-open "http://localhost:${{PORT_VALUE}}" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then open "http://localhost:${{PORT_VALUE}}" || true
fi
"""


def _start_ps1() -> str:
    return f"""# Start the exported agent and open its local interface. Needs Docker only.
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path ".env")) {{ Copy-Item ".env.example" ".env" }}
$portLine = Get-Content ".env" | Where-Object {{ $_ -match '^AGENT_PORT=' }} | Select-Object -First 1
$port = if ($portLine) {{ $portLine.Split('=')[1] }} else {{ "{DEFAULT_PORT}" }}
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {{ throw "Docker could not start the agent." }}
Write-Host "Agent is starting at http://localhost:$port"
Start-Process "http://localhost:$port"
"""


def _readme(
    skill: ExportedAgentSkill,
    project: ProjectDraft,
    language: Language,
    frozen_cases: list[tuple[str, bytes]],
) -> str:
    procedure = skill.skill.procedure
    steps = len(procedure.steps)
    destination = skill.destination.value
    if language == "es":
        return f"""# Agente APRENDIZ — {project.task_definition.task_name}

Versión del procedimiento: v{skill.procedure_version} · Destino: {destination} · Exportado: {skill.exported_at.isoformat()}

## Qué es

Un agente que **conoce** un procedimiento aprendido de un video que una persona
aprobó: {steps} pasos, con la marca de tiempo del video de la que salió cada uno,
sus reglas, excepciones e incertidumbres. Arranca en tu máquina y muestra lo que
aprendió en una interfaz local. No necesita ninguna clave ni credencial.

## Qué no es

Estas garantías están escritas como tipos en `skill/skill.json`, no como promesas:

- `approved_for_execution: false` — conoce el procedimiento; nadie lo ha autorizado a ejecutarlo.
- `physically_measured: false` — los ángulos de la evidencia son estimaciones de un modelo de visión, no sensores.
- `hardware_execution_approved: false` — el hardware queda detrás de un adaptador aparte con aprobación de seguridad.
- `model_weights_updated: false` — aprender aquí es adquirir memoria procedural; ningún peso cambió.
- `uploads_included: false`, `secrets_included: false` — ni tus videos ni ninguna credencial están en el paquete ni en la imagen.
- `provider_calls_at_runtime: false` — servir lo aprendido no cuesta nada.

## Ejecutar

Solo necesitas Docker.

- Linux / macOS: `./start.sh`
- Windows: `.\\start.ps1`

Ambos copian `.env.example` a `.env` si no existe, construyen la imagen a partir de
`requirements.lock` (versiones exactas, build reproducible) y abren
`http://localhost:{DEFAULT_PORT}`. `GET /health` responde cuando está listo;
`GET /api/skill` devuelve el skill completo.

## Contenido

- `skill/skill.json` — todo lo que sabe el agente, con su linaje y garantías.
- `manifest.json` — qué se empaquetó, de qué, y el SHA-256 de cada archivo.
- `app/` — el código del agente, tal cual la aplicación que lo exportó.
- `evaluations/` — {len(frozen_cases)} caso(s) de evaluación congelados, copiados byte a byte. El agente los lee; nada los escribe.
- `Dockerfile`, `compose.yaml`, `requirements.lock`, `.env.example`, `agent.py`, `start.sh`, `start.ps1`.

## Configuración

Todo se lee de `.env` al arrancar; nada se hornea en la imagen. Ver `.env.example`.
"""
    return f"""# APRENDIZ agent — {project.task_definition.task_name}

Procedure version: v{skill.procedure_version} · Destination: {destination} · Exported: {skill.exported_at.isoformat()}

## What it is

An agent that **knows** a procedure learned from a video a person approved:
{steps} steps, each with the video timestamp it came from, plus its rules,
exceptions and uncertainties. It starts on your machine and shows what it
learned in a local interface. It needs no key or credential.

## What it is not

These guarantees are written as types in `skill/skill.json`, not as promises:

- `approved_for_execution: false` — it knows the procedure; nobody has authorised it to run it.
- `physically_measured: false` — joint angles in the evidence are a vision model's estimates, not sensors.
- `hardware_execution_approved: false` — hardware stays behind a separate, safety-approved adapter.
- `model_weights_updated: false` — learning here is procedural-memory acquisition; no weights changed.
- `uploads_included: false`, `secrets_included: false` — neither your videos nor any credential is in the package or the image.
- `provider_calls_at_runtime: false` — serving what was learned costs nothing.

## Run

You only need Docker.

- Linux / macOS: `./start.sh`
- Windows: `.\\start.ps1`

Both copy `.env.example` to `.env` if it is missing, build the image from
`requirements.lock` (exact versions, reproducible build) and open
`http://localhost:{DEFAULT_PORT}`. `GET /health` answers when it is ready;
`GET /api/skill` returns the full skill.

## Contents

- `skill/skill.json` — everything the agent knows, with lineage and guarantees.
- `manifest.json` — what was packaged, from what, and each file's SHA-256.
- `app/` — the agent's code, exactly the application that exported it.
- `evaluations/` — {len(frozen_cases)} frozen evaluation case(s), copied byte for byte. The agent reads them; nothing writes them.
- `Dockerfile`, `compose.yaml`, `requirements.lock`, `.env.example`, `agent.py`, `start.sh`, `start.ps1`.

## Configuration

Everything is read from `.env` at start-up; nothing is baked into the image. See `.env.example`.
"""

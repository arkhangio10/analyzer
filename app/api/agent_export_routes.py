"""Build and download the exported agent package for one project.

Transport only. Which records may become a package, and what the package
contains, is decided in `AgentExportService`; this module gathers the retained
records the same way the adaptation route does and hands them over.
"""

from fastapi import APIRouter, HTTPException, Response, status

from app.api.runtime import (
    adaptation_service,
    agent_export_service,
    computer_practice_service,
    motion_analysis_service,
    project_service,
    project_video_procedure_service,
)
from app.models.agent_package import AgentPackageManifest, AgentPackageRequest
from app.models.project_video_procedure import ProjectVideoProcedureStatus
from app.services.adaptation_service import AdaptationNotApprovedError
from app.services.agent_export_service import (
    AgentExportRefused,
    AgentPackageNotFoundError,
)
from app.services.motion_analysis_service import MotionAnalysisNotFoundError
from app.services.project_service import ProjectNotFoundError
from app.services.project_video_procedure_service import (
    ProjectVideoProcedureNotFoundError,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/agent-packages",
    tags=["agent packages"],
)


def _project(project_id: str):
    try:
        return project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error


def _build(project_id: str, language: str, exported_at=None, extraction_id: str | None = None):
    """Gather what the project has and build from it, or say what is missing.

    A new package takes the newest approved procedure. A rebuild names the
    extraction it was first built from, so approving a later version does not
    make an older package impossible to download.
    """
    project = _project(project_id)
    if extraction_id is not None:
        try:
            record = project_video_procedure_service.get(project_id, extraction_id)
        except ProjectVideoProcedureNotFoundError as error:
            raise HTTPException(status_code=404, detail="Extraction was not found.") from error
        if record.status is not ProjectVideoProcedureStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The procedure this package was built from is not approved.",
            )
    else:
        approved = [
            item
            for item in project_video_procedure_service.list_for_project(project_id)
            if item.status is ProjectVideoProcedureStatus.APPROVED
        ]
        if not approved:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This project has no approved procedure to export yet.",
            )
        record = max(approved, key=lambda item: (item.procedure_version or 0, item.created_at))
    try:
        motion = motion_analysis_service.latest_for_extraction(record.extraction_id)
    except MotionAnalysisNotFoundError:
        motion = None
    try:
        adaptation = adaptation_service.adapt(project, record, motion, language)
    except AdaptationNotApprovedError as error:  # pragma: no cover - status filtered above
        raise HTTPException(status_code=409, detail=str(error)) from error
    try:
        return agent_export_service.build(
            project=project,
            record=record,
            adaptation=adaptation,
            motion=motion,
            practices=computer_practice_service.list_for_project_redacted(project_id),
            language=language,
            exported_at=exported_at,
        )
    except AgentExportRefused as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("", response_model=AgentPackageManifest, status_code=status.HTTP_201_CREATED)
async def build_agent_package(
    project_id: str,
    request: AgentPackageRequest,
) -> AgentPackageManifest:
    """Package the project's latest approved procedure and its evidence."""
    return _build(project_id, request.language).manifest


@router.get("", response_model=list[AgentPackageManifest])
async def list_agent_packages(project_id: str) -> list[AgentPackageManifest]:
    """List the project's packages, newest first."""
    _project(project_id)
    return agent_export_service.list_for_project(project_id)


@router.get("/{package_id}", response_model=AgentPackageManifest)
async def get_agent_package(project_id: str, package_id: str) -> AgentPackageManifest:
    """Return one package's manifest."""
    try:
        return agent_export_service.get(project_id, package_id)
    except AgentPackageNotFoundError as error:
        raise HTTPException(status_code=404, detail="Package was not found.") from error


@router.get("/{package_id}/download")
async def download_agent_package(project_id: str, package_id: str) -> Response:
    """Return the package as a zip.

    After a restart the bytes are rebuilt from the same records with the same
    `created_at`. If the rebuild does not reproduce the manifest's digests the
    records or the code changed underneath it, and the honest answer is to
    build a new package rather than serve one that no longer matches its own
    manifest.
    """
    try:
        manifest = agent_export_service.get(project_id, package_id)
    except AgentPackageNotFoundError as error:
        raise HTTPException(status_code=404, detail="Package was not found.") from error

    package = agent_export_service.built(package_id)
    if package is None:
        package = _build(
            project_id,
            manifest.language,
            exported_at=manifest.created_at,
            extraction_id=manifest.extraction_id,
        )
        expected = {(f.path, f.sha256) for f in manifest.files}
        actual = {(f.path, f.sha256) for f in package.manifest.files}
        if expected != actual:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The records or the application changed since this package "
                    "was built, so it can no longer be reproduced. Build a new one."
                ),
            )

    return Response(
        content=package.zip_bytes(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{manifest.directory_name}.zip"',
        },
    )

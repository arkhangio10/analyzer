"""Routes for video a person supplies from their own machine.

Nothing here forwards a file anywhere. An upload is written to this machine's
data directory, described by its size and hash so a person can verify what was
kept, and reported with `analysis_available` false, because extraction still
accepts only a public YouTube URL.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.runtime import project_service, video_storage
from app.models.upload import (
    ALLOWED_VIDEO_TYPES,
    UploadedVideoList,
    UploadedVideoRecord,
)
from app.services.project_service import ProjectNotFoundError
from app.services.storage_service import STORAGE_NOTE, UploadRejectedError


router = APIRouter(prefix="/api/projects/{project_id}/uploads", tags=["uploads"])


def _require_project(project_id: str) -> None:
    try:
        project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error


def _listing(project_id: str) -> UploadedVideoList:
    return UploadedVideoList(
        project_id=project_id,
        uploads=video_storage.list_for_project(project_id),
        total_bytes=video_storage.total_bytes(project_id),
        max_upload_bytes=video_storage.max_upload_bytes,
        accepted_types=sorted(ALLOWED_VIDEO_TYPES),
        storage_note=STORAGE_NOTE,
    )


@router.post("", response_model=UploadedVideoRecord, status_code=status.HTTP_201_CREATED)
async def upload_project_video(
    project_id: str,
    file: UploadFile = File(...),
) -> UploadedVideoRecord:
    """Keep one video on this machine; it is never sent to a provider."""
    _require_project(project_id)
    try:
        return video_storage.save(
            project_id,
            file.filename or "video",
            file.content_type,
            file.file,
        )
    except UploadRejectedError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("", response_model=UploadedVideoList)
async def list_project_videos(project_id: str) -> UploadedVideoList:
    """List what this machine is holding for one project."""
    _require_project(project_id)
    return _listing(project_id)


@router.delete("/{upload_id}", response_model=UploadedVideoList)
async def delete_project_video(project_id: str, upload_id: str) -> UploadedVideoList:
    """Delete one upload from this machine."""
    _require_project(project_id)
    if not video_storage.delete(project_id, upload_id):
        raise HTTPException(status_code=404, detail="Upload was not found.")
    return _listing(project_id)

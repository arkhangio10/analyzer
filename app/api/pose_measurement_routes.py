"""Routes for measuring a person's movement from a video they supplied.

Nothing on this path costs anything or leaves the machine, so there is no
spend guard here and no cost acknowledgement to give. The one acknowledgement
the request does carry is `subject_is_human`, because the landmark model
assumes a human body plan and a person has to say that is what the video
shows.

Transport only. What may be measured, what is dropped, and whether the result
survives its two audits is decided in the services.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import (
    pose_measurement_service,
    project_service,
    video_storage,
)
from app.models.pose_benchmark import PoseBenchmarkResult
from app.models.pose_measurement import PoseMeasurementRecord, PoseMeasurementRequest
from app.services.mediapipe_pose_source import (
    PoseModelUnavailable,
    PoseSourceUnreadable,
)
from app.services.pose_measurement import PoseSubjectRefused
from app.services.pose_measurement_service import PoseMeasurementNotFoundError
from app.services.project_service import ProjectNotFoundError
from app.services.storage_service import UploadNotReadableError


router = APIRouter(
    prefix="/api/projects/{project_id}/uploads/{upload_id}",
    tags=["pose measurement"],
)


def _upload(project_id: str, upload_id: str):
    try:
        project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    for record in video_storage.list_for_project(project_id):
        if record.upload_id == upload_id:
            return record
    raise HTTPException(status_code=404, detail="Upload was not found.")


@router.post(
    "/pose-measurement",
    response_model=PoseMeasurementRecord,
    status_code=status.HTTP_201_CREATED,
)
async def measure_uploaded_pose(
    project_id: str,
    upload_id: str,
    request: PoseMeasurementRequest,
) -> PoseMeasurementRecord:
    """Measure joint angles locally from one uploaded video. Costs nothing."""
    upload = _upload(project_id, upload_id)
    try:
        with video_storage.local_copy(upload) as path:
            return pose_measurement_service.measure(
                project_id=project_id,
                upload=upload,
                video_path=path,
                request=request,
            )
    except PoseModelUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except UploadNotReadableError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PoseSourceUnreadable as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except PoseSubjectRefused as error:  # pragma: no cover - typed Literal
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/pose-measurement", response_model=PoseMeasurementRecord)
async def get_uploaded_pose_measurement(
    project_id: str,
    upload_id: str,
) -> PoseMeasurementRecord:
    """Return the newest retained measurement of one upload."""
    _upload(project_id, upload_id)
    try:
        return pose_measurement_service.latest_for_upload(upload_id)
    except PoseMeasurementNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="This upload has not been measured yet.",
        ) from error


@router.get("/pose-measurement/benchmark", response_model=PoseBenchmarkResult)
async def get_pose_measurement_benchmark(
    project_id: str,
    upload_id: str,
) -> PoseBenchmarkResult:
    """Report how the newest measurement compares with a person's labels.

    A video nobody has labelled comes back `unvalidated`, which is not a pass
    and is never reported as one.
    """
    _upload(project_id, upload_id)
    try:
        record = pose_measurement_service.latest_for_upload(upload_id)
    except PoseMeasurementNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="This upload has not been measured yet.",
        ) from error
    return pose_measurement_service.benchmark(record)

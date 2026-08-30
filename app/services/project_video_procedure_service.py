"""Project workflow for approved video extraction and human review."""

from datetime import datetime, timezone
from uuid import uuid4

from app.models.project_video_procedure import (
    ProjectVideoProcedureExtractionRequest,
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureReviewRequest,
    ProjectVideoProcedureStatus,
)
from app.models.video_extraction import VideoExtractionRequest
from app.services.gemini_service import (
    GeminiConfigurationError,
    GeminiProviderError,
    GeminiResponseError,
    GeminiService,
)
from app.services.project_service import ProjectService


class ProjectVideoProcedureNotFoundError(LookupError):
    """Raised when an extraction does not belong to the requested project."""


class ProjectVideoProcedureConflictError(ValueError):
    """Raised when a review decision conflicts with extraction state."""


class ProjectVideoProcedureService:
    """Retain extraction evidence and gate later adaptation on human review."""

    def __init__(
        self,
        project_service: ProjectService,
        gemini_service: GeminiService,
    ) -> None:
        self._project_service = project_service
        self._gemini_service = gemini_service
        self._records: dict[str, ProjectVideoProcedureRecord] = {}
        self._versions: dict[str, int] = {}

    async def extract(
        self,
        project_id: str,
        request: ProjectVideoProcedureExtractionRequest,
    ) -> ProjectVideoProcedureRecord:
        project = self._project_service.get(project_id)
        extraction_id = f"vpr_{uuid4().hex[:12]}"
        source_url = str(request.video_url)
        created_at = datetime.now(timezone.utc)
        provider_request = VideoExtractionRequest(
            video_url=request.video_url,
            task_hint=request.task_hint or project.task_definition.objective,
            output_language=request.output_language,
            acknowledge_cloud_cost=request.acknowledge_cloud_cost,
        )
        try:
            result = await self._gemini_service.extract_procedure(provider_request)
        except GeminiConfigurationError as error:
            return self._store_failure(
                extraction_id,
                project_id,
                source_url,
                created_at,
                failure_code="provider_disabled",
                failure_message=str(error),
                cloud_calls_made=0,
            )
        except GeminiProviderError as error:
            return self._store_failure(
                extraction_id,
                project_id,
                source_url,
                created_at,
                failure_code=error.failure_code,
                failure_message=str(error),
                cloud_calls_made=1,
                failure_http_status=error.http_status,
                failure_provider_status=error.provider_status,
                attempted_model=error.requested_model,
            )
        except GeminiResponseError:
            return self._store_failure(
                extraction_id,
                project_id,
                source_url,
                created_at,
                failure_code="invalid_structured_response",
                failure_message=(
                    "Gemini returned no valid structured procedure; no raw response "
                    "was retained."
                ),
                cloud_calls_made=1,
            )

        version = self._versions.get(project_id, 0) + 1
        self._versions[project_id] = version
        record = ProjectVideoProcedureRecord(
            extraction_id=extraction_id,
            project_id=project_id,
            procedure_version=version,
            source_url=result.source_url,
            status=ProjectVideoProcedureStatus.AWAITING_REVIEW,
            procedure=result.procedure,
            provider=result.provider,
            requested_model=result.requested_model,
            model_version=result.model_version,
            elapsed_seconds=result.elapsed_seconds,
            usage=result.usage,
            cloud_calls_made=result.cloud_calls_made,
            created_at=created_at,
        )
        self._records[extraction_id] = record
        return record

    def get(
        self,
        project_id: str,
        extraction_id: str,
    ) -> ProjectVideoProcedureRecord:
        try:
            record = self._records[extraction_id]
        except KeyError as error:
            raise ProjectVideoProcedureNotFoundError(extraction_id) from error
        if record.project_id != project_id:
            raise ProjectVideoProcedureNotFoundError(extraction_id)
        return record

    def review(
        self,
        project_id: str,
        extraction_id: str,
        request: ProjectVideoProcedureReviewRequest,
    ) -> ProjectVideoProcedureRecord:
        record = self.get(project_id, extraction_id)
        if record.status is not ProjectVideoProcedureStatus.AWAITING_REVIEW:
            raise ProjectVideoProcedureConflictError(
                "Only a procedure awaiting review can receive a decision."
            )
        status = (
            ProjectVideoProcedureStatus.APPROVED
            if request.decision == "approve"
            else ProjectVideoProcedureStatus.REJECTED
        )
        updated = record.model_copy(
            update={
                "status": status,
                "review_notes": request.notes,
                "reviewed_at": datetime.now(timezone.utc),
            }
        )
        self._records[extraction_id] = updated
        return updated

    def _store_failure(
        self,
        extraction_id: str,
        project_id: str,
        source_url: str,
        created_at: datetime,
        *,
        failure_code: str,
        failure_message: str,
        cloud_calls_made: int,
        failure_http_status: int | None = None,
        failure_provider_status: str | None = None,
        attempted_model: str | None = None,
    ) -> ProjectVideoProcedureRecord:
        record = ProjectVideoProcedureRecord(
            extraction_id=extraction_id,
            project_id=project_id,
            source_url=source_url,
            status=ProjectVideoProcedureStatus.EXTRACTION_FAILED,
            cloud_calls_made=cloud_calls_made,
            failure_code=failure_code,
            failure_message=failure_message,
            failure_http_status=failure_http_status,
            failure_provider_status=failure_provider_status,
            attempted_model=attempted_model,
            created_at=created_at,
        )
        self._records[extraction_id] = record
        return record

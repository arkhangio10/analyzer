"""Controlled API route for the first real instructional-video experiment."""

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import gemini_service
from app.models.video_extraction import (
    VideoExtractionRequest,
    VideoExtractionResult,
)
from app.services.gemini_service import (
    GeminiConfigurationError,
    GeminiProviderError,
    GeminiResponseError,
)


router = APIRouter(prefix="/api/experiments/video", tags=["experiments"])


@router.post(
    "/extract",
    response_model=VideoExtractionResult,
    status_code=status.HTTP_200_OK,
)
async def extract_video_procedure(
    request: VideoExtractionRequest,
) -> VideoExtractionResult:
    """Run one acknowledged cloud call for an approved YouTube source."""
    try:
        return await gemini_service.extract_procedure(request)
    except GeminiConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except GeminiResponseError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error
    except GeminiProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

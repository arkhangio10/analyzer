"""Routes for reference discovery and explicit source approval."""

from fastapi import APIRouter, HTTPException, status

from app.models.source import (
    SourceApprovalRequest,
    SourceApprovalResult,
    SourceSearchRequest,
    SourceSearchResult,
)
from app.services.youtube_service import (
    SourceSearchNotFoundError,
    SourceSelectionError,
    YouTubeConfigurationError,
    YouTubeProviderError,
    YouTubeService,
)


router = APIRouter(prefix="/api/sources", tags=["sources"])
youtube_service = YouTubeService()


@router.post("/search", response_model=SourceSearchResult)
async def search_sources(request: SourceSearchRequest) -> SourceSearchResult:
    """Search for candidates without analyzing or approving them."""
    try:
        return await youtube_service.search(request)
    except YouTubeConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except YouTubeProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error


@router.post(
    "/search/{search_id}/approve",
    response_model=SourceApprovalResult,
)
async def approve_sources(
    search_id: str,
    request: SourceApprovalRequest,
) -> SourceApprovalResult:
    """Approve selected candidates without starting cloud video analysis."""
    try:
        return youtube_service.approve(search_id, request.video_ids)
    except SourceSearchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source search was not found.",
        ) from error
    except SourceSelectionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

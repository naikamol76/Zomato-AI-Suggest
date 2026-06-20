"""FastAPI Router for restaurant recommendations."""

from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_orchestrator
from app.models.preferences import UserPreferences
from app.models.response import RecommendResponse
from app.services.orchestrator import RecommendationOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Define RecommendRequest as a direct type alias of UserPreferences
# as their Pydantic properties and constraints are identical.
RecommendRequest = UserPreferences


@router.post("", response_model=RecommendResponse, status_code=status.HTTP_200_OK)
async def get_recommendations(
    request: RecommendRequest,
    orchestrator: RecommendationOrchestrator = Depends(get_orchestrator),
) -> RecommendResponse:
    """Accepts user preferences and runs the hybrid filter-then-LLM recommendation flow."""
    try:
        response = await orchestrator.get_recommendations(request)
        return response
    except ValueError as e:
        logger.warning("Invalid request values encountered during recommendation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during recommendation flow execution: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The recommendation service is temporarily unavailable. Details: {e}",
        ) from e

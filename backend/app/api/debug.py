"""Development helpers (Phase 2+). Not for production use without auth."""

from fastapi import APIRouter, Depends, Query

from app.config import Settings, get_settings
from app.deps import get_repository
from app.data.repository import RestaurantRepository
from app.models.preferences import UserPreferences
from app.models.restaurant import BudgetBand
from app.services.filter import CandidateFilterService

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/candidates")
def list_filtered_candidates(
    city: str = Query(..., min_length=1),
    budget: BudgetBand = Query(...),
    cuisine: str = Query(..., min_length=1),
    min_rating: float = Query(default=0.0, ge=0.0, le=5.0),
    max_candidates: int | None = Query(default=None, ge=1, le=100),
    repository: RestaurantRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> dict:
    """
    Run the Phase 2 filter only (no LLM). Useful for verifying constraints.
    """
    preferences = UserPreferences(
        city=city,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
    )
    cap = max_candidates or settings.max_candidates
    service = CandidateFilterService(repository)
    candidates = service.apply(preferences, max_candidates=cap)

    return {
        "count": len(candidates),
        "max_candidates": cap,
        "preferences": preferences.model_dump(),
        "candidates": [c.model_dump() for c in candidates],
    }

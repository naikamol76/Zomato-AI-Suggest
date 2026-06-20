from pydantic import BaseModel, Field

from app.models.restaurant import BudgetBand


class LlmRecommendationItem(BaseModel):
    """Single item parsed from LLM JSON output."""

    restaurant_id: str
    rank: int = Field(ge=1)
    explanation: str = ""


class LlmRecommendationPayload(BaseModel):
    """Structured LLM response before grounding validation."""

    summary: str | None = None
    recommendations: list[LlmRecommendationItem] = Field(default_factory=list)


class Recommendation(BaseModel):
    """Enriched recommendation with facts from the data store."""

    rank: int = Field(ge=1)
    restaurant_id: str
    name: str
    cuisines: str
    rating: float = Field(ge=0, le=5)
    approx_cost_for_two: float | None = Field(default=None, ge=0)
    budget_band: BudgetBand
    locality: str | None = None
    explanation: str


class ResponseMeta(BaseModel):
    candidates_considered: int
    prompt_version: str
    model: str
    summary: str | None = None


class RecommendResponse(BaseModel):
    """API response for recommendation requests (Phase 4+)."""

    recommendations: list[Recommendation] = Field(default_factory=list)
    message: str | None = None
    meta: ResponseMeta | None = None

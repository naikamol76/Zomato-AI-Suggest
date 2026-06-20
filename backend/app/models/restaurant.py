from enum import Enum

from pydantic import BaseModel, Field


class BudgetBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Restaurant(BaseModel):
    """Normalized restaurant record loaded from processed Parquet."""

    restaurant_id: str
    name: str
    city: str
    locality: str | None = None
    cuisines: str
    rating: float = Field(ge=0, le=5)
    votes: int = Field(default=0, ge=0)
    approx_cost_for_two: float | None = Field(default=None, ge=0)
    budget_band: BudgetBand

    model_config = {"frozen": True}

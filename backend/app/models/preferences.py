from pydantic import BaseModel, Field, field_validator

from app.models.restaurant import BudgetBand


class UserPreferences(BaseModel):
    """User constraints for restaurant search (hard filters)."""

    city: str = Field(min_length=1, description="City name, e.g. Bangalore")
    budget: BudgetBand = Field(description="Budget band: low, medium, or high")
    cuisine: str = Field(min_length=1, description="Cuisine substring, e.g. North Indian")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_notes: str | None = Field(
        default=None,
        max_length=500,
        description="Soft preferences passed to LLM in later phases",
    )

    @field_validator("city", "cuisine")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @field_validator("additional_notes")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

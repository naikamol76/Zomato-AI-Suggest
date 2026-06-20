"""Print filtered candidates for sample preferences (Phase 2 smoke test)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import get_settings  # noqa: E402
from app.data.repository import RestaurantRepository  # noqa: E402
from app.models.preferences import UserPreferences  # noqa: E402
from app.models.restaurant import BudgetBand  # noqa: E402
from app.services.filter import CandidateFilterService  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    settings = get_settings()
    repo = RestaurantRepository(settings.data_path)
    repo.load()

    preferences = UserPreferences(
        city="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="North Indian",
        min_rating=4.0,
    )
    service = CandidateFilterService(repo)
    candidates = service.apply(preferences, max_candidates=settings.max_candidates)

    print(f"\nPreferences: {preferences.model_dump()}")
    print(f"Candidates ({len(candidates)}):\n")
    for index, restaurant in enumerate(candidates, start=1):
        print(
            f"  {index}. {restaurant.name} | rating={restaurant.rating} | "
            f"votes={restaurant.votes} | {restaurant.budget_band.value} | {restaurant.cuisines}"
        )


if __name__ == "__main__":
    main()

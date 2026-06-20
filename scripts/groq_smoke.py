"""Smoke test for Groq API integration (Phase 3)."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import get_settings
from app.data.repository import RestaurantRepository
from app.models.preferences import UserPreferences
from app.models.restaurant import BudgetBand
from app.services.filter import CandidateFilterService
from app.services.prompt import PromptBuilder
from app.services.llm import GroqLlmClient
from app.services.parser import LlmResponseParser
from app.services.validator import RecommendationValidator

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()

    if not settings.groq_api_key:
        print("WARNING: groq_api_key (GROQ_API_KEY or LLM_API_KEY) is not set in environment!")
        print("Please check your .env file or run with mock mode.")
        sys.exit(0)

    print("Loading restaurant store repository...")
    repo = RestaurantRepository(settings.data_path)
    repo.load()

    preferences = UserPreferences(
        city="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="North Indian",
        min_rating=4.0,
        additional_notes="Prefer places known for authentic taste, good biryani, and outdoor seating if possible.",
    )

    print("Applying candidate filters...")
    filter_service = CandidateFilterService(repo)
    candidates = filter_service.apply(preferences, max_candidates=5)

    if not candidates:
        print("No candidates found matching the filters. Try relaxing filters.")
        return

    print(f"Found {len(candidates)} candidate restaurants.")

    print("Building chat prompt messages...")
    prompt_builder = PromptBuilder()
    messages = prompt_builder.build_prompt(preferences, candidates, max_recommendations=3)

    print("\nRendered prompt (User message content preview):")
    print("-" * 60)
    print(messages[1]["content"])
    print("-" * 60)

    print("\nCalling Groq API asynchronously...")
    groq_client = GroqLlmClient(settings)

    try:
        raw_response = await groq_client.complete(messages)
        print("\nRaw Groq Response:")
        print("-" * 60)
        print(raw_response)
        print("-" * 60)

        print("\nParsing response JSON...")
        parser = LlmResponseParser()
        payload = parser.parse(raw_response)

        print(f"Summary: {payload.summary}")
        print(f"Parsed {len(payload.recommendations)} recommendations.")

        print("\nValidating and enriching with store facts (grounding)...")
        validator = RecommendationValidator()
        enriched = validator.validate_and_enrich(payload, candidates)

        print(f"\nFinal Recommendations ({len(enriched)}):")
        for rec in enriched:
            print(f"\nRank {rec.rank}: {rec.name}")
            print(f"  ID: {rec.restaurant_id}")
            print(f"  Rating: {rec.rating} | Cost: {rec.approx_cost_for_two} ({rec.budget_band.value})")
            print(f"  Locality: {rec.locality}")
            print(f"  Cuisines: {rec.cuisines}")
            print(f"  Explanation: {rec.explanation}")

    except Exception as e:
        logger.exception("Groq smoke test failed")


if __name__ == "__main__":
    asyncio.run(main())

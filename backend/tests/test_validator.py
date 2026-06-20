"""Unit tests for RecommendationValidator."""

from __future__ import annotations

from pathlib import Path

from app.models.response import LlmRecommendationPayload, LlmRecommendationItem
from app.services.parser import LlmResponseParser
from app.services.validator import RecommendationValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_validate_and_enrich_valid(loaded_repository) -> None:
    parser = LlmResponseParser()
    validator = RecommendationValidator()

    valid_file = FIXTURES_DIR / "llm_valid.json"
    raw_text = valid_file.read_text(encoding="utf-8")
    payload = parser.parse(raw_text)

    # Get all restaurants from sample loaded repository
    df = loaded_repository.get_dataframe()
    candidates = loaded_repository.dataframe_to_restaurants(df)

    enriched = validator.validate_and_enrich(payload, candidates)

    assert len(enriched) == 2

    # Assert rank is normalized
    assert enriched[0].rank == 1
    assert enriched[0].restaurant_id == "aaa111"
    assert enriched[0].name == "North Spice Kitchen"
    assert enriched[0].cuisines == "north indian, chinese"
    assert enriched[0].rating == 4.5
    assert enriched[0].approx_cost_for_two == 800.0
    assert enriched[0].budget_band.value == "medium"
    assert enriched[0].locality == "Indiranagar"
    assert enriched[0].explanation == "Great North Indian food with highly rated dishes."

    assert enriched[1].rank == 2
    assert enriched[1].restaurant_id == "eee555"
    assert enriched[1].name == "Premium Palace"
    assert enriched[1].cuisines == "north indian, mughlai"
    assert enriched[1].rating == 4.8
    assert enriched[1].approx_cost_for_two == 950.0
    assert enriched[1].budget_band.value == "medium"
    assert enriched[1].locality == "UB City"
    assert enriched[1].explanation == "Premium Mughlai cuisine, perfect for a high rating experience."


def test_validate_and_enrich_hallucinated_id(loaded_repository) -> None:
    parser = LlmResponseParser()
    validator = RecommendationValidator()

    hallucinated_file = FIXTURES_DIR / "llm_hallucinated_id.json"
    raw_text = hallucinated_file.read_text(encoding="utf-8")
    payload = parser.parse(raw_text)

    df = loaded_repository.get_dataframe()
    candidates = loaded_repository.dataframe_to_restaurants(df)

    enriched = validator.validate_and_enrich(payload, candidates)

    # The hallucinated ID 'hallucinated_999' must be dropped, leaving exactly 2 valid ones
    assert len(enriched) == 2

    # The ranks must be normalized to sequential 1 and 2
    assert enriched[0].rank == 1
    assert enriched[0].restaurant_id == "aaa111"

    assert enriched[1].rank == 2
    assert enriched[1].restaurant_id == "eee555"


def test_validate_and_enrich_duplicate_ranks(loaded_repository) -> None:
    validator = RecommendationValidator()

    # Build payload manually with duplicate ranks: both rank 1
    payload = LlmRecommendationPayload(
        summary="Duplicates",
        recommendations=[
            LlmRecommendationItem(restaurant_id="aaa111", rank=1, explanation="First"),
            LlmRecommendationItem(restaurant_id="eee555", rank=1, explanation="Second"),
        ],
    )

    df = loaded_repository.get_dataframe()
    candidates = loaded_repository.dataframe_to_restaurants(df)

    enriched = validator.validate_and_enrich(payload, candidates)
    assert len(enriched) == 2
    # Ranks must be normalized to sequential 1 and 2
    assert enriched[0].rank == 1
    assert enriched[1].rank == 2


def test_validate_and_enrich_missing_explanation(loaded_repository) -> None:
    validator = RecommendationValidator()

    payload = LlmRecommendationPayload(
        summary="Missing explanation",
        recommendations=[
            LlmRecommendationItem(restaurant_id="aaa111", rank=1, explanation=""),
        ],
    )

    df = loaded_repository.get_dataframe()
    candidates = loaded_repository.dataframe_to_restaurants(df)

    enriched = validator.validate_and_enrich(payload, candidates)
    assert len(enriched) == 1
    assert enriched[0].explanation == "Recommended based on your preference for north indian, chinese cuisine."


def test_validate_and_enrich_duplicate_restaurant_ids(loaded_repository) -> None:
    validator = RecommendationValidator()

    payload = LlmRecommendationPayload(
        summary="Duplicate restaurant_id",
        recommendations=[
            LlmRecommendationItem(restaurant_id="aaa111", rank=1, explanation="First"),
            LlmRecommendationItem(restaurant_id="aaa111", rank=2, explanation="Second"),
        ],
    )

    df = loaded_repository.get_dataframe()
    candidates = loaded_repository.dataframe_to_restaurants(df)

    enriched = validator.validate_and_enrich(payload, candidates)
    assert len(enriched) == 1
    assert enriched[0].restaurant_id == "aaa111"
    assert enriched[0].rank == 1


def test_validate_and_enrich_duplicate_restaurant_names(loaded_repository) -> None:
    validator = RecommendationValidator()

    df = loaded_repository.get_dataframe().copy()
    import pandas as pd
    duplicate_row = pd.DataFrame([{
        "restaurant_id": "ccc999",
        "name": "North Spice Kitchen",  # Same name, different ID
        "city": "Bangalore",
        "locality": "Indiranagar",
        "cuisines": "north indian",
        "rating": 4.2,
        "votes": 100,
        "approx_cost_for_two": 600.0,
        "budget_band": "medium"
    }])
    df = pd.concat([df, duplicate_row], ignore_index=True)
    candidates = loaded_repository.dataframe_to_restaurants(df)

    payload = LlmRecommendationPayload(
        summary="Duplicate names",
        recommendations=[
            LlmRecommendationItem(restaurant_id="aaa111", rank=1, explanation="First"),
            LlmRecommendationItem(restaurant_id="ccc999", rank=2, explanation="Second"),
        ],
    )

    enriched = validator.validate_and_enrich(payload, candidates)
    assert len(enriched) == 1
    assert enriched[0].restaurant_id == "aaa111"
    assert enriched[0].rank == 1

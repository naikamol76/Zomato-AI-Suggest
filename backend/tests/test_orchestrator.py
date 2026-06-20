"""Unit tests for RecommendationOrchestrator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
import pytest

from app.config import get_settings
from app.models.preferences import UserPreferences
from app.models.restaurant import BudgetBand
from app.services.filter import CandidateFilterService
from app.services.prompt import PromptBuilder
from app.services.parser import LlmResponseParser
from app.services.validator import RecommendationValidator
from app.services.orchestrator import RecommendationOrchestrator


@pytest.fixture
def mock_groq_client() -> MagicMock:
    client = MagicMock()
    client.complete = AsyncMock()
    return client


@pytest.fixture
def orchestrator(filter_service: CandidateFilterService, mock_groq_client: MagicMock) -> RecommendationOrchestrator:
    settings = get_settings()
    prompt_builder = PromptBuilder()
    parser = LlmResponseParser()
    validator = RecommendationValidator()

    return RecommendationOrchestrator(
        filter_service=filter_service,
        prompt_builder=prompt_builder,
        groq_client=mock_groq_client,
        parser=parser,
        validator=validator,
        settings=settings,
    )


@pytest.mark.asyncio
async def test_orchestrator_happy_path(orchestrator: RecommendationOrchestrator, mock_groq_client: MagicMock) -> None:
    # Setup mock Groq response containing valid restaurant IDs 'aaa111' and 'eee555'
    mock_groq_client.complete.return_value = """
    {
      "summary": "AI suggestions.",
      "recommendations": [
        {
          "restaurant_id": "aaa111",
          "rank": 1,
          "explanation": "Best North Indian food."
        },
        {
          "restaurant_id": "eee555",
          "rank": 2,
          "explanation": "Premium ambiance and mughlai cuisine."
        }
      ]
    }
    """

    preferences = UserPreferences(
        city="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="North Indian",
        min_rating=4.0,
    )

    response = await orchestrator.get_recommendations(preferences)

    # Assertions
    assert response.message == "Recommendations generated successfully."
    assert len(response.recommendations) == 2

    rec1 = response.recommendations[0]
    assert rec1.rank == 1
    assert rec1.restaurant_id == "aaa111"
    assert rec1.name == "North Spice Kitchen"
    assert rec1.rating == 4.5

    rec2 = response.recommendations[1]
    assert rec2.rank == 2
    assert rec2.restaurant_id == "eee555"
    assert rec2.name == "Premium Palace"
    assert rec2.rating == 4.8

    assert response.meta is not None
    meta = response.meta
    # The sample restaurants in conftest matching (Bangalore, medium, North Indian, min_rating >= 4.0) are:
    # - aaa111 (rating 4.5)
    # - eee555 (rating 4.8)
    # Total candidates = 2
    assert meta.candidates_considered == 2
    assert meta.prompt_version == "v1"
    assert meta.summary == "AI suggestions."

    # Verify LLM was called
    mock_groq_client.complete.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_zero_candidates(orchestrator: RecommendationOrchestrator, mock_groq_client: MagicMock) -> None:
    preferences = UserPreferences(
        city="Zanzibar",  # Impossible city
        budget=BudgetBand.MEDIUM,
        cuisine="North Indian",
        min_rating=4.0,
    )

    response = await orchestrator.get_recommendations(preferences)

    # Assertions
    assert len(response.recommendations) == 0
    assert response.message is not None
    assert "No restaurants found matching your filters" in response.message
    assert response.meta is not None
    assert response.meta.candidates_considered == 0

    # Verify LLM was NOT called
    mock_groq_client.complete.assert_not_called()


@pytest.mark.asyncio
async def test_orchestrator_hallucinated_ids_fallback(orchestrator: RecommendationOrchestrator, mock_groq_client: MagicMock) -> None:
    # Setup mock Groq response containing only hallucinated IDs
    mock_groq_client.complete.return_value = """
    {
      "summary": "AI suggestions.",
      "recommendations": [
        {
          "restaurant_id": "hallucinated_999",
          "rank": 1,
          "explanation": "Made up restaurant."
        }
      ]
    }
    """

    preferences = UserPreferences(
        city="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="North Indian",
        min_rating=4.0,
    )

    response = await orchestrator.get_recommendations(preferences)

    # Grounding check: Since 'hallucinated_999' is invalid, it falls back to the top candidates from the datastore
    # Matches Bangalore, medium, North Indian, min_rating >= 4.0 are eee555 (4.8) and aaa111 (4.5) (total 2 matching candidates)
    assert len(response.recommendations) == 2
    assert response.recommendations[0].restaurant_id == "eee555"  # highest rating 4.8
    assert response.recommendations[1].restaurant_id == "aaa111"  # rating 4.5
    assert response.meta is not None
    assert "fallback" in response.meta.summary.lower()


@pytest.mark.asyncio
async def test_orchestrator_llm_error_fallback(orchestrator: RecommendationOrchestrator, mock_groq_client: MagicMock) -> None:
    # Setup mock to raise an exception simulating timeout or network error
    mock_groq_client.complete.side_effect = Exception("Groq connection timeout")

    preferences = UserPreferences(
        city="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="North Indian",
        min_rating=4.0,
    )

    response = await orchestrator.get_recommendations(preferences)

    # Must trigger fallback policy using candidates from store
    assert len(response.recommendations) == 2
    assert response.recommendations[0].restaurant_id == "eee555"
    assert response.recommendations[1].restaurant_id == "aaa111"
    assert response.meta is not None
    assert "We encountered a temporary issue generating AI suggestions" in response.meta.summary

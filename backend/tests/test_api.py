"""Unit tests for the recommendations API endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.models.response import RecommendResponse, ResponseMeta, Recommendation
from app.models.restaurant import BudgetBand


@pytest.mark.asyncio
async def test_recommendations_endpoint_happy_path(client: TestClient) -> None:
    # Set up mock response
    mock_response = RecommendResponse(
        recommendations=[
            Recommendation(
                rank=1,
                restaurant_id="aaa111",
                name="North Spice Kitchen",
                cuisines="north indian, chinese",
                rating=4.5,
                approx_cost_for_two=800.0,
                budget_band=BudgetBand.MEDIUM,
                locality="Indiranagar",
                explanation="Awesome place!",
            )
        ],
        message="Recommendations generated successfully.",
        meta=ResponseMeta(
            candidates_considered=1,
            prompt_version="v1",
            model="llama-3.3-70b-versatile",
            summary="AI suggestions.",
        ),
    )

    # Patch the orchestrator's get_recommendations call
    with patch(
        "app.services.orchestrator.RecommendationOrchestrator.get_recommendations",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_response

        response = client.post(
            "/api/v1/recommendations",
            json={
                "city": "Bangalore",
                "budget": "medium",
                "cuisine": "North Indian",
                "min_rating": 4.0,
                "additional_notes": "family-friendly",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Recommendations generated successfully."
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["name"] == "North Spice Kitchen"
        assert data["recommendations"][0]["rating"] == 4.5
        assert data["meta"]["candidates_considered"] == 1
        assert data["meta"]["model"] == "llama-3.3-70b-versatile"


def test_recommendations_endpoint_validation_error(client: TestClient) -> None:
    # Test invalid budget enum values (accepts only low/medium/high)
    response = client.post(
        "/api/v1/recommendations",
        json={
            "city": "Bangalore",
            "budget": "super-expensive",
            "cuisine": "North Indian",
        },
    )
    assert response.status_code == 422

    # Test invalid ratings range (0.0 to 5.0)
    response = client.post(
        "/api/v1/recommendations",
        json={
            "city": "Bangalore",
            "budget": "medium",
            "cuisine": "North Indian",
            "min_rating": 9.0,
        },
    )
    assert response.status_code == 422

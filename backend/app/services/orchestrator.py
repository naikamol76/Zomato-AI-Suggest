"""Recommendation orchestrator service."""

from __future__ import annotations

import logging
import time

from app.config import Settings
from app.models.preferences import UserPreferences
from app.models.response import RecommendResponse, ResponseMeta, Recommendation
from app.models.restaurant import Restaurant
from app.services.filter import CandidateFilterService
from app.services.prompt import PromptBuilder
from app.services.llm import GroqClient
from app.services.parser import LlmResponseParser
from app.services.validator import RecommendationValidator

logger = logging.getLogger(__name__)


class RecommendationOrchestrator:
    """Orchestrates candidate filtering, prompting, LLM execution, parsing, and factual grounding validation."""

    def __init__(
        self,
        filter_service: CandidateFilterService,
        prompt_builder: PromptBuilder,
        groq_client: GroqClient,
        parser: LlmResponseParser,
        validator: RecommendationValidator,
        settings: Settings,
    ) -> None:
        self.filter_service = filter_service
        self.prompt_builder = prompt_builder
        self.groq_client = groq_client
        self.parser = parser
        self.validator = validator
        self.settings = settings

    async def get_recommendations(self, preferences: UserPreferences) -> RecommendResponse:
        """Runs the recommendation pipeline with robust timing, logging, and error fallback policies."""
        start_time = time.perf_counter()

        # 1. Deterministic candidate filtering
        max_candidates = self.settings.max_candidates
        candidates = self.filter_service.apply(preferences, max_candidates=max_candidates)
        candidates_count = len(candidates)

        # Cost Control / PROM-01 / ORCH-01: Zero candidates -> skip LLM entirely
        if not candidates:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Orchestration finished in %.1f ms with 0 candidates for city=%s",
                duration_ms,
                preferences.city,
            )
            return RecommendResponse(
                recommendations=[],
                message=f"No restaurants found matching your filters in {preferences.city}. Try relaxing your budget or minimum rating constraints.",
                meta=ResponseMeta(
                    candidates_considered=0,
                    prompt_version="v1",
                    model=self.settings.groq_model,
                    summary="No matching restaurants available for recommendation.",
                ),
            )

        # 2. Build template prompt
        prompt_messages = self.prompt_builder.build_prompt(
            preferences=preferences,
            candidates=candidates,
            max_recommendations=self.settings.max_recommendations,
        )

        # 3. Call LLM (Groq) & Parse response
        recommendations: list[Recommendation] = []
        summary: str | None = None

        try:
            logger.info("Calling Groq completions API with %s candidates...", candidates_count)
            raw_response = await self.groq_client.complete(prompt_messages)

            # Parse LLM response
            payload = self.parser.parse(raw_response)
            summary = payload.summary

            # Validate and enrich recommendations
            recommendations = self.validator.validate_and_enrich(payload, candidates)

            # Cost Control: Limit response to max_recommendations
            recommendations = recommendations[: self.settings.max_recommendations]

            # Resilience check / VAL-03 / ORCH-02: All hallucinated IDs
            if not recommendations:
                logger.warning("All LLM recommended IDs were hallucinated! Falling back to top-3 by rating.")
                recommendations = self._fallback_top_recommendations(candidates)
                summary = "Here are the top rated matching restaurants in the city (fallback)."

        except Exception as e:
            # Resilience check / VAL-10 / ORCH-03: LLM crash or parsing failures
            logger.exception("LLM or parsing failed in recommendation flow. Triggering top-3 fallback.")
            recommendations = self._fallback_top_recommendations(candidates)
            summary = "We encountered a temporary issue generating AI suggestions. Here are the top-rated matching restaurants (fallback)."

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Orchestration finished in %.1f ms. Considered %s candidates, returned %s recommendations.",
            duration_ms,
            candidates_count,
            len(recommendations),
        )

        return RecommendResponse(
            recommendations=recommendations,
            message="Recommendations generated successfully.",
            meta=ResponseMeta(
                candidates_considered=candidates_count,
                prompt_version="v1",
                model=self.settings.groq_model,
                summary=summary,
            ),
        )

    def _fallback_top_recommendations(self, candidates: list[Restaurant]) -> list[Recommendation]:
        """Provides a simple fallback containing top 3 candidates sorted by rating/votes if LLM fails."""
        # Candidates are already sorted by rating, votes in the filter service
        top_candidates = candidates[:3]
        fallback_recs: list[Recommendation] = []
        for idx, c in enumerate(top_candidates):
            fallback_recs.append(
                Recommendation(
                    rank=idx + 1,
                    restaurant_id=c.restaurant_id,
                    name=c.name,
                    cuisines=c.cuisines,
                    rating=c.rating,
                    approx_cost_for_two=c.approx_cost_for_two,
                    budget_band=c.budget_band,
                    locality=c.locality,
                    explanation=f"Top-rated {c.cuisines} restaurant in {c.locality} (automatic system recommendation).",
                )
            )
        return fallback_recs

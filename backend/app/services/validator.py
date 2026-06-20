"""Factual grounding and enrichment validator for LLM recommendations."""

from __future__ import annotations

from app.models.response import LlmRecommendationPayload, Recommendation
from app.models.restaurant import Restaurant


class RecommendationValidator:
    """Validates and enriches LLM recommendations against data store candidates."""

    def validate_and_enrich(
        self,
        payload: LlmRecommendationPayload,
        candidates: list[Restaurant],
    ) -> list[Recommendation]:
        """Filters hallucinated IDs, enriches facts from store, and normalizes ranks."""
        # Map candidates by ID for O(1) grounding checks
        candidate_map = {c.restaurant_id: c for c in candidates}

        enriched: list[Recommendation] = []
        seen_ids: set[str] = set()
        seen_names: set[str] = set()

        for item in payload.recommendations:
            rest_id = str(item.restaurant_id).strip()

            # Grounding check: Skip invalid or hallucinated IDs
            if rest_id not in candidate_map:
                continue

            # De-duplicate to prevent LLM from recommending same venue twice
            if rest_id in seen_ids:
                continue

            restaurant = candidate_map[rest_id]
            name_norm = restaurant.name.strip().casefold()
            if name_norm in seen_names:
                continue

            seen_ids.add(rest_id)
            seen_names.add(name_norm)

            explanation = (item.explanation or "").strip()
            if not explanation:
                explanation = f"Recommended based on your preference for {restaurant.cuisines} cuisine."

            enriched.append(
                Recommendation(
                    rank=item.rank,
                    restaurant_id=restaurant.restaurant_id,
                    name=restaurant.name,
                    cuisines=restaurant.cuisines,
                    rating=restaurant.rating,
                    approx_cost_for_two=restaurant.approx_cost_for_two,
                    budget_band=restaurant.budget_band,
                    locality=restaurant.locality,
                    explanation=explanation,
                )
            )

        # Sort based on the LLM's suggested rank (fallback to large rank for invalid ones)
        enriched.sort(key=lambda r: r.rank if r.rank >= 1 else 9999)

        # Normalize ranks sequentially: 1, 2, 3...
        for idx, rec in enumerate(enriched):
            # Mutate rank to be normalized sequential
            # Recommendation model is mutable so this is safe and clean
            rec.rank = idx + 1

        return enriched

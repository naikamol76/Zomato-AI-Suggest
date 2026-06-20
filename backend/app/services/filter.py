"""Deterministic candidate filtering before LLM ranking."""

from __future__ import annotations

import logging

import pandas as pd

from app.data.repository import RestaurantRepository
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class CandidateFilterService:
    """Apply hard constraints and return a capped, rating-sorted shortlist."""

    def __init__(self, repository: RestaurantRepository) -> None:
        self._repository = repository

    def apply(
        self,
        preferences: UserPreferences,
        max_candidates: int,
    ) -> list[Restaurant]:
        if max_candidates < 1:
            return []

        df = self._repository.get_dataframe()
        filtered = self._filter_dataframe(df, preferences)

        if filtered.empty:
            logger.info(
                "No candidates for city=%s cuisine=%s budget=%s min_rating=%s",
                preferences.city,
                preferences.cuisine,
                preferences.budget.value,
                preferences.min_rating,
            )
            return []

        sorted_df = filtered.sort_values(
            by=["rating", "votes"],
            ascending=[False, False],
            kind="mergesort",
        )
        
        # De-duplicate by name case-insensitively, keeping the highest-rated first match
        sorted_df["name_lower"] = sorted_df["name"].astype(str).str.strip().str.casefold()
        deduped_df = sorted_df.drop_duplicates(subset=["name_lower"], keep="first")
        deduped_df = deduped_df.drop(columns=["name_lower"])
        final_df = deduped_df.head(max_candidates)

        results = self._repository.dataframe_to_restaurants(final_df)
        logger.info(
            "Filtered %s candidates (max %s) for city=%s",
            len(results),
            max_candidates,
            preferences.city,
        )
        return results

    @staticmethod
    def _filter_dataframe(df: pd.DataFrame, preferences: UserPreferences) -> pd.DataFrame:
        city_norm = preferences.city.casefold()
        cuisine_norm = preferences.cuisine.casefold()
        budget_norm = preferences.budget.value

        city_match = df["city"].astype(str).str.strip().str.casefold() == city_norm
        rating_match = df["rating"] >= preferences.min_rating
        budget_match = df["budget_band"].astype(str).str.strip().str.casefold() == budget_norm
        cuisine_match = (
            df["cuisines"]
            .fillna("")
            .astype(str)
            .str.casefold()
            .str.contains(cuisine_norm, regex=False)
        )

        mask = city_match & rating_match & budget_match & cuisine_match
        return df[mask].copy()

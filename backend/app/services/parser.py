"""Parser for LLM JSON responses."""

from __future__ import annotations

import json
import re

from app.models.response import LlmRecommendationPayload


class LlmResponseParser:
    """Parses raw text responses from the LLM, stripping markdown and validating structure."""

    def parse(self, raw_text: str) -> LlmRecommendationPayload:
        """Parses and validates a raw text response as an LlmRecommendationPayload."""
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty response received from the LLM.")

        clean_text = raw_text.strip()

        # Strip markdown fences if present (e.g. ```json ... ``` or ``` ... ```)
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
        if fence_match:
            clean_text = fence_match.group(1).strip()

        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("LLM response is not a JSON object.")

        # Provide resilience for missing/incorrect field types
        if "recommendations" not in data:
            data["recommendations"] = []
        elif not isinstance(data["recommendations"], list):
            raise ValueError("The 'recommendations' field in LLM response must be a list.")

        return LlmRecommendationPayload.model_validate(data)

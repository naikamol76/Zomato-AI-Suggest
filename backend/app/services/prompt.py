"""Jinja2 prompt template builder for LLM recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant


class PromptBuilder:
    """Loads and renders recommendation prompts using Jinja2."""

    def __init__(self, template_dir: Path | str | None = None) -> None:
        if template_dir is None:
            # Dynamically locate the prompts directory
            services_dir = Path(__file__).resolve().parent
            root_prompts = services_dir.parents[2] / "prompts"
            backend_prompts = services_dir.parents[1] / "prompts"

            if root_prompts.exists() and (root_prompts / "recommend_v1.jinja2").exists():
                self._template_dir = root_prompts
            elif backend_prompts.exists() and (backend_prompts / "recommend_v1.jinja2").exists():
                self._template_dir = backend_prompts
            else:
                self._template_dir = Path("prompts").resolve()
        else:
            self._template_dir = Path(template_dir)

        if not (self._template_dir / "recommend_v1.jinja2").exists():
            raise FileNotFoundError(
                f"Required prompt template 'recommend_v1.jinja2' not found in: {self._template_dir}"
            )

        self._env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            autoescape=False,
        )
        self._template_name = "recommend_v1.jinja2"

    def build_prompt(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        max_recommendations: int,
    ) -> list[dict[str, str]]:
        """Renders system and user messages containing preferences and candidates."""
        preferences_json = preferences.model_dump_json(exclude_none=True, indent=2)

        candidates_data = [
            {
                "restaurant_id": c.restaurant_id,
                "name": c.name,
                "cuisines": c.cuisines,
                "rating": c.rating,
                "votes": c.votes,
                "approx_cost_for_two": c.approx_cost_for_two,
                "budget_band": c.budget_band.value if hasattr(c.budget_band, "value") else c.budget_band,
                "locality": c.locality,
            }
            for c in candidates
        ]
        candidates_json = json.dumps(candidates_data, indent=2)

        template = self._env.get_template(self._template_name)
        rendered_user_msg = template.render(
            preferences_json=preferences_json,
            candidates_json=candidates_json,
            max_recommendations=max_recommendations,
        )

        system_msg = (
            "You are an expert restaurant recommender system.\n"
            "Your task is to rank and recommend restaurants strictly from the provided candidate list.\n"
            "You must return a valid JSON object matching the requested schema and rules.\n"
            "Do not invent any restaurant IDs or make up venues not present in the candidate list."
        )

        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": rendered_user_msg},
        ]

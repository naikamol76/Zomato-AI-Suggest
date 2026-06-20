"""FastAPI Dependency Injection helpers."""

from __future__ import annotations

from functools import lru_cache
from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.data.repository import RestaurantRepository
from app.services.filter import CandidateFilterService
from app.services.prompt import PromptBuilder
from app.services.llm import GroqLlmClient
from app.services.parser import LlmResponseParser
from app.services.validator import RecommendationValidator
from app.services.orchestrator import RecommendationOrchestrator


@lru_cache
def get_repository_singleton(data_path: str) -> RestaurantRepository:
    return RestaurantRepository(data_path=data_path)


def get_repository(request: Request) -> RestaurantRepository:
    repo: RestaurantRepository | None = getattr(request.app.state, "repository", None)
    if repo is None or not repo.is_loaded:
        raise RuntimeError("Restaurant repository is not initialized.")
    return repo


def init_repository(settings: Settings) -> RestaurantRepository:
    get_repository_singleton.cache_clear()
    repo = get_repository_singleton(settings.data_path)
    repo.load()
    return repo


def get_filter_service(request: Request) -> CandidateFilterService:
    return CandidateFilterService(get_repository(request))


def get_orchestrator(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> RecommendationOrchestrator:
    """Dependency resolver for RecommendationOrchestrator."""
    filter_service = get_filter_service(request)
    prompt_builder = PromptBuilder()
    groq_client = GroqLlmClient(settings)
    parser = LlmResponseParser()
    validator = RecommendationValidator()

    return RecommendationOrchestrator(
        filter_service=filter_service,
        prompt_builder=prompt_builder,
        groq_client=groq_client,
        parser=parser,
        validator=validator,
        settings=settings,
    )

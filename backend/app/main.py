import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.config import get_settings
from app.deps import init_repository

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Starting restaurant recommendation API v%s", __version__)

    repository = init_repository(settings)
    app.state.repository = repository

    yield

    logger.info("Shutting down API")


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title="Restaurant Recommendation API",
        description="Zomato-inspired hybrid filter + LLM recommendations",
        version=__version__,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api/v1")

    return application


app = create_app()

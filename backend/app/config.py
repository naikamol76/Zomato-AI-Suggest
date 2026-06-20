from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY", "LLM_API_KEY"),
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices("GROQ_MODEL", "LLM_MODEL"),
    )
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        validation_alias=AliasChoices("GROQ_BASE_URL", "LLM_BASE_URL"),
    )
    groq_timeout: float = Field(
        default=60.0,
        validation_alias=AliasChoices("GROQ_TIMEOUT", "LLM_TIMEOUT"),
    )
    groq_max_retries: int = Field(
        default=2,
        validation_alias=AliasChoices("GROQ_MAX_RETRIES", "LLM_MAX_RETRIES"),
    )

    data_path: str = Field(
        default="../data/processed/restaurants.parquet",
        alias="DATA_PATH",
    )
    max_candidates: int = Field(default=20, alias="MAX_CANDIDATES")
    max_recommendations: int = Field(default=5, alias="MAX_RECOMMENDATIONS")

    cors_origins: str | list[str] = Field(
        default=["http://localhost:5173"],
        alias="CORS_ORIGINS",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

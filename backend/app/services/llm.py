"""Groq client service using Groq API adapter."""

from __future__ import annotations

import logging
from typing import Protocol

import groq
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception

from app.config import Settings

logger = logging.getLogger(__name__)


class GroqClient(Protocol):
    """Protocol defining the interface for Groq clients."""

    async def complete(self, messages: list[dict[str, str]]) -> str:
        """Asynchronously call chat completion."""
        ...


def is_retryable_groq_exception(exception: BaseException) -> bool:
    """Helper to check if a groq exception is retryable (429 or 5xx)."""
    if isinstance(exception, groq.RateLimitError):
        logger.warning("Groq API rate limit hit (429). Retrying...")
        return True
    if isinstance(exception, groq.APITimeoutError):
        logger.warning("Groq API timeout. Retrying...")
        return True
    if isinstance(exception, groq.APIStatusError):
        if exception.status_code >= 500:
            logger.warning("Groq API server error (%s). Retrying...", exception.status_code)
            return True
    return False


class GroqLlmClient:
    """Async client wrapper for Groq API with built-in tenacity retries."""

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.base_url = settings.groq_base_url
        self.timeout = settings.groq_timeout
        self.max_retries = settings.groq_max_retries

        if not self.api_key:
            logger.warning("GROQ_API_KEY is empty. Calls to Groq API will fail unless mocked.")
            self.client = None
        else:
            if self.base_url and self.base_url != "https://api.groq.com/openai/v1":
                self.client = groq.AsyncGroq(api_key=self.api_key, base_url=self.base_url)
            else:
                self.client = groq.AsyncGroq(api_key=self.api_key)

    async def complete(self, messages: list[dict[str, str]]) -> str:
        """Call Chat Completions on Groq API with retries and timeout."""
        if not self.client:
            raise ValueError(
                "Groq client is not initialized because GROQ_API_KEY is not set."
            )

        @retry(
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_random_exponential(min=1, max=10),
            retry=retry_if_exception(is_retryable_groq_exception),
            reraise=True,
        )
        async def _call_api() -> str:
            response_format = None
            model_lower = self.model.lower()
            if "llama" in model_lower or "mixtral" in model_lower or "gemma" in model_lower:
                response_format = {"type": "json_object"}

            chat_completion = await self.client.chat.completions.create(
                messages=messages,  # type: ignore
                model=self.model,
                response_format=response_format,  # type: ignore
                timeout=self.timeout,
            )
            content = chat_completion.choices[0].message.content
            if content is None:
                raise ValueError("Groq API returned an empty response content.")
            return content

        return await _call_api()

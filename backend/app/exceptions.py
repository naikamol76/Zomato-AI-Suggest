class LlmError(Exception):
    """Raised when the LLM provider call fails."""


class LlmConfigurationError(LlmError):
    """Raised when LLM is not configured (e.g. missing API key)."""


class LlmParseError(Exception):
    """Raised when LLM output cannot be parsed as expected JSON."""

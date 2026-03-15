"""LLM client factory."""

from __future__ import annotations

from findocparser.llm.base import LLMClient


def get_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """Create an LLM client for the given provider.

    Args:
        provider: LLM provider name. Supported: "openai", "deepseek", "gemini".
        **kwargs: Additional provider-specific configuration.

    Returns:
        An LLM client instance.
    """
    if provider in ("openai", "deepseek"):
        from findocparser.llm.openai_client import OpenAIClient

        return OpenAIClient(provider=provider, **kwargs)
    raise ValueError(
        f"Unknown LLM provider: {provider}. "
        f"Supported: openai, deepseek"
    )

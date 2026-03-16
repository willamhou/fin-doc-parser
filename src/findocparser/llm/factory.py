"""LLM client factory."""

from __future__ import annotations

from findocparser.llm.base import LLMClient


def get_llm_client(provider: str = "deepseek", **kwargs) -> LLMClient:
    """Create an LLM client for the given provider.

    Args:
        provider: LLM provider name. Supported: "deepseek", "openai".
        **kwargs: Passed to the client constructor (``api_key``,
            ``base_url``, ``model``).

    Returns:
        An LLM client instance.
    """
    if provider in ("openai", "deepseek"):
        from findocparser.llm.openai_client import OpenAIClient

        return OpenAIClient(provider=provider, **kwargs)
    raise ValueError(f"Unknown LLM provider: {provider}. Supported: deepseek, openai")

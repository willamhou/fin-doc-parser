"""LLM client protocol."""

from __future__ import annotations

from typing import Any, Protocol


class LLMClient(Protocol):
    """Protocol for LLM clients."""

    async def extract_json(self, prompt: str) -> dict[str, Any]:
        """Send a prompt and return parsed JSON response."""
        ...

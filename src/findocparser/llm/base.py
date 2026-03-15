"""LLM client protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM clients.

    Any class with an ``extract_json(prompt) -> dict`` async method
    satisfies this protocol.  Users can bring their own LLM client
    without inheriting from any base class.
    """

    async def extract_json(self, prompt: str) -> dict[str, Any]:
        """Send a prompt and return parsed JSON response."""
        ...

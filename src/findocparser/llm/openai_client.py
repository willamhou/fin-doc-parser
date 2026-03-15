"""OpenAI-compatible LLM client (works with OpenAI, DeepSeek, etc.)."""

from __future__ import annotations

import json
import os
import re
from typing import Any


_PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
}


class OpenAIClient:
    """OpenAI-compatible client for structured JSON extraction."""

    def __init__(
        self,
        provider: str = "openai",
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        defaults = _PROVIDER_DEFAULTS.get(provider, _PROVIDER_DEFAULTS["openai"])

        self.base_url = base_url or defaults["base_url"]
        self.model = model or defaults["model"]

        resolved_key = api_key or os.environ.get(defaults["api_key_env"], "")
        if not resolved_key:
            raise ValueError(
                f"API key not found. Set {defaults['api_key_env']} environment variable "
                f"or pass api_key parameter."
            )
        self.api_key = resolved_key

    async def extract_json(self, prompt: str) -> dict[str, Any]:
        """Send prompt and parse JSON from response."""
        import httpx

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial document parser. Always respond with valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse_json(content)

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        """Extract JSON from LLM response text."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding first { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {"raw_response": text, "parse_error": "Failed to extract JSON"}

"""OpenAI-compatible LLM client (works with OpenAI, DeepSeek, etc.)."""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

import httpx

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
        max_retries: int = 3,
        http_client: httpx.AsyncClient | None = None,
    ):
        defaults = _PROVIDER_DEFAULTS.get(provider, _PROVIDER_DEFAULTS["openai"])

        self.base_url = base_url or defaults["base_url"]
        self.model = model or defaults["model"]
        self.max_retries = max_retries
        self._http_client = http_client

        resolved_key = api_key or os.environ.get(defaults["api_key_env"], "")
        if not resolved_key:
            raise ValueError(
                f"API key not found. Set {defaults['api_key_env']} environment variable "
                f"or pass api_key parameter."
            )
        self._api_key = resolved_key

    def __repr__(self) -> str:
        return f"OpenAIClient(base_url={self.base_url!r}, model={self.model!r})"

    async def extract_json(self, prompt: str) -> dict[str, Any]:
        """Send prompt and parse JSON from response, with retry on transient errors."""
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                return await self._call_api(prompt)
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code in (429, 500, 502, 503):
                    await asyncio.sleep(2**attempt)
                    continue
                raise
            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                last_exc = exc
                await asyncio.sleep(2**attempt)
                continue

        raise RuntimeError(f"LLM API call failed after {self.max_retries} retries") from last_exc

    async def _call_api(self, prompt: str) -> dict[str, Any]:
        """Single API call."""
        if self._http_client is not None:
            resp = await self._post(self._http_client, prompt)
        else:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await self._post(client, prompt)

        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse_json(content)

    async def _post(self, client: httpx.AsyncClient, prompt: str) -> httpx.Response:
        return await client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a financial document parser. "
                            "Always respond with valid JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 4096,
            },
        )

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

        # Try finding first balanced { ... } block
        result = _find_json_object(text)
        if result is not None:
            return result

        return {"raw_response": text, "parse_error": "Failed to extract JSON"}


def _find_json_object(text: str) -> dict[str, Any] | None:
    """Find the first balanced JSON object in text using brace counting."""
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None

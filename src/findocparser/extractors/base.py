"""Base extractor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from findocparser.llm.base import LLMClient

# ~12k tokens for most models — prevents token limit overflows and cost spikes.
MAX_CONTENT_CHARS = 50_000


class BaseExtractor(ABC):
    """Base class for document extractors."""

    @property
    @abstractmethod
    def doc_type(self) -> str:
        """Document type this extractor handles."""

    @property
    @abstractmethod
    def prompt_template(self) -> str:
        """Prompt template for LLM extraction."""

    async def extract(
        self,
        content: str,
        llm_client: LLMClient,
        *,
        max_content_chars: int = MAX_CONTENT_CHARS,
    ) -> dict[str, Any]:
        """Extract structured data from document content.

        Args:
            content: Raw text content (from OCR or Excel parser).
            llm_client: LLM client for structured extraction.
            max_content_chars: Truncate content beyond this length.

        Returns:
            Extracted structured data.
        """
        truncated = content[:max_content_chars]
        if len(content) > max_content_chars:
            truncated += "\n\n[... content truncated ...]"
        prompt = self.prompt_template.format(content=truncated)
        return await llm_client.extract_json(prompt)

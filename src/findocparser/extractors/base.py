"""Base extractor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from findocparser.llm.base import LLMClient


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

    async def extract(self, content: str, llm_client: LLMClient) -> dict[str, Any]:
        """Extract structured data from document content.

        Args:
            content: Raw text content (from OCR or Excel parser).
            llm_client: LLM client for structured extraction.

        Returns:
            Extracted structured data.
        """
        prompt = self.prompt_template.format(content=content)
        return await llm_client.extract_json(prompt)

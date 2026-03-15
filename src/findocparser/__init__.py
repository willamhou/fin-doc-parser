"""fin-doc-parser: AI-powered financial document parsing SDK."""

__version__ = "0.1.0"

from findocparser.api import parse, parse_async
from findocparser.compare import compare_periods
from findocparser.llm.base import LLMClient
from findocparser.llm.openai_client import OpenAIClient

__all__ = ["LLMClient", "OpenAIClient", "compare_periods", "parse", "parse_async"]

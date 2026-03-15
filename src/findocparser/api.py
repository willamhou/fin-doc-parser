"""Public API — the main entry points for fin-doc-parser."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from findocparser.llm.base import LLMClient


def parse(
    file_path: str | Path,
    *,
    doc_type: str | None = None,
    llm_provider: str = "deepseek",
    llm_client: LLMClient | None = None,
    llm_base_url: str | None = None,
    llm_api_key: str | None = None,
    llm_model: str | None = None,
    ocr_backend: str = "auto",
) -> dict[str, Any]:
    """Parse a financial document and return structured data.

    Args:
        file_path: Path to the document (PDF, image, or Excel file).
        doc_type: Document type hint. If None, auto-detect.
        llm_provider: LLM provider name. Default "deepseek".
            Supported: "deepseek", "openai".
        llm_client: Pre-configured LLM client instance. If provided,
            ``llm_provider`` / ``llm_base_url`` / ``llm_api_key`` / ``llm_model``
            are ignored.
        llm_base_url: Override the default base URL for the provider.
        llm_api_key: Override the API key (otherwise read from env).
        llm_model: Override the default model name.
        ocr_backend: OCR backend. "auto" (default), "paddleocr",
            "prismer", or "none".

    Returns:
        Structured extraction result as a dict.
    """
    import asyncio

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass  # No running loop — safe to call asyncio.run()
    else:
        raise RuntimeError(
            "parse() cannot be called from an async context (e.g. Jupyter, FastAPI). "
            "Use 'await parse_async(...)' instead."
        )

    return asyncio.run(
        parse_async(
            file_path,
            doc_type=doc_type,
            llm_provider=llm_provider,
            llm_client=llm_client,
            llm_base_url=llm_base_url,
            llm_api_key=llm_api_key,
            llm_model=llm_model,
            ocr_backend=ocr_backend,
        )
    )


async def parse_async(
    file_path: str | Path,
    *,
    doc_type: str | None = None,
    llm_provider: str = "deepseek",
    llm_client: LLMClient | None = None,
    llm_base_url: str | None = None,
    llm_api_key: str | None = None,
    llm_model: str | None = None,
    ocr_backend: str = "auto",
) -> dict[str, Any]:
    """Async version of :func:`parse`. See :func:`parse` for documentation."""
    from findocparser.pipeline import run_pipeline

    return await run_pipeline(
        file_path=Path(file_path),
        doc_type=doc_type,
        llm_provider=llm_provider,
        llm_client=llm_client,
        llm_base_url=llm_base_url,
        llm_api_key=llm_api_key,
        llm_model=llm_model,
        ocr_backend=ocr_backend,
    )

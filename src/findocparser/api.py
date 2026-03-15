"""Public API — the main entry points for fin-doc-parser."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def parse(
    file_path: str | Path,
    *,
    doc_type: str | None = None,
    llm_provider: str = "openai",
    ocr_backend: str = "auto",
) -> dict[str, Any]:
    """Parse a financial document and return structured data.

    Args:
        file_path: Path to the document (PDF, image, or Excel file).
        doc_type: Document type hint. If None, auto-detect.
            Supported: financial_statement, bank_statement, business_license,
            credit_report, tax_invoice, fixed_asset, lease_contract,
            shareholder_info, property_cert.
        llm_provider: LLM provider for extraction. Default "openai".
        ocr_backend: OCR backend. "auto" (default), "paddleocr", "prismer", or "none".

    Returns:
        Structured extraction result as a dict.
    """
    import asyncio

    return asyncio.run(
        parse_async(
            file_path,
            doc_type=doc_type,
            llm_provider=llm_provider,
            ocr_backend=ocr_backend,
        )
    )


async def parse_async(
    file_path: str | Path,
    *,
    doc_type: str | None = None,
    llm_provider: str = "openai",
    ocr_backend: str = "auto",
) -> dict[str, Any]:
    """Async version of parse(). See parse() for documentation."""
    from findocparser.pipeline import run_pipeline

    return await run_pipeline(
        file_path=Path(file_path),
        doc_type=doc_type,
        llm_provider=llm_provider,
        ocr_backend=ocr_backend,
    )

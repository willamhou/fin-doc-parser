"""Core pipeline: detect → parse → extract → return structured data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from findocparser.detect import detect_doc_type, detect_file_type


async def run_pipeline(
    file_path: Path,
    doc_type: str | None,
    llm_provider: str,
    ocr_backend: str,
) -> dict[str, Any]:
    """Run the full parsing pipeline.

    Steps:
        1. Detect file type (pdf/image/excel)
        2. Parse content (OCR or Excel parser)
        3. Detect document type (if not provided)
        4. Extract structured data via LLM
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Step 1: Detect file type
    file_type = detect_file_type(file_path)

    # Step 2: Parse raw content
    if file_type == "excel":
        from findocparser.parsers.excel import parse_excel

        raw_content = parse_excel(file_path)
    else:
        from findocparser.parsers.ocr import parse_ocr

        raw_content = await parse_ocr(file_path, backend=ocr_backend)

    # Step 3: Detect document type if not provided
    if doc_type is None:
        doc_type = detect_doc_type(raw_content, file_path.name)

    # Step 4: Extract structured data
    from findocparser.extractors.registry import get_extractor

    extractor = get_extractor(doc_type)

    from findocparser.llm.factory import get_llm_client

    llm_client = get_llm_client(llm_provider)

    result = await extractor.extract(raw_content, llm_client)

    return {
        "doc_type": doc_type,
        "file_name": file_path.name,
        "file_type": file_type,
        "data": result,
    }

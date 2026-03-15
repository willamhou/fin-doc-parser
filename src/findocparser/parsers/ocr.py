"""OCR parser — pluggable backend for PDF and image files."""

from __future__ import annotations

from pathlib import Path


async def parse_ocr(file_path: Path, *, backend: str = "auto") -> str:
    """Parse a PDF or image file using OCR.

    Args:
        file_path: Path to PDF or image.
        backend: OCR backend to use.
            "auto" — try text extraction first, fall back to OCR.
            "paddleocr" — use PaddleOCR (local, no external service).
            "prismer" — use Prismer OCR service (requires PRISMER_OCR_BASE_URL).
            "none" — text-only extraction (no OCR, PDF only).

    Returns:
        Extracted text content.
    """
    if backend == "auto":
        return await _auto_parse(file_path)
    if backend == "paddleocr":
        return await _paddleocr_parse(file_path)
    if backend == "prismer":
        return await _prismer_parse(file_path)
    if backend == "none":
        return _text_extract(file_path)
    raise ValueError(f"Unknown OCR backend: {backend}")


async def _auto_parse(file_path: Path) -> str:
    """Auto: try text extraction first, fall back to PaddleOCR."""
    if file_path.suffix.lower() == ".pdf":
        text = _text_extract(file_path)
        if text.strip() and len(text.strip()) > 100:
            return text

    return await _paddleocr_parse(file_path)


def _text_extract(file_path: Path) -> str:
    """Extract text from PDF using PyMuPDF (no OCR)."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(file_path))
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n\n".join(pages)
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for text extraction. "
            "Install with: pip install pymupdf"
        )


async def _paddleocr_parse(file_path: Path) -> str:
    """Parse using PaddleOCR (local)."""
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        raise ImportError(
            "PaddleOCR is required. "
            "Install with: pip install 'fin-doc-parser[ocr]'"
        )

    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    result = ocr.ocr(str(file_path), cls=True)

    lines: list[str] = []
    if result:
        for page in result:
            if page:
                for line in page:
                    text = line[1][0] if line[1] else ""
                    if text:
                        lines.append(text)

    return "\n".join(lines)


async def _prismer_parse(file_path: Path) -> str:
    """Parse using Prismer OCR service (external)."""
    import os

    base_url = os.environ.get("PRISMER_OCR_BASE_URL")
    if not base_url:
        raise ValueError(
            "PRISMER_OCR_BASE_URL environment variable is required "
            "for Prismer OCR backend."
        )

    import asyncio

    import httpx

    async with httpx.AsyncClient(base_url=base_url, timeout=120) as client:
        # Submit task
        with open(file_path, "rb") as f:
            resp = await client.post(
                "/parse",
                files={"file": (file_path.name, f)},
                data={"mode": "auto", "output": "markdown"},
            )
        resp.raise_for_status()
        task_id = resp.json().get("task_id")

        # Poll for completion
        for _ in range(60):
            status_resp = await client.get(f"/parse/{task_id}")
            status_resp.raise_for_status()
            status_data = status_resp.json()
            if status_data.get("status") == "completed":
                result_resp = await client.get(f"/parse/{task_id}/result")
                result_resp.raise_for_status()
                return result_resp.json().get("markdown_content", "")
            if status_data.get("status") == "failed":
                raise RuntimeError(f"OCR failed: {status_data}")
            await asyncio.sleep(2)

        raise TimeoutError("OCR task timed out after 120 seconds")

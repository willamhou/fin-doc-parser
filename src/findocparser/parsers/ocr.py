"""OCR parser — pluggable backend for PDF and image files."""

from __future__ import annotations

import asyncio
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
        return await asyncio.to_thread(_text_extract, file_path)
    raise ValueError(f"Unknown OCR backend: {backend}")


async def _auto_parse(file_path: Path) -> str:
    """Auto: try text extraction first, fall back to PaddleOCR."""
    if file_path.suffix.lower() == ".pdf":
        text = await asyncio.to_thread(_text_extract, file_path)
        if text.strip() and len(text.strip()) > 100:
            return text

    return await _paddleocr_parse(file_path)


def _text_extract(file_path: Path) -> str:
    """Extract text from PDF using PyMuPDF (no OCR). Blocking — call via to_thread."""
    try:
        import fitz  # PyMuPDF
    except ImportError as err:
        raise ImportError(
            "PyMuPDF is required for PDF text extraction. "
            "Install with: pip install 'fin-doc-parser[pdf]'"
        ) from err

    doc = fitz.open(str(file_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# PaddleOCR — cached singleton to avoid reloading the model each call
# ---------------------------------------------------------------------------

_paddleocr_instance = None


def _get_paddleocr():
    """Lazy singleton for PaddleOCR engine."""
    global _paddleocr_instance
    if _paddleocr_instance is None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as err:
            raise ImportError(
                "PaddleOCR is required. Install with: pip install 'fin-doc-parser[ocr]'"
            ) from err
        _paddleocr_instance = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    return _paddleocr_instance


def _paddleocr_sync(file_path: Path) -> str:
    """Run PaddleOCR synchronously. Blocking — call via to_thread."""
    ocr = _get_paddleocr()
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


async def _paddleocr_parse(file_path: Path) -> str:
    """Parse using PaddleOCR (local). Runs in a thread to avoid blocking the loop."""
    return await asyncio.to_thread(_paddleocr_sync, file_path)


# ---------------------------------------------------------------------------
# Prismer OCR service
# ---------------------------------------------------------------------------


async def _prismer_parse(file_path: Path) -> str:
    """Parse using Prismer OCR service (external)."""
    import os

    base_url = os.environ.get("PRISMER_OCR_BASE_URL")
    if not base_url:
        raise ValueError(
            "PRISMER_OCR_BASE_URL environment variable is required for Prismer OCR backend."
        )

    import httpx

    # Read file bytes in a thread to avoid blocking the event loop
    file_bytes = await asyncio.to_thread(file_path.read_bytes)

    async with httpx.AsyncClient(base_url=base_url, timeout=120) as client:
        resp = await client.post(
            "/parse",
            files={"file": (file_path.name, file_bytes)},
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

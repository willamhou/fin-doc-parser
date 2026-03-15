"""File type and document type detection."""

from __future__ import annotations

from pathlib import Path

# File extension → file type mapping
_EXCEL_EXTENSIONS = {".xlsx", ".xls", ".csv"}
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
_PDF_EXTENSIONS = {".pdf"}

# Filename keyword → document type mapping
_FILENAME_HINTS: list[tuple[list[str], str]] = [
    (["资产负债", "利润表", "现金流", "财务报表", "balance", "income", "cash_flow"], "financial_statement"),
    (["银行流水", "bank_statement", "bank_flow"], "bank_statement"),
    (["营业执照", "business_license"], "business_license"),
    (["征信", "credit_report"], "credit_report"),
    (["发票", "invoice"], "tax_invoice"),
    (["固定资产", "fixed_asset"], "fixed_asset"),
    (["租赁", "lease"], "lease_contract"),
    (["股东", "shareholder"], "shareholder_info"),
    (["房产证", "property"], "property_cert"),
    (["土地证", "land_cert"], "land_cert"),
]


def detect_file_type(file_path: Path) -> str:
    """Detect file type from extension.

    Returns:
        "pdf", "image", or "excel".
    """
    ext = file_path.suffix.lower()
    if ext in _EXCEL_EXTENSIONS:
        return "excel"
    if ext in _IMAGE_EXTENSIONS:
        return "image"
    if ext in _PDF_EXTENSIONS:
        return "pdf"
    raise ValueError(f"Unsupported file type: {ext}")


def detect_doc_type(content: str, filename: str = "") -> str:
    """Auto-detect document type from content and filename.

    Returns:
        Document type string, or "generic" if unknown.
    """
    filename_lower = filename.lower()

    # Check filename hints first
    for keywords, doc_type in _FILENAME_HINTS:
        if any(kw in filename_lower for kw in keywords):
            return doc_type

    # Check content hints
    content_sample = content[:2000].lower()
    for keywords, doc_type in _FILENAME_HINTS:
        if any(kw in content_sample for kw in keywords):
            return doc_type

    return "generic"

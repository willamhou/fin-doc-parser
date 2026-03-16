# Changelog

## 0.1.0 (2026-03-16)

Initial release.

### Features

- **10 document type extractors**: financial_statement, bank_statement, business_license, audit_report, credit_report, shareholder_info, financial_notes, md_and_a, guarantee, equity_changes_stmt
- **Generic fallback** for unknown document types
- **Pluggable OCR**: PaddleOCR (local), Prismer (GPU service), PyMuPDF (text-only)
- **Pluggable LLM**: DeepSeek, OpenAI, or any OpenAI-compatible API
- **Bring your own client**: pass a pre-configured `LLMClient` instance
- **Excel support**: xlsx, xls, csv with automatic markdown conversion
- **Auto-detection**: file type and document type from filename and content
- **Multi-period comparison**: `compare_periods()` with significant change detection
- **Async-first**: `parse_async()` for high-throughput pipelines

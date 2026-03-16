# Contributing to fin-doc-parser

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Clone & Install

```bash
git clone https://github.com/willamhou/fin-doc-parser.git
cd fin-doc-parser

# Install with dev dependencies
pip install -e ".[dev]"

# Or with all optional features
pip install -e ".[all,dev]"
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `DEEPSEEK_API_KEY` | One of these required | DeepSeek API key (recommended for Chinese docs) |
| `OPENAI_API_KEY` | | OpenAI API key (alternative) |
| `PRISMER_OCR_BASE_URL` | No | Prismer OCR service URL (only for `ocr_backend="prismer"`) |

## Development Workflow

### Project Structure

```
src/findocparser/
  __init__.py          # Public exports: parse, parse_async, compare_periods, OpenAIClient
  api.py               # Public entry points: parse(), parse_async()
  pipeline.py          # Core pipeline orchestration
  detect.py            # File type & document type detection
  compare.py           # Multi-period comparison
  extractors/          # Document-type-specific extractors
    base.py            # BaseExtractor abstract class
    registry.py        # Extractor registry (lazy loading)
    generic.py         # Fallback extractor for unknown types
    financial_statement.py
    bank_statement.py
    business_license.py
    audit_report.py
    credit_report.py
    shareholder_info.py
    financial_notes.py
    md_and_a.py
    guarantee.py
    equity_changes_stmt.py
  llm/                 # LLM provider abstraction
    base.py            # LLMClient protocol
    openai_client.py   # OpenAI-compatible implementation
    factory.py         # Provider factory
  parsers/             # Content parsers
    ocr.py             # OCR backends (PaddleOCR, Prismer, PyMuPDF)
    excel.py           # Excel/CSV parser
```

### Extractor Status

| doc_type | Dedicated Extractor | Status |
|---|---|---|
| `financial_statement` | Yes | Implemented |
| `bank_statement` | Yes | Implemented |
| `business_license` | Yes | Implemented |
| `audit_report` | Yes | Implemented |
| `credit_report` | Yes | Implemented |
| `shareholder_info` | Yes | Implemented |
| `financial_notes` | Yes | Implemented |
| `md_and_a` | Yes | Implemented |
| `guarantee` | Yes | Implemented |
| `equity_changes_stmt` | Yes | Implemented |
| `tax_invoice` | No (generic fallback) | Needs implementation |
| `fixed_asset` | No (generic fallback) | Needs implementation |
| `lease_contract` | No (generic fallback) | Needs implementation |
| `property_cert` | No (generic fallback) | Needs implementation |
| `land_cert` | No (generic fallback) | Needs implementation |

### Adding a New Extractor

1. Create `src/findocparser/extractors/<doc_type>.py`
2. Subclass `BaseExtractor` and implement `build_prompt()` + `parse_response()`
3. Register in `src/findocparser/extractors/registry.py`
4. Add detection keywords in `src/findocparser/detect.py` (if not already present)
5. Add entry to the document types table in `README.md`
6. Add tests in `tests/test_extractors.py`

### Code Style

This project uses **ruff** for linting and formatting:

```bash
# Lint
ruff check .

# Auto-fix
ruff check --fix .

# Format
ruff format .
```

Configuration in `pyproject.toml`:
- Line length: 100
- Target: Python 3.11
- Rules: E, W, F, I, B, C4, UP

### Type Checking

```bash
mypy src/findocparser/
```

## Testing

### Run Tests

```bash
# All tests
pytest

# Verbose
pytest -v

# Specific test file
pytest tests/test_extractors.py

# Specific test
pytest tests/test_extractors.py::test_financial_statement_extractor
```

### Test Structure

```
tests/
  conftest.py          # Shared fixtures
  test_detect.py       # File/document type detection
  test_extractors.py   # Extractor unit tests
  test_llm_client.py   # LLM client tests
  test_parsers.py      # OCR & Excel parser tests
  test_pipeline.py     # End-to-end pipeline tests
  test_compare.py      # Multi-period comparison tests
```

### Coverage

```bash
pytest --cov=findocparser --cov-report=term-missing
```

## Build & Publish

### Build

```bash
python -m build
# Output in dist/
```

Build system: **hatchling** (configured in `pyproject.toml`).

### Publish to PyPI

```bash
pip install twine
twine upload dist/*
```

Requires a PyPI API token configured in `~/.pypirc`.

## Optional Dependencies

| Extra | Packages | Purpose |
|---|---|---|
| `excel` | openpyxl, xlrd | Parse .xlsx, .xls files |
| `pdf` | pymupdf | Extract text from PDFs (no OCR) |
| `ocr` | paddleocr, paddlepaddle | Local OCR (no external service) |
| `all` | All of the above | Everything |
| `dev` | pytest, pytest-asyncio, ruff, mypy | Development tools |

## Areas Needing Help

- Dedicated extractors for: tax_invoice, fixed_asset, lease_contract, property_cert, land_cert
- Better prompt templates for higher extraction accuracy
- More OCR backends (Surya, EasyOCR, Tesseract)
- More LLM providers (Claude, Gemini, Kimi)
- Test coverage improvements

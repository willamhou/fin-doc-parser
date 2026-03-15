<div align="center">

# fin-doc-parser

**AI-powered financial document parsing SDK**

Extract structured JSON from financial statements, bank statements, invoices, business licenses, and more.

[![PyPI](https://img.shields.io/pypi/v/fin-doc-parser.svg)](https://pypi.org/project/fin-doc-parser/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

[English](#quick-start) | [中文](#快速开始)

</div>

---

## Why fin-doc-parser?

Financial documents are messy — scanned PDFs, inconsistent Excel formats, images of licenses. Extracting structured data from them typically requires weeks of custom code.

**fin-doc-parser** solves this in 3 lines:

```python
from findocparser import parse

result = parse("财务报表2024.pdf", doc_type="financial_statement")
print(result["data"]["balance_sheet"]["total_assets"])  # 125000000.0
```

## Features

- **9 document types** — financial statements, bank statements, business licenses, credit reports, tax invoices, fixed assets, lease contracts, shareholder info, property certs
- **Pluggable OCR** — PaddleOCR (local, free), Prismer (GPU service), or text-only extraction
- **Pluggable LLM** — DeepSeek, OpenAI, or any OpenAI-compatible API (Ollama, vLLM, etc.)
- **Bring your own client** — pass a pre-configured `LLMClient` instance directly
- **Excel support** — xlsx, xls, csv with automatic markdown conversion
- **Auto-detection** — file type and document type detected from filename and content
- **Generic fallback** — unknown document types get a best-effort extraction
- **Async-first** — `parse_async()` for high-throughput pipelines
- **Minimal core** — only `httpx` required; OCR, Excel, PDF are optional

## Quick Start

### Install

```bash
pip install fin-doc-parser

# With Excel support (xlsx/xls)
pip install "fin-doc-parser[excel]"

# With PDF text extraction (PyMuPDF)
pip install "fin-doc-parser[pdf]"

# With local OCR (PaddleOCR, no external service)
pip install "fin-doc-parser[ocr]"

# Everything
pip install "fin-doc-parser[all]"
```

### Set API key

```bash
# Pick one:
export DEEPSEEK_API_KEY="sk-..."    # Recommended (cheap + good at Chinese)
export OPENAI_API_KEY="sk-..."       # Also works
```

### Parse a document

```python
from findocparser import parse

# Financial statement (PDF or image)
result = parse("资产负债表2024.pdf")
balance_sheet = result["data"]["balance_sheet"]
print(f"Total assets: {balance_sheet['total_assets']}")
print(f"Total liabilities: {balance_sheet['total_liabilities']}")

# Bank statement
result = parse("银行流水_2024.pdf")
for txn in result["data"]["transactions"][:5]:
    print(f"{txn['date']}  {txn['counterparty']}  {txn['amount']}")

# Business license (image)
result = parse("营业执照.jpg")
print(f"Company: {result['data']['company_name']}")
print(f"Credit code: {result['data']['unified_social_credit_code']}")

# Excel file
result = parse("固定资产清单.xlsx", doc_type="fixed_asset")

# Auto-detect document type
result = parse("some_unknown_document.pdf")
print(f"Detected type: {result['doc_type']}")
```

### Async usage

```python
import asyncio
from findocparser import parse_async

async def main():
    result = await parse_async("report.pdf", llm_provider="deepseek")
    print(result["data"])

asyncio.run(main())
```

### Custom LLM endpoint

```python
from findocparser import parse, parse_async, OpenAIClient

# Option 1: Pass config through parse()
result = parse(
    "report.pdf",
    llm_base_url="http://localhost:11434/v1",  # Ollama
    llm_api_key="ollama",
    llm_model="qwen2.5:14b",
)

# Option 2: Bring your own LLM client
client = OpenAIClient(
    provider="openai",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:14b",
)
result = parse("report.pdf", llm_client=client)
```

---

## 快速开始

### 安装

```bash
pip install fin-doc-parser

# 带 Excel 支持
pip install "fin-doc-parser[excel]"

# 带 PDF 文本提取
pip install "fin-doc-parser[pdf]"

# 带本地 OCR（无需外部服务）
pip install "fin-doc-parser[ocr]"
```

### 配置 API 密钥

```bash
export DEEPSEEK_API_KEY="sk-..."    # 推荐（便宜 + 中文能力强）
```

### 解析文档

```python
from findocparser import parse

# 一行代码解析财务报表
result = parse("资产负债表2024.pdf")
print(result["data"]["balance_sheet"]["total_assets"])

# 解析银行流水
result = parse("银行流水.pdf")
print(result["data"]["transactions"])

# 解析营业执照（图片）
result = parse("营业执照.jpg")
print(result["data"]["company_name"])

# 自定义 LLM 端点（如 Ollama）
result = parse(
    "report.pdf",
    llm_base_url="http://localhost:11434/v1",
    llm_api_key="ollama",
    llm_model="qwen2.5:14b",
)
```

---

## Supported Document Types

| Document Type | `doc_type` | Input Formats | Output |
|---|---|---|---|
| Financial Statement | `financial_statement` | PDF, image, Excel | Balance sheet, income statement, cash flow |
| Bank Statement | `bank_statement` | PDF, image | Transaction list with counterparty & amounts |
| Business License | `business_license` | PDF, image | Company name, credit code, legal rep, scope |
| Credit Report | `credit_report` | PDF | Credit lines, overdue records, utilization |
| Tax Invoice | `tax_invoice` | PDF, image, Excel | Invoice items, amounts, tax rates |
| Fixed Asset | `fixed_asset` | Excel | Asset list with depreciation |
| Lease Contract | `lease_contract` | PDF | Terms, amounts, maturity dates |
| Shareholder Info | `shareholder_info` | PDF, image | Shareholder names, ratios, capital |
| Property Cert | `property_cert` | PDF, image | Owner, location, area, registration |
| *(any other)* | `generic` | PDF, image, Excel | Auto-extracted key entities & numbers |

## Architecture

```
parse("document.pdf")
    │
    ├─ detect_file_type()      →  pdf / image / excel
    │
    ├─ OCR or Excel Parser     →  raw text (markdown)
    │   ├─ PaddleOCR (local)        [ocr]
    │   ├─ Prismer (GPU service)    env: PRISMER_OCR_BASE_URL
    │   ├─ PyMuPDF (text-only)      [pdf]
    │   └─ openpyxl / xlrd          [excel]
    │
    ├─ detect_doc_type()       →  financial_statement / bank_statement / ...
    │
    └─ LLM Extractor           →  structured JSON
        ├─ DeepSeek (default)
        ├─ OpenAI
        └─ Any OpenAI-compatible API
```

## API Reference

### `parse(file_path, **kwargs)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str \| Path` | *required* | Path to document |
| `doc_type` | `str \| None` | `None` | Document type (auto-detect if None) |
| `llm_provider` | `str` | `"deepseek"` | LLM provider name |
| `llm_client` | `LLMClient \| None` | `None` | Pre-configured client (overrides provider) |
| `llm_base_url` | `str \| None` | `None` | Override provider base URL |
| `llm_api_key` | `str \| None` | `None` | Override API key |
| `llm_model` | `str \| None` | `None` | Override model name |
| `ocr_backend` | `str` | `"auto"` | OCR backend: auto, paddleocr, prismer, none |

Returns `dict` with keys: `doc_type`, `file_name`, `file_type`, `data`.

### `parse_async(...)` — same parameters, returns coroutine.

## Configuration

### OCR Backend

```python
# Auto (default): try text extraction first, fall back to PaddleOCR
parse("doc.pdf", ocr_backend="auto")

# Local PaddleOCR (no external service)
parse("doc.pdf", ocr_backend="paddleocr")

# Prismer service (requires PRISMER_OCR_BASE_URL env var)
parse("doc.pdf", ocr_backend="prismer")

# Text-only (PDF with selectable text, no OCR)
parse("doc.pdf", ocr_backend="none")
```

### LLM Provider

```python
# DeepSeek (default, recommended for Chinese documents)
parse("doc.pdf", llm_provider="deepseek")

# OpenAI
parse("doc.pdf", llm_provider="openai")
```

## Contributing

Contributions welcome! Areas that need help:

- [ ] More extractors (credit report, tax invoice, fixed asset, lease, shareholder, property)
- [ ] Better prompt templates for higher extraction accuracy
- [ ] More OCR backends (Surya, EasyOCR, Tesseract)
- [ ] More LLM providers (Claude, Gemini, Kimi)
- [ ] Test coverage

```bash
git clone https://github.com/willamhou/fin-doc-parser.git
cd fin-doc-parser
pip install -e ".[dev]"
pytest
```

## License

[Apache License 2.0](LICENSE)

## Related Projects

- [FinSight](https://github.com/willamhou/finsight) — AI-powered stock analysis tool built on fin-doc-parser

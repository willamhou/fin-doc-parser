# Runbook — fin-doc-parser

## Overview

fin-doc-parser is a Python SDK (library), not a standalone service. This runbook covers integration, troubleshooting, and operational guidance for applications that depend on it.

## Deployment

### As a Library Dependency

```bash
# From PyPI (v0.1.0+)
pip install fin-doc-parser

# With specific extras
pip install "fin-doc-parser[all]"

# From source (pinned to a commit)
pip install git+https://github.com/willamhou/fin-doc-parser.git@<commit-hash>
```

### Environment Setup

Ensure the following environment variables are set in your deployment:

| Variable | Required | Notes |
|---|---|---|
| `DEEPSEEK_API_KEY` | Yes (or OPENAI) | DeepSeek API key for LLM extraction |
| `OPENAI_API_KEY` | Alternative | If using OpenAI instead of DeepSeek |
| `PRISMER_OCR_BASE_URL` | Only if using Prismer | URL to Prismer OCR service (e.g., `http://localhost:8000`) |

### Self-Hosted LLM (Recommended for PII)

For documents containing PII (credit reports, bank statements):

```python
result = parse(
    "sensitive_doc.pdf",
    llm_base_url="http://your-vllm-server:8000/v1",
    llm_api_key="local",
    llm_model="Qwen/Qwen2.5-14B",
)
```

## Common Issues & Fixes

### 1. `ValueError: DEEPSEEK_API_KEY environment variable is required`

**Cause:** No LLM API key configured.

**Fix:** Set either `DEEPSEEK_API_KEY` or `OPENAI_API_KEY`, or pass `llm_api_key` directly:
```python
parse("doc.pdf", llm_api_key="sk-...", llm_provider="deepseek")
```

### 2. `ValueError: PRISMER_OCR_BASE_URL environment variable is required`

**Cause:** Using `ocr_backend="prismer"` without configuring the URL.

**Fix:** Set the env var or switch OCR backend:
```bash
export PRISMER_OCR_BASE_URL="http://localhost:8000"
```
Or use a different backend:
```python
parse("doc.pdf", ocr_backend="paddleocr")  # Local OCR
parse("doc.pdf", ocr_backend="none")        # Text-only (no OCR)
```

### 3. `ImportError: paddleocr is not installed`

**Cause:** Using PaddleOCR backend without the optional dependency.

**Fix:**
```bash
pip install "fin-doc-parser[ocr]"
```

### 4. `ImportError: openpyxl is not installed`

**Cause:** Parsing Excel files without the optional dependency.

**Fix:**
```bash
pip install "fin-doc-parser[excel]"
```

### 5. LLM Returns Invalid JSON

**Cause:** LLM response doesn't contain valid JSON (common with smaller models).

**Fix:**
- Use a larger/better model (DeepSeek-Chat or GPT-4o recommended)
- The SDK has built-in JSON extraction that handles markdown code blocks and escaped text
- If persistent, check the raw LLM response in debug logs

### 6. OCR Quality Issues

**Cause:** Scanned document has low resolution or complex layouts.

**Fix:**
- Use higher-resolution scans (300+ DPI)
- Try PaddleOCR over text-only extraction for scanned PDFs
- For complex layouts, consider Prismer GPU service

### 7. Wrong Document Type Detected

**Cause:** Auto-detection relies on filename and content keywords.

**Fix:** Explicitly specify the document type:
```python
parse("ambiguous_file.pdf", doc_type="financial_statement")
```

### 8. Document Type Falls Back to Generic

**Cause:** Some detected doc types (tax_invoice, fixed_asset, lease_contract, property_cert, land_cert) do not have dedicated extractors yet and fall back to `GenericExtractor`.

**Fix:** The generic extractor does best-effort extraction. For better results, either:
- Contribute a dedicated extractor (see `docs/CONTRIB.md`)
- Post-process the generic output in your application

## Monitoring & Observability

Since fin-doc-parser is a library, monitoring is the responsibility of the consuming application. Key metrics to track:

| Metric | What to Watch |
|---|---|
| Parse latency | LLM API call time dominates; typical 5-30s per document |
| LLM error rate | Track 4xx/5xx from LLM provider |
| OCR success rate | Track OCR failures vs. fallback to text-only |
| Extraction accuracy | Sample-check extracted JSON against ground truth |
| API key quota | Monitor LLM provider usage/billing |

### Logging

Enable debug logging in your application:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Rollback Procedures

### Dependency Rollback

If a new version introduces issues:

```bash
# Pin to a known-good version
pip install fin-doc-parser==0.1.0

# Or pin in requirements.txt / pyproject.toml
# fin-doc-parser==0.1.0
```

### LLM Provider Fallback

If primary LLM provider is down, switch provider at runtime:

```python
# Primary: DeepSeek
result = parse("doc.pdf", llm_provider="deepseek")

# Fallback: OpenAI
result = parse("doc.pdf", llm_provider="openai")

# Fallback: Self-hosted
result = parse("doc.pdf", llm_base_url="http://backup:8000/v1", llm_api_key="local")
```

### OCR Backend Fallback

```python
# Primary: PaddleOCR
parse("doc.pdf", ocr_backend="paddleocr")

# Fallback: text-only (works for PDFs with selectable text)
parse("doc.pdf", ocr_backend="none")
```

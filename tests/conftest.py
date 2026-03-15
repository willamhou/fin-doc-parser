"""Shared test fixtures — mock LLM client, temp files, etc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Mock LLM client
# ---------------------------------------------------------------------------

class MockLLMClient:
    """LLM client that returns pre-canned JSON responses.

    Use ``responses`` dict to register expected outputs keyed by doc_type
    or a substring of the prompt.
    """

    def __init__(self, responses: dict[str, dict[str, Any]] | None = None):
        self.responses = responses or {}
        self.call_count = 0
        self.last_prompt: str | None = None

    async def extract_json(self, prompt: str) -> dict[str, Any]:
        self.call_count += 1
        self.last_prompt = prompt

        # Match by key substring in prompt
        for key, response in self.responses.items():
            if key in prompt:
                return response

        # Default: return a generic extraction
        return {
            "document_type": "unknown",
            "summary": "Mock extraction result",
            "extraction_confidence": 0.95,
        }


@pytest.fixture
def mock_llm():
    """Provide a MockLLMClient factory."""
    return MockLLMClient


@pytest.fixture
def mock_llm_financial():
    """MockLLMClient pre-loaded with financial statement response."""
    return MockLLMClient(responses={
        "财务报表": {
            "statement_type": "balance_sheet",
            "report_period": "2024-12-31",
            "currency": "CNY",
            "balance_sheet": {
                "total_assets": 125000000.0,
                "total_liabilities": 50000000.0,
                "total_equity": 75000000.0,
                "current_assets": 45000000.0,
                "non_current_assets": 80000000.0,
                "current_liabilities": 30000000.0,
                "non_current_liabilities": 20000000.0,
                "cash_and_equivalents": 15000000.0,
                "accounts_receivable": 12000000.0,
                "inventory": 8000000.0,
                "fixed_assets": 60000000.0,
                "short_term_borrowing": 10000000.0,
                "long_term_borrowing": 15000000.0,
                "accounts_payable": 9000000.0,
            },
            "income_statement": {
                "revenue": 200000000.0,
                "cost_of_goods_sold": 140000000.0,
                "gross_profit": 60000000.0,
                "operating_expenses": 30000000.0,
                "operating_income": 30000000.0,
                "net_income": 25000000.0,
                "ebitda": 35000000.0,
            },
            "cash_flow": {
                "operating_cash_flow": 28000000.0,
                "investing_cash_flow": -15000000.0,
                "financing_cash_flow": -5000000.0,
                "net_cash_flow": 8000000.0,
            },
        },
    })


@pytest.fixture
def mock_llm_bank():
    """MockLLMClient pre-loaded with bank statement response."""
    return MockLLMClient(responses={
        "银行流水": {
            "account_name": "某某公司",
            "account_number": "6222021234567890",
            "bank_name": "中国工商银行",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "opening_balance": 1000000.0,
            "closing_balance": 1500000.0,
            "transactions": [
                {
                    "date": "2024-01-15",
                    "description": "货款",
                    "counterparty": "供应商A",
                    "amount": -50000.0,
                    "balance": 950000.0,
                    "type": "debit",
                },
                {
                    "date": "2024-01-20",
                    "description": "销售收入",
                    "counterparty": "客户B",
                    "amount": 120000.0,
                    "balance": 1070000.0,
                    "type": "credit",
                },
            ],
        },
    })


@pytest.fixture
def mock_llm_license():
    """MockLLMClient pre-loaded with business license response."""
    return MockLLMClient(responses={
        "营业执照": {
            "company_name": "北京示例科技有限公司",
            "unified_social_credit_code": "91110108MA01XXXXX",
            "legal_representative": "张三",
            "registered_capital": 1000,
            "establishment_date": "2020-01-15",
            "business_term_start": "2020-01-15",
            "business_term_end": "长期",
            "registered_address": "北京市海淀区中关村大街1号",
            "business_scope": "技术开发；技术咨询；软件开发",
            "company_type": "有限责任公司",
        },
    })


# ---------------------------------------------------------------------------
# Temp file fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_csv(tmp_path: Path) -> Path:
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(
        "日期,摘要,金额,余额\n"
        "2024-01-01,期初余额,0,1000000\n"
        "2024-01-15,采购付款,-50000,950000\n"
        "2024-01-20,销售回款,120000,1070000\n",
        encoding="utf-8",
    )
    return csv_file


@pytest.fixture
def tmp_txt_pdf(tmp_path: Path) -> Path:
    """Create a temporary text file pretending to be a PDF (for testing detect)."""
    f = tmp_path / "资产负债表2024.pdf"
    f.write_text("placeholder", encoding="utf-8")
    return f

"""Financial statement extractor."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class FinancialStatementExtractor(BaseExtractor):
    """Extract structured data from financial statements (balance sheet, income, cash flow)."""

    @property
    def doc_type(self) -> str:
        return "financial_statement"

    @property
    def prompt_template(self) -> str:
        return """请从以下财务报表中提取结构化数据。

文档内容:
{content}

请以 JSON 格式返回，包含以下部分 (缺失的部分返回 null):
{{
    "statement_type": "balance_sheet | income_statement | cash_flow",
    "report_period": "报告期 (如 2024-12-31)",
    "currency": "币种",
    "balance_sheet": {{
        "total_assets": null,
        "total_liabilities": null,
        "total_equity": null,
        "current_assets": null,
        "non_current_assets": null,
        "current_liabilities": null,
        "non_current_liabilities": null,
        "cash_and_equivalents": null,
        "accounts_receivable": null,
        "inventory": null,
        "fixed_assets": null,
        "short_term_borrowing": null,
        "long_term_borrowing": null,
        "accounts_payable": null
    }},
    "income_statement": {{
        "revenue": null,
        "cost_of_goods_sold": null,
        "gross_profit": null,
        "operating_expenses": null,
        "operating_income": null,
        "net_income": null,
        "ebitda": null
    }},
    "cash_flow": {{
        "operating_cash_flow": null,
        "investing_cash_flow": null,
        "financing_cash_flow": null,
        "net_cash_flow": null
    }}
}}

注意: 所有金额统一为元(人民币)，不要带单位文字。如果是万元请乘以10000。"""

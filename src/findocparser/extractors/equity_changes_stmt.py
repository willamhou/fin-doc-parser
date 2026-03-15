"""Statement of changes in equity extractor (所有者权益变动表)."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class EquityChangesStmtExtractor(BaseExtractor):
    """Extract structured data from statement of changes in equity (所有者权益变动表).

    The fourth mandatory financial statement under CAS, covering capital changes,
    profit distribution, and other comprehensive income.
    """

    @property
    def doc_type(self) -> str:
        return "equity_changes_stmt"

    @property
    def prompt_template(self) -> str:
        return """请从以下所有者权益变动表中提取关键数据。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "企业名称",
    "report_period": "报告期 (如 2024-12-31)",
    "currency": "币种",
    "opening_balance": {{
        "share_capital": null,
        "capital_reserve": null,
        "other_comprehensive_income": null,
        "special_reserve": null,
        "surplus_reserve": null,
        "retained_earnings": null,
        "total_equity_parent": null,
        "minority_interest": null,
        "total_equity": null
    }},
    "changes": {{
        "net_income": null,
        "other_comprehensive_income_change": null,
        "total_comprehensive_income": null,
        "share_capital_increase": null,
        "capital_reserve_increase": null,
        "profit_distribution": {{
            "statutory_surplus_reserve": null,
            "discretionary_surplus_reserve": null,
            "dividends_declared": null,
            "dividend_per_share": null
        }},
        "share_based_payment": null,
        "other_equity_changes": null
    }},
    "closing_balance": {{
        "share_capital": null,
        "capital_reserve": null,
        "other_comprehensive_income": null,
        "special_reserve": null,
        "surplus_reserve": null,
        "retained_earnings": null,
        "total_equity_parent": null,
        "minority_interest": null,
        "total_equity": null
    }}
}}

注意: 所有金额统一为元(人民币)。如果是万元请乘以10000。"""

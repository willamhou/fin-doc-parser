"""Credit report extractor."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class CreditReportExtractor(BaseExtractor):
    """Extract structured data from corporate credit reports (征信报告)."""

    @property
    def doc_type(self) -> str:
        return "credit_report"

    @property
    def prompt_template(self) -> str:
        return """请从以下企业征信报告中提取关键信息。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "企业名称",
    "credit_code": "统一社会信用代码",
    "query_date": "查询日期 (YYYY-MM-DD)",
    "credit_score": null,
    "credit_level": "信用等级 (如 AAA/AA/A/BBB/BB/B/C/D)",
    "outstanding_loans": {{
        "total_count": null,
        "total_amount": null,
        "normal_count": null,
        "overdue_count": null,
        "overdue_amount": null
    }},
    "credit_cards": {{
        "total_count": null,
        "total_limit": null,
        "used_amount": null,
        "overdue_count": null,
        "overdue_amount": null
    }},
    "guarantees": {{
        "total_count": null,
        "total_amount": null
    }},
    "overdue_records": [
        {{
            "type": "贷款 | 信用卡 | 担保",
            "institution": "机构名称",
            "amount": null,
            "overdue_days": null,
            "status": "状态"
        }}
    ],
    "query_records": [
        {{
            "date": "查询日期 (YYYY-MM-DD)",
            "institution": "查询机构",
            "reason": "查询原因"
        }}
    ],
    "public_records": {{
        "tax_arrears": null,
        "civil_judgments": null,
        "enforcements": null
    }}
}}

注意: 金额统一为元(人民币)。逾期记录和查询记录最多各提取20条。"""

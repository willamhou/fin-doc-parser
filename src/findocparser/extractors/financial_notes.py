"""Financial statement notes extractor (财务报表附注)."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class FinancialNotesExtractor(BaseExtractor):
    """Extract structured data from financial statement notes (财务报表附注).

    Covers key disclosures required by CAS (企业会计准则) in A-share annual reports:
    related party transactions, contingent liabilities, accounting policy changes,
    and significant accounting estimates.
    """

    @property
    def doc_type(self) -> str:
        return "financial_notes"

    @property
    def prompt_template(self) -> str:
        return """请从以下财务报表附注中提取关键信息。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "企业名称",
    "fiscal_year_end": "报告期末日期 (YYYY-MM-DD)",
    "accounting_policies": {{
        "revenue_recognition": "收入确认方法描述",
        "bad_debt_provision": "坏账准备计提方法 (账龄分析法/个别认定法等)",
        "depreciation_method": "折旧方法及年限",
        "policy_changes": [
            {{
                "item": "变更项目",
                "from_policy": "原政策",
                "to_policy": "新政策",
                "impact_amount": null,
                "reason": "变更原因"
            }}
        ]
    }},
    "related_party_transactions": [
        {{
            "party_name": "关联方名称",
            "relationship": "关系类型 (母公司/子公司/联营/合营/关键管理人等)",
            "transaction_type": "交易类型 (销售/采购/借款/担保等)",
            "amount": null,
            "pricing_method": "定价方式"
        }}
    ],
    "contingent_liabilities": [
        {{
            "type": "类型 (未决诉讼/对外担保/票据贴现/其他)",
            "description": "描述",
            "amount": null,
            "probability": "可能性 (很可能/可能/极小可能)"
        }}
    ],
    "pledged_assets": [
        {{
            "asset_type": "资产类型",
            "book_value": null,
            "pledge_purpose": "用途 (借款担保/票据保证金等)"
        }}
    ],
    "significant_estimates": [
        {{
            "item": "估计项目 (坏账/减值/公允价值/预计负债等)",
            "method": "估计方法",
            "key_assumptions": "关键假设"
        }}
    ],
    "subsequent_events": [
        {{
            "date": "事件日期 (YYYY-MM-DD)",
            "description": "事件描述",
            "financial_impact": null
        }}
    ]
}}

注意: 金额统一为元(人民币)。关联交易和或有负债最多各提取20条。"""

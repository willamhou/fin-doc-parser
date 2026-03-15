"""Guarantee disclosure extractor (对外担保)."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class GuaranteeExtractor(BaseExtractor):
    """Extract structured data from guarantee disclosures (对外担保).

    A-share listed companies must disclose all external guarantees per
    CSRC regulations. Critical for assessing contingent liability risk.
    """

    @property
    def doc_type(self) -> str:
        return "guarantee"

    @property
    def prompt_template(self) -> str:
        return """请从以下对外担保信息中提取关键数据。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "担保方(上市公司)名称",
    "report_date": "披露日期 (YYYY-MM-DD)",
    "guarantee_summary": {{
        "total_guarantee_amount": null,
        "total_guarantee_to_net_assets_pct": null,
        "overdue_guarantee_amount": null,
        "guarantee_for_subsidiaries": null,
        "guarantee_for_shareholders": null,
        "guarantee_for_related_parties": null,
        "guarantee_for_others": null
    }},
    "guarantee_details": [
        {{
            "guaranteed_party": "被担保方名称",
            "relationship": "关联关系 (子公司/联营/关联方/无关联第三方)",
            "guarantee_amount": null,
            "guarantee_type": "一般保证 | 连带责任保证",
            "start_date": "担保起始日 (YYYY-MM-DD)",
            "end_date": "担保到期日 (YYYY-MM-DD)",
            "is_completed": false,
            "is_overdue": false,
            "counter_guarantee": "反担保措施 (如有)"
        }}
    ],
    "violation_guarantees": [
        {{
            "guaranteed_party": "被担保方名称",
            "amount": null,
            "reason": "违规原因",
            "resolution": "解决措施"
        }}
    ]
}}

注意: 金额统一为元(人民币)。百分比为数值(如35.5表示35.5%)。担保明细最多提取30条。"""

"""Shareholder info extractor."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class ShareholderInfoExtractor(BaseExtractor):
    """Extract structured shareholder and equity data (股东信息/股权结构)."""

    @property
    def doc_type(self) -> str:
        return "shareholder_info"

    @property
    def prompt_template(self) -> str:
        return """请从以下股东信息/股权结构文档中提取关键信息。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "企业名称",
    "registered_capital": null,
    "paid_in_capital": null,
    "currency": "币种",
    "shareholders": [
        {{
            "name": "股东名称",
            "type": "自然人 | 法人 | 合伙企业 | 其他",
            "id_number": "身份证号/统一社会信用代码",
            "subscribed_amount": null,
            "paid_in_amount": null,
            "ownership_pct": "持股比例 (0-100的数值)",
            "subscription_date": "认缴日期 (YYYY-MM-DD)"
        }}
    ],
    "actual_controller": {{
        "name": "实际控制人姓名",
        "id_number": "身份证号",
        "control_pct": "控制比例 (0-100的数值)",
        "control_path": "控制路径描述"
    }},
    "equity_pledges": [
        {{
            "pledgor": "出质人",
            "pledgee": "质权人",
            "pledged_amount": null,
            "pledge_date": "质押日期 (YYYY-MM-DD)",
            "status": "有效 | 已解除"
        }}
    ],
    "equity_changes": [
        {{
            "date": "变更日期 (YYYY-MM-DD)",
            "type": "转让 | 增资 | 减资",
            "description": "变更描述"
        }}
    ]
}}

注意: 金额统一为万元。持股比例为百分比数值(如25.5表示25.5%)。最多提取前50名股东、20条质押记录和20条变更记录。"""

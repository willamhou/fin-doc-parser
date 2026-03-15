"""Audit report extractor (审计报告)."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class AuditReportExtractor(BaseExtractor):
    """Extract structured data from audit reports (审计报告).

    Covers standard Chinese CPA audit reports per CSA (中国注册会计师审计准则),
    commonly found in A-share annual report filings.
    """

    @property
    def doc_type(self) -> str:
        return "audit_report"

    @property
    def prompt_template(self) -> str:
        return """请从以下审计报告中提取关键信息。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "audit_firm": "会计师事务所名称",
    "report_date": "审计报告日期 (YYYY-MM-DD)",
    "report_number": "报告文号",
    "company_name": "被审计单位名称",
    "fiscal_year_end": "审计期间截止日 (YYYY-MM-DD)",
    "opinion_type": "标准无保留意见 | 带强调事项段的无保留意见 | 保留意见 | 否定意见 | 无法表示意见",
    "opinion_basis": "审计意见的依据说明",
    "going_concern": {{
        "has_uncertainty": false,
        "description": "持续经营不确定性描述 (如无则为 null)"
    }},
    "key_audit_matters": [
        {{
            "title": "关键审计事项标题",
            "description": "事项描述",
            "audit_response": "审计应对措施"
        }}
    ],
    "emphasis_of_matter": [
        {{
            "title": "强调事项标题",
            "description": "事项描述"
        }}
    ],
    "other_matters": "其他事项说明 (如无则为 null)",
    "signatories": [
        {{
            "name": "签字注册会计师姓名",
            "cpa_number": "执业证书编号"
        }}
    ]
}}

注意:
- opinion_type 必须是以下五种之一: 标准无保留意见、带强调事项段的无保留意见、保留意见、否定意见、无法表示意见
- 关键审计事项和强调事项如果没有则返回空数组
- 最多提取前10条关键审计事项"""

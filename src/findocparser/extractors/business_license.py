"""Business license extractor."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class BusinessLicenseExtractor(BaseExtractor):
    """Extract structured data from business licenses."""

    @property
    def doc_type(self) -> str:
        return "business_license"

    @property
    def prompt_template(self) -> str:
        return """请从以下营业执照内容中提取关键信息。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "企业名称",
    "unified_social_credit_code": "统一社会信用代码",
    "legal_representative": "法定代表人",
    "registered_capital": "注册资本 (数值，单位万元)",
    "establishment_date": "成立日期 (YYYY-MM-DD)",
    "business_term_start": "营业期限起 (YYYY-MM-DD)",
    "business_term_end": "营业期限止 (YYYY-MM-DD 或 长期)",
    "registered_address": "注册地址",
    "business_scope": "经营范围",
    "company_type": "企业类型"
}}"""

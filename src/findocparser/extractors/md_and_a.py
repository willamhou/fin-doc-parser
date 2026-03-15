"""Management Discussion & Analysis extractor (管理层讨论与分析)."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class MdAndAExtractor(BaseExtractor):
    """Extract structured data from MD&A section (管理层讨论与分析).

    Standard section in A-share annual reports covering business review,
    industry analysis, risk factors, and future outlook.
    """

    @property
    def doc_type(self) -> str:
        return "md_and_a"

    @property
    def prompt_template(self) -> str:
        return """请从以下管理层讨论与分析(MD&A)中提取关键信息。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "company_name": "企业名称",
    "fiscal_year": "报告年度",
    "business_overview": {{
        "main_business": "主营业务描述",
        "industry": "所属行业",
        "business_model": "盈利模式",
        "core_competitiveness": "核心竞争力"
    }},
    "operating_results": {{
        "revenue_change_pct": null,
        "net_income_change_pct": null,
        "revenue_drivers": "收入变动主要原因",
        "cost_drivers": "成本变动主要原因",
        "gross_margin_change": "毛利率变动说明"
    }},
    "industry_analysis": {{
        "industry_trends": "行业发展趋势",
        "competitive_landscape": "竞争格局",
        "regulatory_environment": "监管政策变化"
    }},
    "risk_factors": [
        {{
            "category": "宏观经济 | 行业政策 | 经营管理 | 财务 | 法律合规 | 技术",
            "description": "风险描述",
            "mitigation": "应对措施"
        }}
    ],
    "future_outlook": {{
        "development_strategy": "发展战略",
        "business_plan": "经营计划",
        "capex_plan": "资本开支计划",
        "rd_plan": "研发计划"
    }},
    "major_events": [
        {{
            "event": "事件描述",
            "impact": "对公司的影响"
        }}
    ]
}}

注意: 百分比变动为数值(如15.5表示增长15.5%，-8.2表示下降8.2%)。风险因素最多提取10条。"""

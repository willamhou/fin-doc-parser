"""Shared test fixtures — mock LLM client, temp files, etc."""

from __future__ import annotations

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
    return MockLLMClient(
        responses={
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
        }
    )


@pytest.fixture
def mock_llm_bank():
    """MockLLMClient pre-loaded with bank statement response."""
    return MockLLMClient(
        responses={
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
        }
    )


@pytest.fixture
def mock_llm_audit():
    """MockLLMClient pre-loaded with audit report response."""
    return MockLLMClient(
        responses={
            "审计报告": {
                "audit_firm": "普华永道中天会计师事务所",
                "report_date": "2025-03-28",
                "report_number": "普华永道中天审字(2025)第12345号",
                "company_name": "北京示例科技股份有限公司",
                "fiscal_year_end": "2024-12-31",
                "opinion_type": "标准无保留意见",
                "opinion_basis": "我们按照中国注册会计师审计准则的规定执行了审计工作。",
                "going_concern": {
                    "has_uncertainty": False,
                    "description": None,
                },
                "key_audit_matters": [
                    {
                        "title": "收入确认",
                        "description": "公司2024年度营业收入为20亿元，收入确认涉及重大管理层判断。",
                        "audit_response": "我们评价了收入确认相关的内部控制，对收入交易执行了细节测试。",
                    },
                    {
                        "title": "应收账款坏账准备",
                        "description": "截至2024年12月31日应收账款余额为1.2亿元，坏账准备计提涉及管理层估计。",
                        "audit_response": "我们评价了管理层采用的预期信用损失模型及关键假设。",
                    },
                ],
                "emphasis_of_matter": [],
                "other_matters": None,
                "signatories": [
                    {"name": "李明", "cpa_number": "110XXXXXXX01"},
                    {"name": "王芳", "cpa_number": "110XXXXXXX02"},
                ],
            },
        }
    )


@pytest.fixture
def mock_llm_credit():
    """MockLLMClient pre-loaded with credit report response."""
    return MockLLMClient(
        responses={
            "征信报告": {
                "company_name": "北京示例科技有限公司",
                "credit_code": "91110108MA01XXXXX",
                "query_date": "2024-06-15",
                "credit_score": 720,
                "credit_level": "AA",
                "outstanding_loans": {
                    "total_count": 3,
                    "total_amount": 5000000.0,
                    "normal_count": 2,
                    "overdue_count": 1,
                    "overdue_amount": 200000.0,
                },
                "credit_cards": {
                    "total_count": 2,
                    "total_limit": 500000.0,
                    "used_amount": 150000.0,
                    "overdue_count": 0,
                    "overdue_amount": 0,
                },
                "guarantees": {
                    "total_count": 1,
                    "total_amount": 1000000.0,
                },
                "overdue_records": [
                    {
                        "type": "贷款",
                        "institution": "中国银行",
                        "amount": 200000.0,
                        "overdue_days": 30,
                        "status": "已结清",
                    },
                ],
                "query_records": [
                    {
                        "date": "2024-06-01",
                        "institution": "工商银行",
                        "reason": "贷后管理",
                    },
                ],
                "public_records": {
                    "tax_arrears": 0,
                    "civil_judgments": 0,
                    "enforcements": 0,
                },
            },
        }
    )


@pytest.fixture
def mock_llm_shareholder():
    """MockLLMClient pre-loaded with shareholder info response."""
    return MockLLMClient(
        responses={
            "股东信息": {
                "company_name": "北京示例科技有限公司",
                "registered_capital": 1000,
                "paid_in_capital": 1000,
                "currency": "CNY",
                "shareholders": [
                    {
                        "name": "张三",
                        "type": "自然人",
                        "id_number": "110101199001011234",
                        "subscribed_amount": 600,
                        "paid_in_amount": 600,
                        "ownership_pct": 60.0,
                        "subscription_date": "2020-01-15",
                    },
                    {
                        "name": "深圳投资有限公司",
                        "type": "法人",
                        "id_number": "91440300MA5XXXXXX",
                        "subscribed_amount": 400,
                        "paid_in_amount": 400,
                        "ownership_pct": 40.0,
                        "subscription_date": "2020-01-15",
                    },
                ],
                "actual_controller": {
                    "name": "张三",
                    "id_number": "110101199001011234",
                    "control_pct": 60.0,
                    "control_path": "直接持股60%",
                },
                "equity_pledges": [],
                "equity_changes": [],
            },
        }
    )


@pytest.fixture
def mock_llm_financial_notes():
    """MockLLMClient pre-loaded with financial notes response."""
    return MockLLMClient(
        responses={
            "附注": {
                "company_name": "北京示例科技股份有限公司",
                "fiscal_year_end": "2024-12-31",
                "accounting_policies": {
                    "revenue_recognition": "在客户取得相关商品控制权时确认收入",
                    "bad_debt_provision": "账龄分析法与个别认定法结合",
                    "depreciation_method": "直线法，房屋建筑物20年，设备5-10年",
                    "policy_changes": [],
                },
                "related_party_transactions": [
                    {
                        "party_name": "北京示例投资有限公司",
                        "relationship": "母公司",
                        "transaction_type": "采购",
                        "amount": 15000000.0,
                        "pricing_method": "市场价格",
                    },
                ],
                "contingent_liabilities": [
                    {
                        "type": "未决诉讼",
                        "description": "与供应商合同纠纷",
                        "amount": 5000000.0,
                        "probability": "可能",
                    },
                ],
                "pledged_assets": [
                    {
                        "asset_type": "房屋建筑物",
                        "book_value": 30000000.0,
                        "pledge_purpose": "借款担保",
                    },
                ],
                "significant_estimates": [
                    {
                        "item": "应收账款坏账准备",
                        "method": "预期信用损失模型",
                        "key_assumptions": "基于历史违约率和前瞻性信息",
                    },
                ],
                "subsequent_events": [],
            },
        }
    )


@pytest.fixture
def mock_llm_mda():
    """MockLLMClient pre-loaded with MD&A response."""
    return MockLLMClient(
        responses={
            "管理层讨论": {
                "company_name": "北京示例科技股份有限公司",
                "fiscal_year": "2024",
                "business_overview": {
                    "main_business": "企业级SaaS软件研发与销售",
                    "industry": "软件和信息技术服务业",
                    "business_model": "订阅制SaaS收费",
                    "core_competitiveness": "自主研发的AI中台技术",
                },
                "operating_results": {
                    "revenue_change_pct": 25.3,
                    "net_income_change_pct": 18.7,
                    "revenue_drivers": "新客户增长及存量客户续费率提升",
                    "cost_drivers": "研发人员扩招导致人力成本增加",
                    "gross_margin_change": "毛利率同比提升2.1个百分点至68.5%",
                },
                "industry_analysis": {
                    "industry_trends": "企业数字化转型加速，SaaS渗透率持续提升",
                    "competitive_landscape": "行业集中度较低，竞争格局分散",
                    "regulatory_environment": "数据安全法实施，合规成本增加",
                },
                "risk_factors": [
                    {
                        "category": "行业政策",
                        "description": "数据安全监管趋严可能影响产品功能",
                        "mitigation": "成立数据合规委员会，通过等保三级认证",
                    },
                    {
                        "category": "经营管理",
                        "description": "核心技术人员流失风险",
                        "mitigation": "股权激励计划覆盖核心团队",
                    },
                ],
                "future_outlook": {
                    "development_strategy": "深耕行业垂直场景，拓展海外市场",
                    "business_plan": "2025年目标收入增长20%以上",
                    "capex_plan": "计划投入5000万元建设新数据中心",
                    "rd_plan": "研发投入占收入比例维持在15%以上",
                },
                "major_events": [],
            },
        }
    )


@pytest.fixture
def mock_llm_guarantee():
    """MockLLMClient pre-loaded with guarantee disclosure response."""
    return MockLLMClient(
        responses={
            "对外担保": {
                "company_name": "北京示例科技股份有限公司",
                "report_date": "2024-12-31",
                "guarantee_summary": {
                    "total_guarantee_amount": 80000000.0,
                    "total_guarantee_to_net_assets_pct": 10.7,
                    "overdue_guarantee_amount": 0,
                    "guarantee_for_subsidiaries": 60000000.0,
                    "guarantee_for_shareholders": 0,
                    "guarantee_for_related_parties": 0,
                    "guarantee_for_others": 20000000.0,
                },
                "guarantee_details": [
                    {
                        "guaranteed_party": "北京示例云计算有限公司",
                        "relationship": "子公司",
                        "guarantee_amount": 60000000.0,
                        "guarantee_type": "连带责任保证",
                        "start_date": "2024-03-15",
                        "end_date": "2026-03-14",
                        "is_completed": False,
                        "is_overdue": False,
                        "counter_guarantee": None,
                    },
                ],
                "violation_guarantees": [],
            },
        }
    )


@pytest.fixture
def mock_llm_equity_changes():
    """MockLLMClient pre-loaded with equity changes statement response."""
    return MockLLMClient(
        responses={
            "权益变动表": {
                "company_name": "北京示例科技股份有限公司",
                "report_period": "2024-12-31",
                "currency": "CNY",
                "opening_balance": {
                    "share_capital": 500000000.0,
                    "capital_reserve": 200000000.0,
                    "other_comprehensive_income": -5000000.0,
                    "special_reserve": None,
                    "surplus_reserve": 50000000.0,
                    "retained_earnings": 300000000.0,
                    "total_equity_parent": 1045000000.0,
                    "minority_interest": 15000000.0,
                    "total_equity": 1060000000.0,
                },
                "changes": {
                    "net_income": 125000000.0,
                    "other_comprehensive_income_change": 3000000.0,
                    "total_comprehensive_income": 128000000.0,
                    "share_capital_increase": None,
                    "capital_reserve_increase": None,
                    "profit_distribution": {
                        "statutory_surplus_reserve": 12500000.0,
                        "discretionary_surplus_reserve": None,
                        "dividends_declared": 50000000.0,
                        "dividend_per_share": 0.10,
                    },
                    "share_based_payment": 8000000.0,
                    "other_equity_changes": None,
                },
                "closing_balance": {
                    "share_capital": 500000000.0,
                    "capital_reserve": 208000000.0,
                    "other_comprehensive_income": -2000000.0,
                    "special_reserve": None,
                    "surplus_reserve": 62500000.0,
                    "retained_earnings": 362500000.0,
                    "total_equity_parent": 1131000000.0,
                    "minority_interest": 17000000.0,
                    "total_equity": 1148000000.0,
                },
            },
        }
    )


@pytest.fixture
def mock_llm_license():
    """MockLLMClient pre-loaded with business license response."""
    return MockLLMClient(
        responses={
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
        }
    )


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

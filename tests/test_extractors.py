"""Tests for extractors — registry, base, and built-in extractors."""

from __future__ import annotations

from findocparser.extractors.generic import GenericExtractor
from findocparser.extractors.registry import get_extractor


class TestRegistry:
    """Test extractor registry and lookup."""

    def test_financial_statement_registered(self):
        ext = get_extractor("financial_statement")
        assert ext.doc_type == "financial_statement"

    def test_bank_statement_registered(self):
        ext = get_extractor("bank_statement")
        assert ext.doc_type == "bank_statement"

    def test_business_license_registered(self):
        ext = get_extractor("business_license")
        assert ext.doc_type == "business_license"

    def test_audit_report_registered(self):
        ext = get_extractor("audit_report")
        assert ext.doc_type == "audit_report"

    def test_credit_report_registered(self):
        ext = get_extractor("credit_report")
        assert ext.doc_type == "credit_report"

    def test_shareholder_info_registered(self):
        ext = get_extractor("shareholder_info")
        assert ext.doc_type == "shareholder_info"

    def test_financial_notes_registered(self):
        ext = get_extractor("financial_notes")
        assert ext.doc_type == "financial_notes"

    def test_md_and_a_registered(self):
        ext = get_extractor("md_and_a")
        assert ext.doc_type == "md_and_a"

    def test_guarantee_registered(self):
        ext = get_extractor("guarantee")
        assert ext.doc_type == "guarantee"

    def test_equity_changes_stmt_registered(self):
        ext = get_extractor("equity_changes_stmt")
        assert ext.doc_type == "equity_changes_stmt"

    def test_unknown_falls_back_to_generic(self):
        ext = get_extractor("nonexistent_type")
        assert isinstance(ext, GenericExtractor)
        assert ext.doc_type == "generic"


class TestExtractorOutput:
    """Test that extractors produce correct output with mock LLM."""

    async def test_financial_statement_extract(self, mock_llm_financial):
        ext = get_extractor("financial_statement")
        result = await ext.extract("财务报表内容...", mock_llm_financial)
        assert result["balance_sheet"]["total_assets"] == 125000000.0
        assert result["income_statement"]["revenue"] == 200000000.0
        assert mock_llm_financial.call_count == 1

    async def test_bank_statement_extract(self, mock_llm_bank):
        ext = get_extractor("bank_statement")
        result = await ext.extract("银行流水内容...", mock_llm_bank)
        assert result["account_name"] == "某某公司"
        assert len(result["transactions"]) == 2
        assert result["transactions"][0]["amount"] == -50000.0

    async def test_business_license_extract(self, mock_llm_license):
        ext = get_extractor("business_license")
        result = await ext.extract("营业执照内容...", mock_llm_license)
        assert result["company_name"] == "北京示例科技有限公司"
        assert result["unified_social_credit_code"] == "91110108MA01XXXXX"

    async def test_audit_report_extract(self, mock_llm_audit):
        ext = get_extractor("audit_report")
        result = await ext.extract("审计报告内容...", mock_llm_audit)
        assert result["audit_firm"] == "普华永道中天会计师事务所"
        assert result["opinion_type"] == "标准无保留意见"
        assert result["going_concern"]["has_uncertainty"] is False
        assert len(result["key_audit_matters"]) == 2
        assert result["key_audit_matters"][0]["title"] == "收入确认"
        assert result["emphasis_of_matter"] == []
        assert len(result["signatories"]) == 2
        assert mock_llm_audit.call_count == 1

    async def test_credit_report_extract(self, mock_llm_credit):
        ext = get_extractor("credit_report")
        result = await ext.extract("征信报告内容...", mock_llm_credit)
        assert result["company_name"] == "北京示例科技有限公司"
        assert result["credit_score"] == 720
        assert result["credit_level"] == "AA"
        assert result["outstanding_loans"]["overdue_count"] == 1
        assert result["outstanding_loans"]["overdue_amount"] == 200000.0
        assert len(result["overdue_records"]) == 1
        assert result["overdue_records"][0]["overdue_days"] == 30
        assert result["credit_cards"]["total_count"] == 2
        assert result["guarantees"]["total_amount"] == 1000000.0
        assert len(result["query_records"]) == 1
        assert result["public_records"]["tax_arrears"] == 0
        assert mock_llm_credit.call_count == 1

    async def test_shareholder_info_extract(self, mock_llm_shareholder):
        ext = get_extractor("shareholder_info")
        result = await ext.extract("股东信息内容...", mock_llm_shareholder)
        assert result["company_name"] == "北京示例科技有限公司"
        assert len(result["shareholders"]) == 2
        assert result["shareholders"][0]["name"] == "张三"
        assert result["shareholders"][0]["ownership_pct"] == 60.0
        assert result["actual_controller"]["name"] == "张三"
        assert result["actual_controller"]["control_pct"] == 60.0
        assert result["equity_pledges"] == []
        assert result["equity_changes"] == []
        assert mock_llm_shareholder.call_count == 1

    async def test_financial_notes_extract(self, mock_llm_financial_notes):
        ext = get_extractor("financial_notes")
        result = await ext.extract("附注内容...", mock_llm_financial_notes)
        assert result["company_name"] == "北京示例科技股份有限公司"
        assert len(result["related_party_transactions"]) == 1
        assert result["related_party_transactions"][0]["amount"] == 15000000.0
        assert len(result["contingent_liabilities"]) == 1
        assert result["contingent_liabilities"][0]["probability"] == "可能"
        assert len(result["pledged_assets"]) == 1
        assert result["subsequent_events"] == []
        assert mock_llm_financial_notes.call_count == 1

    async def test_md_and_a_extract(self, mock_llm_mda):
        ext = get_extractor("md_and_a")
        result = await ext.extract("管理层讨论与分析...", mock_llm_mda)
        assert result["company_name"] == "北京示例科技股份有限公司"
        assert result["operating_results"]["revenue_change_pct"] == 25.3
        assert result["operating_results"]["net_income_change_pct"] == 18.7
        assert len(result["risk_factors"]) == 2
        assert result["risk_factors"][0]["category"] == "行业政策"
        assert result["future_outlook"]["capex_plan"] is not None
        assert mock_llm_mda.call_count == 1

    async def test_guarantee_extract(self, mock_llm_guarantee):
        ext = get_extractor("guarantee")
        result = await ext.extract("对外担保信息...", mock_llm_guarantee)
        assert result["company_name"] == "北京示例科技股份有限公司"
        assert result["guarantee_summary"]["total_guarantee_amount"] == 80000000.0
        assert result["guarantee_summary"]["total_guarantee_to_net_assets_pct"] == 10.7
        assert len(result["guarantee_details"]) == 1
        assert result["guarantee_details"][0]["guarantee_type"] == "连带责任保证"
        assert result["violation_guarantees"] == []
        assert mock_llm_guarantee.call_count == 1

    async def test_equity_changes_stmt_extract(self, mock_llm_equity_changes):
        ext = get_extractor("equity_changes_stmt")
        result = await ext.extract("权益变动表内容...", mock_llm_equity_changes)
        assert result["company_name"] == "北京示例科技股份有限公司"
        assert result["opening_balance"]["total_equity"] == 1060000000.0
        assert result["changes"]["net_income"] == 125000000.0
        assert result["changes"]["profit_distribution"]["dividends_declared"] == 50000000.0
        assert result["closing_balance"]["total_equity"] == 1148000000.0
        assert mock_llm_equity_changes.call_count == 1

    async def test_generic_extract(self, mock_llm):
        ext = get_extractor("generic")
        client = mock_llm()
        result = await ext.extract("一些未知文档内容", client)
        assert "summary" in result or "document_type" in result

    async def test_content_truncation(self, mock_llm):
        """Content exceeding max_content_chars should be truncated."""
        ext = get_extractor("generic")
        client = mock_llm()
        big_content = "A" * 100_000
        await ext.extract(big_content, client, max_content_chars=1000)
        # Verify the prompt was truncated
        assert len(client.last_prompt) < 100_000
        assert "[... content truncated ...]" in client.last_prompt


class TestPromptTemplate:
    """Test that prompt templates contain expected placeholders."""

    def test_financial_has_content_placeholder(self):
        ext = get_extractor("financial_statement")
        assert "{content}" in ext.prompt_template

    def test_bank_has_content_placeholder(self):
        ext = get_extractor("bank_statement")
        assert "{content}" in ext.prompt_template

    def test_license_has_content_placeholder(self):
        ext = get_extractor("business_license")
        assert "{content}" in ext.prompt_template

    def test_audit_report_has_content_placeholder(self):
        ext = get_extractor("audit_report")
        assert "{content}" in ext.prompt_template

    def test_credit_report_has_content_placeholder(self):
        ext = get_extractor("credit_report")
        assert "{content}" in ext.prompt_template

    def test_shareholder_has_content_placeholder(self):
        ext = get_extractor("shareholder_info")
        assert "{content}" in ext.prompt_template

    def test_generic_has_content_placeholder(self):
        ext = get_extractor("generic")
        assert "{content}" in ext.prompt_template

    def test_financial_notes_has_content_placeholder(self):
        ext = get_extractor("financial_notes")
        assert "{content}" in ext.prompt_template

    def test_md_and_a_has_content_placeholder(self):
        ext = get_extractor("md_and_a")
        assert "{content}" in ext.prompt_template

    def test_guarantee_has_content_placeholder(self):
        ext = get_extractor("guarantee")
        assert "{content}" in ext.prompt_template

    def test_equity_changes_has_content_placeholder(self):
        ext = get_extractor("equity_changes_stmt")
        assert "{content}" in ext.prompt_template

    def test_prompt_renders_without_error(self):
        """All extractors' prompts should render with content= kwarg."""
        for doc_type in [
            "financial_statement",
            "bank_statement",
            "business_license",
            "audit_report",
            "credit_report",
            "shareholder_info",
            "financial_notes",
            "md_and_a",
            "guarantee",
            "equity_changes_stmt",
            "generic",
        ]:
            ext = get_extractor(doc_type)
            rendered = ext.prompt_template.format(content="test content 123")
            assert "test content 123" in rendered

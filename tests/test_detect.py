"""Tests for file/document type detection."""

from pathlib import Path

from findocparser.detect import detect_doc_type, detect_file_type


class TestDetectFileType:
    def test_pdf(self):
        assert detect_file_type(Path("test.pdf")) == "pdf"

    def test_xlsx(self):
        assert detect_file_type(Path("test.xlsx")) == "excel"

    def test_xls(self):
        assert detect_file_type(Path("test.xls")) == "excel"

    def test_csv(self):
        assert detect_file_type(Path("test.csv")) == "excel"

    def test_jpg(self):
        assert detect_file_type(Path("test.jpg")) == "image"

    def test_png(self):
        assert detect_file_type(Path("test.png")) == "image"

    def test_unsupported(self):
        import pytest

        with pytest.raises(ValueError):
            detect_file_type(Path("test.docx"))


class TestDetectDocType:
    def test_financial_statement_by_filename(self):
        assert detect_doc_type("", "资产负债表2024.pdf") == "financial_statement"

    def test_bank_statement_by_filename(self):
        assert detect_doc_type("", "银行流水_2024.pdf") == "bank_statement"

    def test_business_license_by_filename(self):
        assert detect_doc_type("", "营业执照.jpg") == "business_license"

    def test_audit_report_by_filename(self):
        assert detect_doc_type("", "审计报告2024.pdf") == "audit_report"

    def test_audit_report_by_content(self):
        content = "审计意见：我们认为，财务报表在所有重大方面按照企业会计准则..."
        assert detect_doc_type(content, "report.pdf") == "audit_report"

    def test_generic_fallback(self):
        assert detect_doc_type("some random content", "unknown.pdf") == "generic"

    def test_detect_by_content(self):
        content = "发票代码：1234 发票号码：5678 金额：1000"
        assert detect_doc_type(content, "doc.pdf") == "tax_invoice"

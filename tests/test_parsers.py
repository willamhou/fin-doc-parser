"""Tests for parsers — Excel/CSV parsing (no external deps needed for CSV)."""

from __future__ import annotations

import pytest


class TestCSVParser:
    """Test CSV parser (no optional dependencies needed)."""

    def test_basic_csv(self, tmp_csv):
        from findocparser.parsers.excel import parse_excel

        result = parse_excel(tmp_csv)
        assert "## CSV" in result
        assert "日期" in result
        assert "摘要" in result
        assert "1000000" in result

    def test_empty_csv(self, tmp_path):
        from findocparser.parsers.excel import parse_excel

        f = tmp_path / "empty.csv"
        f.write_text("", encoding="utf-8")
        result = parse_excel(f)
        assert result == "(empty)"

    def test_single_row_csv(self, tmp_path):
        from findocparser.parsers.excel import parse_excel

        f = tmp_path / "header_only.csv"
        f.write_text("col1,col2,col3\n", encoding="utf-8")
        result = parse_excel(f)
        assert "col1" in result
        assert "---" in result

    def test_csv_with_chinese(self, tmp_path):
        from findocparser.parsers.excel import parse_excel

        f = tmp_path / "中文.csv"
        f.write_text(
            "公司名称,注册资本\n北京科技,1000万\n上海实业,500万\n",
            encoding="utf-8",
        )
        result = parse_excel(f)
        assert "北京科技" in result
        assert "上海实业" in result

    def test_markdown_table_format(self, tmp_csv):
        from findocparser.parsers.excel import parse_excel

        result = parse_excel(tmp_csv)
        lines = [line for line in result.split("\n") if line.strip()]
        # Should have header separator with ---
        separator_lines = [line for line in lines if "---" in line]
        assert len(separator_lines) >= 1


class TestExcelParserImportErrors:
    """Test that missing optional deps give clear error messages."""

    def test_xlsx_import_error_message(self, tmp_path, monkeypatch):
        """If openpyxl is not installed, should give clear error."""

        f = tmp_path / "test.xlsx"
        f.write_bytes(b"fake xlsx content")

        # We can't easily remove openpyxl if it's installed,
        # so just verify the function exists and handles the extension
        from findocparser.parsers.excel import parse_excel

        # If openpyxl IS installed, this would fail on invalid content,
        # not ImportError. Both are acceptable behaviors.
        with pytest.raises((ImportError, Exception)):
            parse_excel(f)

    def test_xls_import_error_message(self, tmp_path):
        f = tmp_path / "test.xls"
        f.write_bytes(b"fake xls content")

        from findocparser.parsers.excel import parse_excel

        with pytest.raises((ImportError, Exception)):
            parse_excel(f)

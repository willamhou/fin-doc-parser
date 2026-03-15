"""Tests for the full pipeline — with mock LLM, no real API calls."""

from __future__ import annotations

import pytest


class TestPipelineWithCSV:
    """Test pipeline end-to-end with CSV file + mock LLM."""

    async def test_csv_auto_detect(self, tmp_csv, mock_llm):
        from findocparser.api import parse_async

        client = mock_llm(responses={
            "金融文档": {
                "document_type": "financial_data",
                "summary": "CSV financial data",
            },
        })

        result = await parse_async(
            tmp_csv,
            llm_client=client,
        )
        assert result["file_type"] == "excel"
        assert result["file_name"] == "test_data.csv"
        assert result["doc_type"] == "generic"  # no keywords in filename
        assert "data" in result
        assert client.call_count == 1

    async def test_csv_explicit_doc_type(self, tmp_csv, mock_llm):
        from findocparser.api import parse_async

        client = mock_llm(responses={
            "银行流水": {
                "transactions": [{"date": "2024-01-01", "amount": 100}],
            },
        })

        result = await parse_async(
            tmp_csv,
            doc_type="bank_statement",
            llm_client=client,
        )
        assert result["doc_type"] == "bank_statement"
        assert result["data"]["transactions"][0]["amount"] == 100

    async def test_csv_with_financial_filename(self, tmp_path, mock_llm):
        """CSV with Chinese financial keyword in name → auto-detect."""
        from findocparser.api import parse_async

        csv_file = tmp_path / "资产负债表_2024.csv"
        csv_file.write_text("项目,金额\n总资产,100\n", encoding="utf-8")

        client = mock_llm(responses={
            "财务报表": {"total_assets": 100},
        })

        result = await parse_async(csv_file, llm_client=client)
        assert result["doc_type"] == "financial_statement"


class TestPipelineFileNotFound:
    """Test pipeline error handling."""

    async def test_missing_file(self, mock_llm):
        from findocparser.api import parse_async

        with pytest.raises(FileNotFoundError):
            await parse_async(
                "/nonexistent/path/file.pdf",
                llm_client=mock_llm(),
            )

    async def test_unsupported_extension(self, tmp_path, mock_llm):
        from findocparser.api import parse_async

        docx = tmp_path / "test.docx"
        docx.write_text("test")
        with pytest.raises(ValueError, match="Unsupported file type"):
            await parse_async(docx, llm_client=mock_llm())

    async def test_parse_sync_in_async_context_raises(self, tmp_csv, mock_llm):
        """parse() should raise RuntimeError when called from async context."""
        from findocparser.api import parse

        with pytest.raises(RuntimeError, match="cannot be called from an async context"):
            parse(tmp_csv, llm_client=mock_llm())


class TestPipelineReturnShape:
    """Verify the shape of pipeline return value."""

    async def test_return_has_required_keys(self, tmp_csv, mock_llm):
        from findocparser.api import parse_async

        result = await parse_async(tmp_csv, llm_client=mock_llm())
        assert set(result.keys()) == {"doc_type", "file_name", "file_type", "data"}

    async def test_return_types(self, tmp_csv, mock_llm):
        from findocparser.api import parse_async

        result = await parse_async(tmp_csv, llm_client=mock_llm())
        assert isinstance(result["doc_type"], str)
        assert isinstance(result["file_name"], str)
        assert isinstance(result["file_type"], str)
        assert isinstance(result["data"], dict)

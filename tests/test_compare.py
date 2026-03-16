"""Tests for multi-period comparison."""

from __future__ import annotations

import pytest

from findocparser.compare import compare_periods


def _make_result(doc_type: str, data: dict, period: str = "2024-12-31") -> dict:
    """Helper to build a parse() result dict."""
    data.setdefault("report_period", period)
    return {"doc_type": doc_type, "file_name": "test.pdf", "file_type": "pdf", "data": data}


class TestComparePeriodsValidation:
    def test_requires_at_least_two_results(self):
        with pytest.raises(ValueError, match="at least 2"):
            compare_periods([_make_result("financial_statement", {})])

    def test_rejects_empty_list(self):
        with pytest.raises(ValueError, match="at least 2"):
            compare_periods([])

    def test_rejects_mismatched_doc_types(self):
        r1 = _make_result("financial_statement", {}, "2023-12-31")
        r2 = _make_result("bank_statement", {}, "2024-12-31")
        with pytest.raises(ValueError, match="same doc_type"):
            compare_periods([r1, r2])


class TestComparePeriodsOutput:
    def test_basic_structure(self):
        r1 = _make_result("financial_statement", {"revenue": 100}, "2023-12-31")
        r2 = _make_result("financial_statement", {"revenue": 120}, "2024-12-31")
        result = compare_periods([r1, r2])

        assert result["doc_type"] == "financial_statement"
        assert result["period_count"] == 2
        assert result["periods"] == ["2023-12-31", "2024-12-31"]
        assert len(result["comparisons"]) == 1

    def test_numeric_change(self):
        r1 = _make_result(
            "financial_statement",
            {
                "balance_sheet": {"total_assets": 100_000_000},
            },
            "2023-12-31",
        )
        r2 = _make_result(
            "financial_statement",
            {
                "balance_sheet": {"total_assets": 125_000_000},
            },
            "2024-12-31",
        )
        result = compare_periods([r1, r2])

        assets = result["comparisons"][0]["balance_sheet"]["total_assets"]
        assert assets["previous"] == 100_000_000
        assert assets["current"] == 125_000_000
        assert assets["change"] == 25_000_000
        assert assets["change_pct"] == 25.0

    def test_negative_change(self):
        r1 = _make_result("financial_statement", {"revenue": 200_000_000}, "2023")
        r2 = _make_result("financial_statement", {"revenue": 160_000_000}, "2024")
        result = compare_periods([r1, r2])

        revenue = result["comparisons"][0]["revenue"]
        assert revenue["change"] == -40_000_000
        assert revenue["change_pct"] == -20.0

    def test_zero_base_no_pct(self):
        r1 = _make_result("financial_statement", {"val": 0}, "2023")
        r2 = _make_result("financial_statement", {"val": 100}, "2024")
        result = compare_periods([r1, r2])

        val = result["comparisons"][0]["val"]
        assert val["change"] == 100
        assert val["change_pct"] is None

    def test_null_previous(self):
        r1 = _make_result("financial_statement", {"val": None}, "2023")
        r2 = _make_result("financial_statement", {"val": 500}, "2024")
        result = compare_periods([r1, r2])

        val = result["comparisons"][0]["val"]
        assert val["previous"] is None
        assert val["current"] == 500
        assert val["change"] is None

    def test_null_current(self):
        r1 = _make_result("financial_statement", {"val": 500}, "2023")
        r2 = _make_result("financial_statement", {"val": None}, "2024")
        result = compare_periods([r1, r2])

        val = result["comparisons"][0]["val"]
        assert val["previous"] == 500
        assert val["current"] is None

    def test_nested_dict_comparison(self):
        r1 = _make_result(
            "financial_statement",
            {
                "balance_sheet": {"total_assets": 100, "total_liabilities": 60},
                "income_statement": {"revenue": 200, "net_income": 30},
            },
            "2023",
        )
        r2 = _make_result(
            "financial_statement",
            {
                "balance_sheet": {"total_assets": 130, "total_liabilities": 70},
                "income_statement": {"revenue": 250, "net_income": 45},
            },
            "2024",
        )
        result = compare_periods([r1, r2])
        comp = result["comparisons"][0]

        assert comp["balance_sheet"]["total_assets"]["change"] == 30
        assert comp["income_statement"]["revenue"]["change"] == 50
        assert comp["income_statement"]["net_income"]["change_pct"] == 50.0

    def test_list_fields_show_counts(self):
        r1 = _make_result(
            "bank_statement",
            {
                "transactions": [{"amount": 100}, {"amount": 200}],
            },
            "2023",
        )
        r2 = _make_result(
            "bank_statement",
            {
                "transactions": [{"amount": 100}, {"amount": 200}, {"amount": 300}],
            },
            "2024",
        )
        result = compare_periods([r1, r2])

        txn = result["comparisons"][0]["transactions"]
        assert txn["previous_count"] == 2
        assert txn["current_count"] == 3

    def test_string_change_shown(self):
        r1 = _make_result("audit_report", {"opinion_type": "标准无保留意见"}, "2023")
        r2 = _make_result("audit_report", {"opinion_type": "保留意见"}, "2024")
        result = compare_periods([r1, r2])

        opinion = result["comparisons"][0]["opinion_type"]
        assert opinion["previous"] == "标准无保留意见"
        assert opinion["current"] == "保留意见"

    def test_same_string_not_in_output(self):
        r1 = _make_result("financial_statement", {"currency": "CNY"}, "2023")
        r2 = _make_result("financial_statement", {"currency": "CNY"}, "2024")
        result = compare_periods([r1, r2])
        assert "currency" not in result["comparisons"][0]


class TestSignificantChanges:
    def test_flags_above_threshold(self):
        r1 = _make_result(
            "financial_statement",
            {
                "balance_sheet": {"total_assets": 100, "inventory": 50},
            },
            "2023",
        )
        r2 = _make_result(
            "financial_statement",
            {
                "balance_sheet": {"total_assets": 105, "inventory": 80},
            },
            "2024",
        )
        result = compare_periods([r1, r2], significant_change_pct=20.0)

        sig = result["significant_changes"]
        fields = [s["field"] for s in sig]
        # inventory +60% should be flagged, total_assets +5% should not
        assert "balance_sheet.inventory" in fields
        assert "balance_sheet.total_assets" not in fields

    def test_custom_threshold(self):
        r1 = _make_result("financial_statement", {"revenue": 100}, "2023")
        r2 = _make_result("financial_statement", {"revenue": 110}, "2024")

        # 10% change, threshold 5% → flagged
        result = compare_periods([r1, r2], significant_change_pct=5.0)
        assert len(result["significant_changes"]) >= 1

        # 10% change, threshold 15% → not flagged
        result = compare_periods([r1, r2], significant_change_pct=15.0)
        sig_fields = [s["field"] for s in result["significant_changes"]]
        assert "revenue" not in sig_fields

    def test_negative_change_flagged(self):
        r1 = _make_result("financial_statement", {"net_income": 100}, "2023")
        r2 = _make_result("financial_statement", {"net_income": 50}, "2024")
        result = compare_periods([r1, r2])

        sig = result["significant_changes"]
        assert any(s["field"] == "net_income" and s["change_pct"] == -50.0 for s in sig)


class TestThreePeriods:
    def test_three_period_comparison(self):
        r1 = _make_result("financial_statement", {"revenue": 100}, "2022")
        r2 = _make_result("financial_statement", {"revenue": 120}, "2023")
        r3 = _make_result("financial_statement", {"revenue": 150}, "2024")
        result = compare_periods([r1, r2, r3])

        assert result["period_count"] == 3
        assert len(result["comparisons"]) == 2
        assert result["comparisons"][0]["from_period"] == "2022"
        assert result["comparisons"][0]["to_period"] == "2023"
        assert result["comparisons"][1]["from_period"] == "2023"
        assert result["comparisons"][1]["to_period"] == "2024"

        assert result["comparisons"][0]["revenue"]["change_pct"] == 20.0
        assert result["comparisons"][1]["revenue"]["change_pct"] == 25.0

    def test_missing_period_label_uses_index(self):
        r1 = {"doc_type": "financial_statement", "data": {"revenue": 100}}
        r2 = {"doc_type": "financial_statement", "data": {"revenue": 120}}
        result = compare_periods([r1, r2])
        assert result["periods"] == ["period_0", "period_1"]

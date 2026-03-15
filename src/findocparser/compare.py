"""Multi-period comparison for financial documents.

Compare parse() results across reporting periods to compute
period-over-period changes, growth rates, and trend flags.
"""

from __future__ import annotations

from typing import Any


def compare_periods(
    results: list[dict[str, Any]],
    *,
    significant_change_pct: float = 20.0,
) -> dict[str, Any]:
    """Compare parse() results across multiple reporting periods.

    Takes a list of ``parse()`` return dicts (same ``doc_type``), ordered
    from **earliest to latest**, and produces a comparison with absolute
    and percentage changes between consecutive periods.

    Args:
        results: List of parse() results, ordered earliest → latest.
            Each must have ``doc_type`` and ``data`` keys.
        significant_change_pct: Threshold (%) for flagging significant changes.
            Defaults to 20.0 (i.e., ±20% change is flagged).

    Returns:
        Dict with ``doc_type``, ``period_count``, ``periods`` (list of
        period labels), ``comparisons`` (list of pairwise diffs), and
        ``significant_changes`` (list of flagged items).

    Raises:
        ValueError: If fewer than 2 results, or doc_type mismatch.

    Example::

        r2023 = parse("财务报表2023.pdf")
        r2024 = parse("财务报表2024.pdf")
        diff = compare_periods([r2023, r2024])
        print(diff["comparisons"][0]["balance_sheet"]["total_assets"])
        # {"previous": 100000000, "current": 125000000,
        #  "change": 25000000, "change_pct": 25.0}
    """
    if len(results) < 2:
        raise ValueError("compare_periods requires at least 2 results")

    doc_types = {r.get("doc_type") for r in results}
    if len(doc_types) > 1:
        raise ValueError(f"All results must have the same doc_type, got: {doc_types}")

    doc_type = results[0]["doc_type"]
    periods = [r["data"].get("report_period", f"period_{i}") for i, r in enumerate(results)]

    comparisons = []
    significant_changes: list[dict[str, Any]] = []

    for i in range(1, len(results)):
        prev_data = results[i - 1]["data"]
        curr_data = results[i]["data"]
        diff = _diff_dicts(prev_data, curr_data)
        comparisons.append({
            "from_period": periods[i - 1],
            "to_period": periods[i],
            **diff,
        })

        # Collect significant changes
        _collect_significant(
            diff,
            path_prefix="",
            threshold=significant_change_pct,
            from_period=periods[i - 1],
            to_period=periods[i],
            out=significant_changes,
        )

    return {
        "doc_type": doc_type,
        "period_count": len(results),
        "periods": periods,
        "comparisons": comparisons,
        "significant_changes": significant_changes,
    }


def _diff_dicts(
    prev: dict[str, Any],
    curr: dict[str, Any],
) -> dict[str, Any]:
    """Recursively diff two data dicts, computing changes for numeric fields."""
    result: dict[str, Any] = {}
    all_keys = set(prev.keys()) | set(curr.keys())

    for key in sorted(all_keys):
        pv = prev.get(key)
        cv = curr.get(key)

        # Both are dicts → recurse
        if isinstance(pv, dict) and isinstance(cv, dict):
            result[key] = _diff_dicts(pv, cv)
        # Both are numeric → compute change
        elif _is_numeric(pv) and _is_numeric(cv):
            result[key] = _numeric_change(pv, cv)
        # One is numeric, other is None → partial comparison
        elif _is_numeric(pv) and cv is None:
            result[key] = {"previous": pv, "current": None, "change": None, "change_pct": None}
        elif pv is None and _is_numeric(cv):
            result[key] = {"previous": None, "current": cv, "change": None, "change_pct": None}
        # Both are lists → store as-is (transactions, shareholders, etc.)
        elif isinstance(pv, list) and isinstance(cv, list):
            result[key] = {"previous_count": len(pv), "current_count": len(cv)}
        # String fields → show both if different
        elif pv != cv:
            result[key] = {"previous": pv, "current": cv}
        # Same non-numeric value → skip to keep output clean
    return result


def _numeric_change(prev: float | int, curr: float | int) -> dict[str, Any]:
    """Compute absolute and percentage change between two numbers."""
    change = curr - prev
    if prev != 0:
        change_pct = round(change / abs(prev) * 100, 2)
    else:
        change_pct = None  # Can't compute % from zero base
    return {
        "previous": prev,
        "current": curr,
        "change": round(change, 2) if isinstance(change, float) else change,
        "change_pct": change_pct,
    }


def _is_numeric(value: Any) -> bool:
    """Check if value is a number (int or float), excluding None and bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _collect_significant(
    diff: dict[str, Any],
    *,
    path_prefix: str,
    threshold: float,
    from_period: str,
    to_period: str,
    out: list[dict[str, Any]],
) -> None:
    """Walk diff tree and collect entries where |change_pct| >= threshold."""
    for key, value in diff.items():
        path = f"{path_prefix}.{key}" if path_prefix else key

        if isinstance(value, dict):
            if "change_pct" in value and value["change_pct"] is not None:
                if abs(value["change_pct"]) >= threshold:
                    out.append({
                        "field": path,
                        "from_period": from_period,
                        "to_period": to_period,
                        **value,
                    })
            else:
                # Nested dict without change_pct → recurse
                _collect_significant(
                    value,
                    path_prefix=path,
                    threshold=threshold,
                    from_period=from_period,
                    to_period=to_period,
                    out=out,
                )

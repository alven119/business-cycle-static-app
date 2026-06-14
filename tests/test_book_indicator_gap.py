from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    BookIndicatorGapAnalysisError,
    high_priority_book_gap_count,
    load_book_indicator_gap_analysis,
    sensitivity_issues,
    validate_book_indicator_gap_analysis,
)

SPEC_PATH = Path("specs/backtests/book_indicator_gap_analysis.yaml")


def test_book_indicator_gap_analysis_yaml_can_be_loaded() -> None:
    analysis = load_book_indicator_gap_analysis(SPEC_PATH)

    assert analysis.version == 1
    assert analysis.status == "draft"
    assert len(analysis.book_aligned_indicator_groups) > 0
    validate_book_indicator_gap_analysis(analysis)


def test_book_indicator_gap_analysis_contains_high_priority_items() -> None:
    analysis = load_book_indicator_gap_analysis(SPEC_PATH)
    groups = {group["group_id"]: group for group in analysis.book_aligned_indicator_groups}
    recommendations = {item["recommendation_id"]: item for item in analysis.priority_recommendations}

    assert groups["boom_ending_indicators"]["implementation_priority"] == "high"
    assert groups["recession_confirmation_indicators"]["implementation_priority"] == "high"
    assert recommendations["phase_7e_breadth_confirmation"]["priority"] == "high"
    assert high_priority_book_gap_count(analysis) >= 3


def test_book_indicator_gap_analysis_sensitivity_issues() -> None:
    analysis = load_book_indicator_gap_analysis(SPEC_PATH)
    issue_ids = {issue["indicator_id"] for issue in sensitivity_issues(analysis)}

    assert "short_term_unemployment" in issue_ids
    assert "real_pce_durable_goods" in issue_ids
    assert "initial_jobless_claims" in issue_ids
    assert "real_retail_sales" in issue_ids


def test_book_indicator_gap_analysis_contains_required_caveats() -> None:
    analysis = load_book_indicator_gap_analysis(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in analysis.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in analysis.caveats_zh)


def test_book_indicator_gap_duplicate_sensitivity_issue_raises(tmp_path: Path) -> None:
    path = tmp_path / "book_indicator_gap_analysis.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "indicator_id: real_retail_sales",
        "indicator_id: initial_jobless_claims",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(BookIndicatorGapAnalysisError, match="duplicate indicator_id"):
        load_book_indicator_gap_analysis(path)


def test_book_indicator_gap_invalid_priority_raises(tmp_path: Path) -> None:
    path = tmp_path / "book_indicator_gap_analysis.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "implementation_priority: high",
        "implementation_priority: urgent",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(BookIndicatorGapAnalysisError, match="implementation_priority"):
        load_book_indicator_gap_analysis(path)

from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    BookAlignedIndicatorImplementationPlanError,
    high_priority_indicator_count,
    load_book_aligned_indicator_implementation_plan,
    purpose_groups,
    validate_book_aligned_indicator_implementation_plan,
)

SPEC_PATH = Path("specs/backtests/book_aligned_indicator_implementation_plan.yaml")


def test_book_aligned_indicator_plan_yaml_can_be_loaded() -> None:
    plan = load_book_aligned_indicator_implementation_plan(SPEC_PATH)

    assert plan.version == 1
    assert plan.status == "draft"
    assert len(plan.candidate_indicators) > 0
    validate_book_aligned_indicator_implementation_plan(plan)


def test_book_aligned_indicator_plan_has_high_priority_candidates() -> None:
    plan = load_book_aligned_indicator_implementation_plan(SPEC_PATH)
    high_priority_ids = {
        item["indicator_id"]
        for item in plan.candidate_indicators
        if item.get("implementation_priority") == "high"
    }

    assert high_priority_indicator_count(plan) > 0
    assert "continuing_jobless_claims" in high_priority_ids
    assert "credit_spread_baa_aaa" in high_priority_ids
    assert "yield_curve_10y_3m" in high_priority_ids


def test_book_aligned_indicator_plan_candidate_ids_are_unique() -> None:
    plan = load_book_aligned_indicator_implementation_plan(SPEC_PATH)
    indicator_ids = [item["indicator_id"] for item in plan.candidate_indicators]

    assert len(indicator_ids) == len(set(indicator_ids))


def test_book_aligned_indicator_plan_contains_required_batches() -> None:
    plan = load_book_aligned_indicator_implementation_plan(SPEC_PATH)
    batch_ids = {item["batch_id"] for item in plan.implementation_batches}
    groups = set(purpose_groups(plan))

    assert "phase_7f1_recession_confirmation_indicators" in batch_ids
    assert "phase_7f2_boom_ending_indicators" in batch_ids
    assert "phase_7f3_recession_trough_recovery_indicators" in batch_ids
    assert "recession_confirmation" in groups
    assert "boom_ending" in groups
    assert "recession_trough_recovery" in groups


def test_book_aligned_indicator_plan_contains_required_caveats() -> None:
    plan = load_book_aligned_indicator_implementation_plan(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in plan.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in plan.caveats_zh)


def test_book_aligned_indicator_plan_duplicate_indicator_raises(tmp_path: Path) -> None:
    path = tmp_path / "book_aligned_indicator_implementation_plan.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "indicator_id: insured_unemployment_rate",
        "indicator_id: continuing_jobless_claims",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(BookAlignedIndicatorImplementationPlanError, match="duplicate indicator_id"):
        load_book_aligned_indicator_implementation_plan(path)


def test_book_aligned_indicator_plan_invalid_priority_raises(tmp_path: Path) -> None:
    path = tmp_path / "book_aligned_indicator_implementation_plan.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "implementation_priority: high",
        "implementation_priority: urgent",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(BookAlignedIndicatorImplementationPlanError, match="implementation_priority"):
        load_book_aligned_indicator_implementation_plan(path)

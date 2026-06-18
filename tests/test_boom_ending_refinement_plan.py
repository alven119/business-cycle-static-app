from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    load_boom_ending_refinement_plan,
    validate_boom_ending_refinement_plan,
)

PLAN_PATH = Path("specs/backtests/boom_ending_refinement_plan.yaml")


def test_boom_ending_refinement_plan_can_be_loaded() -> None:
    plan = load_boom_ending_refinement_plan(PLAN_PATH)

    assert plan.version == 1
    assert plan.status == "draft"
    assert len(plan.diagnosed_issues) > 0
    assert len(plan.proposed_refinements) > 0
    validate_boom_ending_refinement_plan(plan)


def test_boom_ending_refinement_plan_recommends_7f23() -> None:
    plan = load_boom_ending_refinement_plan(PLAN_PATH)

    assert plan.recommended_next_phase["phase_id"] == "7F2.3"


def test_boom_ending_refinement_plan_contains_required_refinements() -> None:
    plan = load_boom_ending_refinement_plan(PLAN_PATH)
    refinement_ids = {item["refinement_id"] for item in plan.proposed_refinements}

    assert "replace_or_compare_credit_spread_baa_10y" in refinement_ids
    assert "yield_curve_lead_time_pressure" in refinement_ids


def test_boom_ending_refinement_plan_contains_required_caveats() -> None:
    plan = load_boom_ending_refinement_plan(PLAN_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in plan.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in plan.caveats_zh)

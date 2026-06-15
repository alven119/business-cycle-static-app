from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    load_boom_ending_candidate_indicators,
    validate_boom_ending_candidate_indicators,
)

SPEC_PATH = Path("specs/backtests/boom_ending_candidate_indicators.yaml")


def test_boom_ending_candidate_yaml_can_be_loaded() -> None:
    spec = load_boom_ending_candidate_indicators(SPEC_PATH)

    assert spec.version == 1
    assert spec.status == "draft"
    assert len(spec.indicators) == 8
    validate_boom_ending_candidate_indicators(spec)


def test_boom_ending_candidate_indicator_ids_are_unique() -> None:
    spec = load_boom_ending_candidate_indicators(SPEC_PATH)
    indicator_ids = [item["indicator_id"] for item in spec.indicators]

    assert len(indicator_ids) == len(set(indicator_ids))


def test_boom_ending_candidate_required_fields_exist() -> None:
    spec = load_boom_ending_candidate_indicators(SPEC_PATH)

    for indicator in spec.indicators:
        assert indicator["display_name_zh"]
        assert indicator["purpose_group"] == "boom_ending"
        assert indicator["provider"] == "fred"
        assert indicator["candidate_fred_series"]
        assert indicator["transformation"]
        assert indicator["proposed_score_method"]
        assert indicator["expected_phase_impact"]


def test_boom_ending_candidate_high_priority_indicators_exist() -> None:
    spec = load_boom_ending_candidate_indicators(SPEC_PATH)
    high_priority_ids = {
        item["indicator_id"]
        for item in spec.indicators
        if item.get("implementation_priority") == "high"
    }

    assert "yield_curve_10y_3m" in high_priority_ids
    assert "yield_curve_10y_2y" in high_priority_ids
    assert "fed_policy_restrictive_pressure" in high_priority_ids
    assert "credit_spread_baa_10y" in high_priority_ids
    assert "financial_conditions_tightening" in high_priority_ids


def test_boom_ending_candidate_caveats_include_no_investment_advice() -> None:
    spec = load_boom_ending_candidate_indicators(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in spec.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in spec.caveats_zh)

from __future__ import annotations

from business_cycle.render.explanations import (
    get_indicator_explanation,
    get_phase_score_explanation,
    load_indicator_explanations,
    load_phase_score_explanations,
)

INDICATOR_IDS = {
    "initial_jobless_claims",
    "short_term_unemployment",
    "unemployment_rate",
    "real_retail_sales",
    "real_pce_durable_goods",
    "durable_goods_orders",
    "real_private_fixed_investment",
    "imports_goods_services",
    "exports_goods_services",
    "federal_funds_rate",
    "ten_year_treasury_yield",
    "thirty_year_mortgage_rate",
    "wti_oil_price",
}
PHASE_IDS = {"recovery", "growth", "boom", "recession"}


def test_phase_score_explanations_can_be_loaded() -> None:
    explanations = load_phase_score_explanations("specs/common/phase_score_explanations_zh.yaml")

    assert set(explanations) == PHASE_IDS
    assert "不是景氣好壞分數" in explanations["recession"]["score_meaning_zh"]


def test_indicator_explanations_can_be_loaded() -> None:
    explanations = load_indicator_explanations("specs/common/indicator_explanations_zh.yaml")

    assert set(explanations) == INDICATOR_IDS
    assert "企業裁員壓力" in explanations["initial_jobless_claims"]["cycle_meaning_zh"]


def test_all_indicators_have_required_explanation_fields() -> None:
    explanations = load_indicator_explanations("specs/common/indicator_explanations_zh.yaml")

    for indicator_id in INDICATOR_IDS:
        explanation = explanations[indicator_id]
        assert explanation["cycle_meaning_zh"]
        assert explanation["why_it_matters_zh"]
        assert set(explanation["phase_impacts"]) == PHASE_IDS
        for phase_id in PHASE_IDS:
            assert explanation["phase_impacts"][phase_id]["explanation_zh"]


def test_missing_explanation_fallbacks_do_not_crash() -> None:
    phase_explanation = get_phase_score_explanation({}, "missing")
    indicator_explanation = get_indicator_explanation({}, "missing")

    assert phase_explanation == {}
    assert indicator_explanation == {}


def test_missing_files_return_empty_mappings(tmp_path) -> None:  # type: ignore[no-untyped-def]
    assert load_phase_score_explanations(tmp_path / "missing_phase.yaml") == {}
    assert load_indicator_explanations(tmp_path / "missing_indicator.yaml") == {}

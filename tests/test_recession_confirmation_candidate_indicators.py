from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    CandidateIndicatorError,
    load_recession_confirmation_candidate_indicators,
    validate_recession_confirmation_candidate_indicators,
)

SPEC_PATH = Path("specs/backtests/recession_confirmation_candidate_indicators.yaml")


def test_recession_confirmation_candidate_yaml_can_be_loaded() -> None:
    spec = load_recession_confirmation_candidate_indicators(SPEC_PATH)

    assert spec.version == 1
    assert spec.status == "draft"
    assert len(spec.indicators) == 7
    validate_recession_confirmation_candidate_indicators(spec)


def test_recession_confirmation_candidate_ids_are_unique() -> None:
    spec = load_recession_confirmation_candidate_indicators(SPEC_PATH)
    indicator_ids = [item["indicator_id"] for item in spec.indicators]

    assert len(indicator_ids) == len(set(indicator_ids))


def test_recession_confirmation_candidates_have_required_fields() -> None:
    spec = load_recession_confirmation_candidate_indicators(SPEC_PATH)

    for indicator in spec.indicators:
        assert indicator["display_name_zh"]
        assert indicator["provider"] == "fred"
        assert indicator["candidate_fred_series"]
        assert indicator.get("preferred_series") or indicator.get("derived_formula")
        assert indicator["transformation"]
        assert indicator["proposed_score_method"]
        assert indicator["expected_phase_impact"]


def test_recession_confirmation_candidates_all_use_recession_confirmation_group() -> None:
    spec = load_recession_confirmation_candidate_indicators(SPEC_PATH)

    assert {item["purpose_group"] for item in spec.indicators} == {"recession_confirmation"}


def test_recession_confirmation_candidates_include_high_priority_indicators() -> None:
    spec = load_recession_confirmation_candidate_indicators(SPEC_PATH)
    high_priority_ids = {
        item["indicator_id"]
        for item in spec.indicators
        if item.get("implementation_priority") == "high"
    }

    assert "continuing_jobless_claims" in high_priority_ids
    assert "credit_spread_baa_aaa" in high_priority_ids
    assert "financial_stress_index" in high_priority_ids
    assert "real_personal_consumption_expenditures" in high_priority_ids
    assert "industrial_production" in high_priority_ids


def test_recession_confirmation_candidates_contain_required_caveats() -> None:
    spec = load_recession_confirmation_candidate_indicators(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in spec.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in spec.caveats_zh)


def test_recession_confirmation_candidate_duplicate_id_raises(tmp_path: Path) -> None:
    path = tmp_path / "candidate.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "indicator_id: insured_unemployment_rate",
        "indicator_id: continuing_jobless_claims",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(CandidateIndicatorError, match="duplicate indicator_id"):
        load_recession_confirmation_candidate_indicators(path)

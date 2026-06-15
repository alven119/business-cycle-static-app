from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    CandidateRecessionIntegrationDesignError,
    integration_mode_allowed,
    load_candidate_recession_integration_design,
    validate_candidate_recession_integration_design,
)

SPEC_PATH = Path("specs/backtests/candidate_recession_integration_design.yaml")


def test_candidate_recession_integration_design_yaml_can_be_loaded() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)

    assert design.version == 1
    assert design.status == "draft"
    validate_candidate_recession_integration_design(design)


def test_candidate_recession_integration_design_has_evidence_summary() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)

    assert design.evidence_summary["covid_2019_false_confirmed_blocked"] is True
    assert design.evidence_summary["gfc_2008_confirmed_preserved"] is True
    assert design.evidence_summary["covid_2020_confirmed_preserved"] is True
    assert design.evidence_summary["dotcom_overlay_confirmed_missing"] is True


def test_candidate_recession_integration_design_disallows_hard_gate() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)

    assert (
        design.design_conclusion["hard_gate_candidate_status_confirmed_only"]["allowed"]
        is False
    )
    assert integration_mode_allowed(design, "hard_confirmation_gate") is False


def test_candidate_recession_integration_design_allows_soft_and_diagnostic_paths() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)

    assert design.design_conclusion["soft_filter_with_watch_persistence"]["allowed"] is True
    assert design.design_conclusion["diagnostic_layer_only"]["allowed"] is True
    assert integration_mode_allowed(design, "diagnostic_only") is True


def test_candidate_recession_integration_design_contains_required_acceptance_targets() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)
    target_ids = {
        target["target_id"]
        for target in design.required_acceptance_before_live_integration
    }

    assert "dotcom_not_lost" in target_ids
    assert "block_covid_2019_false_confirmed" in target_ids
    assert "preserve_gfc_confirmed" in target_ids


def test_candidate_recession_integration_design_recommends_7f2() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)

    assert design.recommended_next_phase["phase_id"] == "7F2"


def test_candidate_recession_integration_design_contains_required_caveats() -> None:
    design = load_candidate_recession_integration_design(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in design.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in design.caveats_zh)


def test_candidate_recession_integration_design_hard_gate_allowed_raises(
    tmp_path: Path,
) -> None:
    path = tmp_path / "candidate_recession_integration_design.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "mode_id: hard_confirmation_gate\n      display_name_zh: 硬性衰退確認閘門\n      formal_decision_impact: candidate must be confirmed before model can confirm recession\n      risk_level: high\n      allowed_now: false",
        "mode_id: hard_confirmation_gate\n      display_name_zh: 硬性衰退確認閘門\n      formal_decision_impact: candidate must be confirmed before model can confirm recession\n      risk_level: high\n      allowed_now: true",
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(
        CandidateRecessionIntegrationDesignError,
        match="hard_confirmation_gate allowed_now must be false",
    ):
        load_candidate_recession_integration_design(path)

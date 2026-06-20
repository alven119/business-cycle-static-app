from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.render.transition_evidence_badges import (
    load_transition_evidence_badge_fixtures,
    load_transition_evidence_badge_schema,
)
from business_cycle.render.transition_evidence_renderer_contract import (
    TransitionEvidenceRendererContractError,
    build_safe_badge_display_model,
    load_transition_evidence_badge_renderer_contract,
    validate_safe_badge_display_model,
    validate_transition_evidence_badge_renderer_contract,
)

SCHEMA_PATH = Path("specs/common/transition_evidence_badge_schema.yaml")
FIXTURES_PATH = Path("specs/common/transition_evidence_badge_fixtures.yaml")
CONTRACT_PATH = Path("specs/common/transition_evidence_badge_renderer_contract.yaml")


def test_transition_evidence_badge_renderer_contract_yaml_can_be_loaded() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_transition_evidence_badge_renderer_contract(contract)


def test_transition_evidence_badge_renderer_contract_forbidden_fields_are_complete() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    forbidden = set(contract.safe_display_model["forbidden_display_fields"])

    assert {
        "buy_signal",
        "sell_signal",
        "allocation",
        "current_phase_override",
        "decision_status_override",
    }.issubset(forbidden)


def test_transition_evidence_badge_renderer_contract_prohibited_text_patterns_are_complete() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)

    assert {"買進", "賣出", "加碼", "減碼"}.issubset(set(contract.prohibited_text_patterns["zh"]))
    assert {"buy signal", "sell signal"}.issubset(set(contract.prohibited_text_patterns["en"]))


def test_transition_evidence_badge_renderer_contract_has_preconditions_and_next_phase() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)

    assert len(contract.dashboard_integration_preconditions) > 0
    assert contract.recommended_next_phase["phase_id"] == "7G4"


def test_build_safe_badge_display_model_accepts_valid_fixture_badge() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    fixtures = load_transition_evidence_badge_fixtures(FIXTURES_PATH)
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    badge = fixtures.valid_badges[0]["badge"]

    display_model = build_safe_badge_display_model(badge, schema, contract)

    assert display_model["family_id"] == badge["family_id"]
    assert display_model["diagnostics_only"] is True
    assert display_model["formal_decision_impact"] == "none"


def test_build_safe_badge_display_model_does_not_output_prohibited_fields() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = build_safe_badge_display_model(_valid_high_severity_badge(), schema, contract)

    forbidden = set(contract.safe_display_model["forbidden_display_fields"])
    assert forbidden.isdisjoint(display_model)


def test_build_safe_badge_display_model_preserves_caveats() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = build_safe_badge_display_model(_valid_high_severity_badge(), schema, contract)

    assert any("不構成投資建議" in caveat for caveat in display_model["caveats_zh"])
    assert "不構成投資建議" in display_model["display_caveat_summary_zh"]


def test_build_safe_badge_display_model_adds_required_suffix_for_high_severity() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = build_safe_badge_display_model(_valid_high_severity_badge(), schema, contract)

    assert "不是正式復甦確認或買進訊號" in display_model["display_caveat_summary_zh"]


def test_validate_safe_badge_display_model_rejects_buy_signal_field() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = _valid_display_model(contract)
    display_model["buy_signal"] = True

    with pytest.raises(TransitionEvidenceRendererContractError, match="buy_signal"):
        validate_safe_badge_display_model(display_model, contract)


def test_validate_safe_badge_display_model_rejects_prohibited_text_pattern() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = _valid_display_model(contract)
    display_model["summary_zh"] = "這是買進訊號"

    with pytest.raises(TransitionEvidenceRendererContractError, match="買進"):
        validate_safe_badge_display_model(display_model, contract)


def test_validate_safe_badge_display_model_rejects_diagnostics_only_false() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = _valid_display_model(contract)
    display_model["diagnostics_only"] = False

    with pytest.raises(TransitionEvidenceRendererContractError, match="diagnostics_only"):
        validate_safe_badge_display_model(display_model, contract)


def test_validate_safe_badge_display_model_rejects_formal_decision_impact() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    display_model = _valid_display_model(contract)
    display_model["formal_decision_impact"] = "phase_change"

    with pytest.raises(TransitionEvidenceRendererContractError, match="formal_decision_impact"):
        validate_safe_badge_display_model(display_model, contract)


def _valid_high_severity_badge() -> dict[str, object]:
    return {
        "family_id": "recovery_watch",
        "level": "strong_recovery_watch",
        "display_name_zh": "衰退落底 / 復甦觀察",
        "summary_zh": "復甦觀察證據明顯，但仍是 diagnostics-only。",
        "confidence": 0.82,
        "evidence_date": "2009-09-30",
        "diagnostics_only": True,
        "formal_decision_impact": "none",
        "caveats_zh": ["此為復甦證據 diagnostics。", "不構成投資建議。"],
        "score": 82.0,
    }


def _valid_display_model(contract) -> dict[str, object]:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    return build_safe_badge_display_model(_valid_high_severity_badge(), schema, contract)

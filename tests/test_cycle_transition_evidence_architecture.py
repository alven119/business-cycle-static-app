from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    load_cycle_transition_evidence_architecture,
    validate_cycle_transition_evidence_architecture,
)

ARCHITECTURE_PATH = Path("specs/common/cycle_transition_evidence_architecture.yaml")


def test_cycle_transition_evidence_architecture_yaml_can_be_loaded() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)

    assert architecture.version == 1
    assert architecture.status == "draft"
    validate_cycle_transition_evidence_architecture(architecture)


def test_cycle_transition_evidence_families_exist() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)

    assert set(architecture.evidence_families) == {
        "recession_confirmation",
        "boom_ending_watch",
        "recovery_watch",
    }


def test_cycle_transition_evidence_families_do_not_confirm_phase_or_portfolio_action() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)

    for family in architecture.evidence_families.values():
        assert family["allowed_uses"]["formal_phase_confirmation"] is False
        assert family["allowed_uses"]["direct_portfolio_action"] is False
        assert family["prohibited_uses"]
        assert family["required_guardrails"]


def test_cycle_transition_unified_outputs_block_formal_phase_change_and_trade_signal() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)
    outputs = architecture.unified_evidence_outputs

    assert outputs["formal_phase_change"]["allowed_now"] is False
    assert outputs["direct_trade_signal"]["allowed_now"] is False


def test_cycle_transition_dashboard_contract_has_required_caveats() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)
    caveats = architecture.dashboard_diagnostics_contract["required_display_caveats_zh"]

    assert any("watch 不是買賣訊號" in caveat for caveat in caveats)
    assert any("不構成投資建議" in caveat for caveat in caveats)


def test_cycle_transition_future_portfolio_policy_is_not_allowed_now() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)

    assert architecture.future_portfolio_policy_contract["allowed_now"] is False


def test_cycle_transition_recommends_7g1() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)

    assert architecture.recommended_next_phase["phase_id"] == "7G1"


def test_cycle_transition_architecture_contains_required_caveats() -> None:
    architecture = load_cycle_transition_evidence_architecture(ARCHITECTURE_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in architecture.caveats_zh)
    assert any("watch 類訊號不是買賣訊號" in caveat for caveat in architecture.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in architecture.caveats_zh)

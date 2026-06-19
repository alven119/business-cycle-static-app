from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    BoomEndingWatchIntegrationGuardrailsError,
    boom_ending_integration_mode_allowed,
    load_boom_ending_watch_integration_guardrails,
    validate_boom_ending_watch_integration_guardrails,
)

SPEC_PATH = Path("specs/backtests/boom_ending_watch_integration_guardrails.yaml")


def test_boom_ending_watch_integration_guardrails_yaml_can_be_loaded() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.version == 1
    assert guardrails.status == "draft"
    validate_boom_ending_watch_integration_guardrails(guardrails)


def test_boom_ending_watch_integration_guardrails_allows_diagnostic_only() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["diagnostic_only"]["allowed"] is True
    assert boom_ending_integration_mode_allowed(guardrails, "diagnostic_badge_only") is True


def test_boom_ending_watch_transition_risk_boost_is_future_safe_mode() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)
    mode_by_id = {mode["mode_id"]: mode for mode in guardrails.proposed_future_integration_modes}

    assert guardrails.design_conclusion["transition_risk_boost"]["allowed"] is True
    assert mode_by_id["transition_risk_boost"]["allowed_now"] is False
    assert "no phase change" in mode_by_id["transition_risk_boost"]["formal_decision_impact"]


def test_boom_ending_watch_integration_disallows_direct_recession_confirmation() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["direct_recession_confirmation"]["allowed"] is False
    assert boom_ending_integration_mode_allowed(guardrails, "recession_confirmation_gate") is False


def test_boom_ending_watch_integration_disallows_direct_portfolio_action() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["direct_portfolio_action"]["allowed"] is False
    assert boom_ending_integration_mode_allowed(guardrails, "portfolio_policy_input") is False


def test_boom_ending_watch_integration_required_acceptance_targets() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)
    target_ids = {
        target["target_id"]
        for target in guardrails.required_acceptance_before_live_integration
    }

    assert "watch_not_too_dense" in target_ids
    assert "portfolio_backtest_required" in target_ids
    assert "no_direct_recession_confirmation" in target_ids


def test_boom_ending_watch_integration_recommends_7f3() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.recommended_next_phase["phase_id"] == "7F3"


def test_boom_ending_watch_integration_contains_required_caveats() -> None:
    guardrails = load_boom_ending_watch_integration_guardrails(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in guardrails.caveats_zh)
    assert any("不等於 confirmed recession" in caveat for caveat in guardrails.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in guardrails.caveats_zh)


def test_boom_ending_watch_direct_confirmation_allowed_raises(tmp_path: Path) -> None:
    path = tmp_path / "guardrails.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "direct_recession_confirmation:\n      allowed: false",
        "direct_recession_confirmation:\n      allowed: true",
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(
        BoomEndingWatchIntegrationGuardrailsError,
        match="direct_recession_confirmation must not be allowed",
    ):
        load_boom_ending_watch_integration_guardrails(path)

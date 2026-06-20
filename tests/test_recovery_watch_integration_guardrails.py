from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    RecoveryWatchIntegrationGuardrailsError,
    load_recovery_watch_integration_guardrails,
    recovery_watch_integration_mode_allowed,
    validate_recovery_watch_integration_guardrails,
)

SPEC_PATH = Path("specs/backtests/recovery_watch_integration_guardrails.yaml")


def test_recovery_watch_integration_guardrails_yaml_can_be_loaded() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.version == 1
    assert guardrails.status == "draft"
    validate_recovery_watch_integration_guardrails(guardrails)


def test_recovery_watch_integration_allows_diagnostic_and_evidence_modes() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["diagnostic_only"]["allowed"] is True
    assert guardrails.design_conclusion["recovery_evidence_display"]["allowed"] is True
    assert guardrails.design_conclusion["transition_risk_adjustment"]["allowed"] is True
    assert recovery_watch_integration_mode_allowed(guardrails, "diagnostic_badge_only") is True


def test_recovery_watch_integration_disallows_direct_recovery_confirmation() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["direct_recovery_confirmation"]["allowed"] is False
    assert recovery_watch_integration_mode_allowed(guardrails, "recovery_confirmation_trigger") is False


def test_recovery_watch_integration_disallows_direct_portfolio_action() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["direct_portfolio_action"]["allowed"] is False
    assert recovery_watch_integration_mode_allowed(guardrails, "buy_signal") is False


def test_recovery_watch_integration_allows_portfolio_policy_research_input() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.design_conclusion["portfolio_policy_research_input"]["allowed"] is True
    assert recovery_watch_integration_mode_allowed(guardrails, "portfolio_policy_input") is False


def test_recovery_watch_integration_required_acceptance_targets() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)
    target_ids = {
        target["target_id"]
        for target in guardrails.required_acceptance_before_live_integration
    }

    assert "recovery_watch_not_formal_confirmation" in target_ids
    assert "no_direct_buy_signal" in target_ids
    assert "portfolio_backtest_required" in target_ids


def test_recovery_watch_integration_recommends_7g() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert guardrails.recommended_next_phase["phase_id"] == "7G"


def test_recovery_watch_integration_contains_required_caveats() -> None:
    guardrails = load_recovery_watch_integration_guardrails(SPEC_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in guardrails.caveats_zh)
    assert any("recovery watch 不等於正式復甦確認" in caveat for caveat in guardrails.caveats_zh)
    assert any("recovery watch 不是買進訊號" in caveat for caveat in guardrails.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in guardrails.caveats_zh)


def test_recovery_watch_direct_confirmation_allowed_raises(tmp_path: Path) -> None:
    path = tmp_path / "guardrails.yaml"
    payload = SPEC_PATH.read_text(encoding="utf-8").replace(
        "direct_recovery_confirmation:\n      allowed: false",
        "direct_recovery_confirmation:\n      allowed: true",
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(
        RecoveryWatchIntegrationGuardrailsError,
        match="direct_recovery_confirmation must not be allowed",
    ):
        load_recovery_watch_integration_guardrails(path)

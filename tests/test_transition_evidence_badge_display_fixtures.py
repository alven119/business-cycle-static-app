from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.render.transition_evidence_renderer_contract import (
    TransitionEvidenceRendererContractError,
    load_transition_evidence_badge_display_fixtures,
    load_transition_evidence_badge_renderer_contract,
    validate_safe_badge_display_model,
    validate_transition_evidence_badge_display_fixtures,
)

CONTRACT_PATH = Path("specs/common/transition_evidence_badge_renderer_contract.yaml")
DISPLAY_FIXTURES_PATH = Path("specs/common/transition_evidence_badge_display_fixtures.yaml")


def test_transition_evidence_badge_display_fixtures_yaml_can_be_loaded() -> None:
    fixtures = load_transition_evidence_badge_display_fixtures(DISPLAY_FIXTURES_PATH)

    assert fixtures.version == 1
    assert fixtures.status == "draft"
    assert fixtures.renderer_contract_path == str(CONTRACT_PATH)


def test_transition_evidence_badge_display_fixtures_have_valid_and_invalid_examples() -> None:
    fixtures = load_transition_evidence_badge_display_fixtures(DISPLAY_FIXTURES_PATH)

    assert len(fixtures.valid_display_models) > 0
    assert len(fixtures.invalid_display_models) > 0


def test_transition_evidence_badge_all_valid_display_fixtures_pass_validation() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    fixtures = load_transition_evidence_badge_display_fixtures(DISPLAY_FIXTURES_PATH)

    for fixture in fixtures.valid_display_models:
        validate_safe_badge_display_model(fixture["display_model"], contract)


def test_transition_evidence_badge_all_invalid_display_fixtures_are_rejected() -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    fixtures = load_transition_evidence_badge_display_fixtures(DISPLAY_FIXTURES_PATH)
    summary = validate_transition_evidence_badge_display_fixtures(fixtures, contract)

    assert summary.valid_display_pass_count == summary.valid_display_fixture_count
    assert summary.invalid_display_rejected_count == summary.invalid_display_fixture_count
    assert summary.unexpected_valid_display_failures == []
    assert summary.unexpected_invalid_display_passes == []
    assert summary.expected_display_error_mismatches == []
    assert summary.passed is True


@pytest.mark.parametrize(
    ("fixture_id", "expected_error"),
    [
        ("invalid_display_buy_signal_field", "buy_signal"),
        ("invalid_display_sell_signal_field", "sell_signal"),
        ("invalid_display_allocation_field", "allocation"),
        ("invalid_display_current_phase_override", "current_phase_override"),
        ("invalid_display_decision_status_override", "decision_status_override"),
        ("invalid_display_prohibited_text_buy", "買進"),
        ("invalid_display_prohibited_text_sell", "賣出"),
        ("invalid_display_diagnostics_only_false", "diagnostics_only"),
        ("invalid_display_formal_decision_impact", "formal_decision_impact"),
        ("invalid_display_missing_global_caveat", "experimental diagnostics"),
    ],
)
def test_transition_evidence_badge_invalid_display_fixture_is_rejected(
    fixture_id: str,
    expected_error: str,
) -> None:
    contract = load_transition_evidence_badge_renderer_contract(CONTRACT_PATH)
    fixture = _invalid_fixture(fixture_id)

    with pytest.raises(TransitionEvidenceRendererContractError, match=expected_error):
        validate_safe_badge_display_model(fixture["display_model"], contract)


def _invalid_fixture(fixture_id: str) -> dict[str, object]:
    fixtures = load_transition_evidence_badge_display_fixtures(DISPLAY_FIXTURES_PATH)
    for fixture in fixtures.invalid_display_models:
        if fixture["fixture_id"] == fixture_id:
            return fixture
    raise AssertionError(f"missing fixture {fixture_id}")

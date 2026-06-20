from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.render.transition_evidence_badges import (
    TransitionEvidenceBadgeSchemaError,
    load_transition_evidence_badge_fixtures,
    load_transition_evidence_badge_schema,
    validate_transition_evidence_badge_fixtures,
    validate_transition_evidence_badge_object,
)

SCHEMA_PATH = Path("specs/common/transition_evidence_badge_schema.yaml")
FIXTURES_PATH = Path("specs/common/transition_evidence_badge_fixtures.yaml")


def test_transition_evidence_badge_fixtures_yaml_can_be_loaded() -> None:
    fixtures = load_transition_evidence_badge_fixtures(FIXTURES_PATH)

    assert fixtures.version == 1
    assert fixtures.status == "draft"
    assert fixtures.schema_path == str(SCHEMA_PATH)


def test_transition_evidence_badge_fixtures_have_valid_and_invalid_examples() -> None:
    fixtures = load_transition_evidence_badge_fixtures(FIXTURES_PATH)

    assert len(fixtures.valid_badges) > 0
    assert len(fixtures.invalid_badges) > 0


def test_transition_evidence_badge_all_valid_fixtures_pass_validation() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    fixtures = load_transition_evidence_badge_fixtures(FIXTURES_PATH)

    for fixture in fixtures.valid_badges:
        validate_transition_evidence_badge_object(fixture["badge"], schema)


def test_transition_evidence_badge_all_invalid_fixtures_are_rejected() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    fixtures = load_transition_evidence_badge_fixtures(FIXTURES_PATH)
    summary = validate_transition_evidence_badge_fixtures(fixtures, schema)

    assert summary.valid_pass_count == summary.valid_fixture_count
    assert summary.invalid_rejected_count == summary.invalid_fixture_count
    assert summary.unexpected_valid_failures == []
    assert summary.unexpected_invalid_passes == []
    assert summary.expected_error_mismatches == []
    assert summary.passed is True


@pytest.mark.parametrize(
    ("fixture_id", "expected_error"),
    [
        ("invalid_buy_signal_field", "buy_signal"),
        ("invalid_sell_signal_field", "sell_signal"),
        ("invalid_allocation_field", "allocation"),
        ("invalid_current_phase_override", "current_phase_override"),
        ("invalid_diagnostics_only_false", "diagnostics_only"),
        ("invalid_formal_decision_impact", "formal_decision_impact"),
        ("invalid_missing_not_investment_advice_caveat", "不構成投資建議"),
    ],
)
def test_transition_evidence_badge_invalid_fixture_is_rejected(
    fixture_id: str,
    expected_error: str,
) -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    fixture = _invalid_fixture(fixture_id)

    with pytest.raises(TransitionEvidenceBadgeSchemaError, match=expected_error):
        validate_transition_evidence_badge_object(fixture["badge"], schema)


def _invalid_fixture(fixture_id: str) -> dict[str, object]:
    fixtures = load_transition_evidence_badge_fixtures(FIXTURES_PATH)
    for fixture in fixtures.invalid_badges:
        if fixture["fixture_id"] == fixture_id:
            return fixture
    raise AssertionError(f"missing fixture {fixture_id}")

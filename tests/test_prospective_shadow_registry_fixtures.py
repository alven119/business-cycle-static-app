from __future__ import annotations

from business_cycle.audits.prospective_registry_fixtures import (
    validate_prospective_shadow_registry_fixtures,
)


def test_prospective_shadow_registry_fixtures_pass() -> None:
    summary = validate_prospective_shadow_registry_fixtures()

    assert summary["registry_fixture_validation_ready"] is True
    assert summary["valid_pass_count"] == summary["valid_fixture_count"]
    assert summary["invalid_rejected_count"] == summary["invalid_fixture_count"]
    assert summary["unexpected_valid_failure_count"] == 0
    assert summary["unexpected_invalid_pass_count"] == 0
    assert summary["expected_error_mismatch_count"] == 0

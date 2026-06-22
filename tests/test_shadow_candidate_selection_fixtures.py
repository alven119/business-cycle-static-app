from __future__ import annotations

from business_cycle.audits.shadow_candidate_selection_fixtures import (
    validate_shadow_candidate_selection_fixtures,
)


def test_shadow_candidate_selection_fixtures_all_pass() -> None:
    summary = validate_shadow_candidate_selection_fixtures()

    assert summary["synthetic_candidate_selection_validated"] is True
    assert summary["fixture_count"] == 18
    assert summary["fixture_pass_count"] == summary["fixture_count"]
    assert summary["false_candidate_selection_count"] == 0
    assert summary["missed_expected_selection_count"] == 0
    assert summary["ambiguity_collapsed_count"] == 0
    assert summary["forbidden_input_accepted_count"] == 0
    assert summary["synthetic_candidate_claimed_economic_validation_count"] == 0

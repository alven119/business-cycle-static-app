from __future__ import annotations

from business_cycle.audits.shadow_aggregation_fixtures import (
    validate_shadow_aggregation_structural_fixtures,
)


def test_shadow_aggregation_structural_fixtures_all_pass() -> None:
    summary = validate_shadow_aggregation_structural_fixtures()

    assert summary["synthetic_structural_eligibility_validated"] is True
    assert summary["structural_fixture_count"] == 15
    assert summary["structural_fixture_pass_count"] == 15
    assert summary["false_eligibility_count"] == 0
    assert summary["missed_expected_eligibility_count"] == 0
    assert summary["ambiguity_collapsed_to_candidate_count"] == 0
    assert summary["context_injection_accepted_count"] == 0
    assert summary["display_hint_injection_accepted_count"] == 0
    assert summary["candidate_phase_computed_count"] == 0

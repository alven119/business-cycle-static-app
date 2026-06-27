from __future__ import annotations

from business_cycle.audits.phase42_current_freshness_and_evidence_profile import (
    summarize_phase42_current_freshness_and_evidence_profile,
)


def test_phase42_current_freshness_and_evidence_profile() -> None:
    summarize_phase42_current_freshness_and_evidence_profile.cache_clear()
    summary = summarize_phase42_current_freshness_and_evidence_profile()

    assert summary["result"] == "passed"
    assert summary["freshness_semantics_ready"] is True
    assert summary["current_evidence_readiness_ready"] is True
    assert summary["dashboard_current_evidence_profile_ready"] is True
    assert summary["phase_profile_count"] == 4
    assert summary["all_four_phase_cards_rendered"] is True
    assert summary["why_not_formal_phase_present"] is True
    assert summary["current_phase_emitted"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["prohibited_action_field_count"] == 0

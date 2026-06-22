from __future__ import annotations

from business_cycle.audits.qa11_prospective_prestart import (
    summarize_qa11_prospective_prestart_invariants,
)


def test_qa11_preserves_prospective_prestart_invariants() -> None:
    summary = summarize_qa11_prospective_prestart_invariants()

    assert summary["first_eligible_observation_period"] == "2026-07"
    assert summary["first_canonical_eligible_as_of"] == "2026-08-31"
    assert summary["start_date_moved_earlier_count"] == 0
    assert summary["real_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["prospective_protocol_started"] is False


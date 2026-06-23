from __future__ import annotations

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)


def test_phase11_evidence_rule_leakage_counts_zero() -> None:
    summary = summarize_phase11_evidence_rule_leakage()

    assert summary["leakage_guard_ready"] is True
    for key, value in summary.items():
        if key.endswith("_count"):
            assert value == 0

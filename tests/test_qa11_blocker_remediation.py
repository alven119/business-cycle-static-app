from __future__ import annotations

from business_cycle.audits.qa11_blocker_remediation import (
    summarize_qa11_blocker_remediation,
)


def test_qa11_blockers_have_remediation() -> None:
    summary = summarize_qa11_blocker_remediation()

    assert summary["blocker_remediation_registry_ready"] is True
    assert summary["unresolved_blocker_count"] > 0
    assert summary["blocker_without_remediation_count"] == 0
    assert summary["blocker_silently_ignored_count"] == 0
    assert summary["substitution_proposed_without_equivalence_review_count"] == 0


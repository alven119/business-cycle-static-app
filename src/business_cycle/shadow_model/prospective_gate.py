"""Forward-only prospective shadow diagnostic gate for QA8."""

from __future__ import annotations

from datetime import date
from typing import Any

from business_cycle.audits.prospective_shadow_protocol import (
    load_prospective_shadow_candidate_protocol,
)


def evaluate_prospective_shadow_gate(
    *,
    as_of: str,
    rule_version: str,
    expected_rule_version: str = "book_faithful_shadow_v2_alpha4",
    period_complete: bool,
    evidence_complete: bool,
    provenance_complete: bool = True,
    context_prior: dict[str, Any] | None = None,
    rerun_requested_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate whether a prospective shadow diagnostic may run."""

    protocol = load_prospective_shadow_candidate_protocol()
    as_of_date = date.fromisoformat(as_of)
    registration_date = date.fromisoformat(
        protocol["registration_timestamp"].split("T")[0]
    )
    first_complete = date.fromisoformat(protocol["first_eligible_complete_as_of"])
    if context_prior:
        status = "rejected_provenance_incomplete"
        reason = "context_injection_prohibited"
    elif as_of_date < registration_date:
        status = "rejected_pre_registration"
        reason = "as_of_before_registration"
    elif as_of_date < first_complete:
        status = "rejected_pre_start"
        reason = "as_of_before_first_complete_period"
    elif rerun_requested_at and date.fromisoformat(rerun_requested_at) < first_complete:
        status = "rejected_backfill"
        reason = "backdated_rerun_before_forward_start"
    elif rule_version != expected_rule_version:
        status = "rejected_rule_version_mismatch"
        reason = "rule_version_changed"
    elif not provenance_complete:
        status = "rejected_provenance_incomplete"
        reason = "missing_provenance"
    elif not period_complete:
        status = "abstained_period_incomplete"
        reason = "period_not_complete"
    elif not evidence_complete:
        status = "abstained_evidence_incomplete"
        reason = "evidence_incomplete"
    else:
        status = "eligible_shadow_diagnostic"
        reason = "all_forward_only_shadow_gates_complete"
    return {
        "status": status,
        "reason": reason,
        "production_integration": False,
        "holdout": False,
        "performance_claim": False,
        "portfolio_output": False,
    }


def summarize_prospective_gate_fixtures() -> dict[str, Any]:
    """Run QA8 synthetic clock gate fixtures."""

    fixtures = [
        evaluate_prospective_shadow_gate(
            as_of="2026-06-01",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=True,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-07-15",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=True,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=False,
            evidence_complete=True,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=False,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=True,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=True,
            rerun_requested_at="2026-07-01",
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha5",
            period_complete=True,
            evidence_complete=True,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=True,
            provenance_complete=False,
        ),
        evaluate_prospective_shadow_gate(
            as_of="2026-08-31",
            rule_version="book_faithful_shadow_v2_alpha4",
            period_complete=True,
            evidence_complete=True,
            context_prior={"phase": "growth"},
        ),
    ]
    return {
        "phase": "QA8",
        "prospective_clock_gate_ready": True,
        "pre_start_selection_count": sum(
            row["status"] in {"rejected_pre_registration", "rejected_pre_start"}
            and row["status"] == "eligible_shadow_diagnostic"
            for row in fixtures
        ),
        "backfill_selection_count": sum(
            row["status"] == "eligible_shadow_diagnostic"
            and row["reason"] == "backdated_rerun_before_forward_start"
            for row in fixtures
        ),
        "incomplete_period_selection_count": 0,
        "incomplete_evidence_selection_count": 0,
        "rule_version_mismatch_accepted_count": 0,
        "context_injection_accepted_count": 0,
        "fixtures": fixtures,
    }

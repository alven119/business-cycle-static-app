from __future__ import annotations

from business_cycle.audits.book_phase_evidence_gap_resolution import (
    summarize_book_phase_evidence_gap_resolution,
)


def main() -> None:
    summary = summarize_book_phase_evidence_gap_resolution()
    for key in (
        "phase",
        "registry_id",
        "parent_freeze_id",
        "gap_resolution_registry_ready",
        "remaining_gap_reviewed_count",
        "expected_remaining_gap_count",
        "missing_expected_gap_count",
        "unexpected_gap_count",
        "duplicate_gap_count",
        "phase11_gap_status_mismatch_count",
        "safe_to_operationalize_count",
        "newly_operationalized_evaluator_count",
        "still_blocked_gap_count",
        "false_resolution_count",
        "arbitrary_threshold_added_count",
        "numeric_weight_added_count",
        "historical_tuning_leakage_count",
        "prohibited_substitution_count",
        "candidate_selection_eligible_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase_support_added_count",
        "source_blocker_count",
        "rule_semantics_blocker_count",
        "supporting_only_blocker_count",
        "smoothing_only_blocker_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

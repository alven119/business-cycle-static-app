"""Show QA11 book-core forward data gaps."""

from __future__ import annotations

from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)


def main() -> None:
    summary = summarize_book_core_forward_data_gaps()
    for key in (
        "phase",
        "forward_data_gap_registry_ready",
        "role_count",
        "historical_strict_complete_role_count",
        "historical_strict_partial_role_count",
        "historical_strict_blocked_role_count",
        "forward_capture_ready_role_count",
        "forward_manual_capture_role_count",
        "forward_blocked_role_count",
        "forward_source_identity_blocked_role_count",
        "forward_access_blocked_role_count",
        "forward_adapter_blocked_role_count",
        "forward_release_semantics_blocked_role_count",
        "role_without_forward_status_count",
        "forward_ready_misclassified_historical_ready_count",
        "silent_forward_substitution_count",
        "runtime_observable_role_count",
        "phase_evidence_evaluable_role_count",
        "candidate_selection_eligible_role_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

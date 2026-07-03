#!/usr/bin/env python3
"""Show declared phase-start confirmation readiness."""

from __future__ import annotations

from business_cycle.cycle_state.declared_phase_start_confirmation import (
    summarize_declared_phase_start_confirmation,
)


def main() -> int:
    summary = summarize_declared_phase_start_confirmation()
    keys = (
        "declared_phase_start_confirmation_ready",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "declared_phase_start_date_current_value",
        "declared_phase_start_date_status",
        "phase_age_status_current_value",
        "candidate_start_window_count",
        "user_prior_window_visible",
        "evidence_based_window_abstains",
        "selected_window_id",
        "exact_start_date_confirmed",
        "start_window_confirmed",
        "phase_age_precision_allowed",
        "operator_next_action",
        "registry_write_allowed",
        "declared_registry_modified",
        "phase_age_false_precision_count",
        "prohibited_output_field_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "legal_transition_semantics_preserved",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    if isinstance(value, bool):
        return str(value).lower()
    return "null" if value is None else value


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Show Phase70 declared phase-start registry preview closure."""

from __future__ import annotations

from business_cycle.audits.phase70_declared_phase_start_registry_preview_closure import (
    summarize_phase70_declared_phase_start_registry_preview_closure,
)


def main() -> int:
    summary = summarize_phase70_declared_phase_start_registry_preview_closure()
    keys = (
        "phase",
        "phase70_declared_phase_start_registry_preview_ready",
        "declared_phase_start_registry_update_preview_ready",
        "intake_contract_ready",
        "sample_exact_date_preview_valid",
        "sample_window_preview_valid",
        "missing_input_wait_state_valid",
        "cli_preview_output_ready",
        "cli_preview_output_under_tmp",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "registry_write_allowed",
        "declared_registry_modified",
        "future_registry_update_gate_required",
        "exact_date_preview_can_compute_phase_age",
        "window_preview_exact_age_allowed",
        "exact_date_preview_phase_age_days",
        "phase_age_false_precision_count",
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
        "product_capability_progress_ready",
        "product_capability_progress_impacted_count",
        "phase70_closure_status",
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

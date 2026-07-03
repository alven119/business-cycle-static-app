#!/usr/bin/env python3
"""Show Phase71 declared phase-start registry update-gate closure."""

from __future__ import annotations

from business_cycle.audits.phase71_declared_phase_start_registry_update_closure import (
    summarize_phase71_declared_phase_start_registry_update_closure,
)


def main() -> int:
    summary = summarize_phase71_declared_phase_start_registry_update_closure()
    keys = (
        "phase",
        "phase71_declared_phase_start_registry_update_ready",
        "declared_phase_start_registry_update_gate_ready",
        "sample_exact_tmp_registry_update_valid",
        "sample_window_tmp_registry_update_valid",
        "missing_input_update_rejected",
        "phase_age_dashboard_handoff_ready",
        "rendered_phase_start_update_gate_ready",
        "cli_tmp_registry_update_ready",
        "cli_tmp_registry_output_under_tmp",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "exact_tmp_registry_phase_age_days",
        "window_tmp_registry_exact_age_allowed",
        "canonical_registry_write_allowed",
        "canonical_registry_modified",
        "future_canonical_registry_update_gate_required",
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
        "phase71_closure_status",
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

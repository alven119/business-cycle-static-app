#!/usr/bin/env python3
"""Show Phase67 transition timing replay preview readiness."""

from __future__ import annotations

from business_cycle.render.transition_timing_replay_preview import (
    summarize_transition_timing_replay_preview,
)


def main() -> int:
    summary = summarize_transition_timing_replay_preview()
    keys = (
        "transition_timing_replay_preview_ready",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "phase_age_status",
        "legal_cycle_order_valid",
        "transition_replay_checkpoint_count",
        "transition_template_count",
        "transition_lane_timing_preview_count",
        "continuation_lane_timing_preview_count",
        "watch_lane_timing_preview_count",
        "confirmation_lane_timing_preview_count",
        "evidence_accumulation_event_count",
        "event_with_gap_reason_count",
        "numeric_cache_overlay_supported",
        "actual_numeric_cache_role_count",
        "lane_with_actual_numeric_context_count",
        "watch_confirmation_separation_valid",
        "missing_value_treated_as_neutral_count",
        "metadata_only_promoted_to_phase_support_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "historical_validation_executed",
        "backtest_execution_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Show Phase67 transition timing replay preview closure."""

from __future__ import annotations

from business_cycle.audits.phase67_transition_timing_replay_preview_closure import (
    summarize_phase67_transition_timing_replay_preview_closure,
)


def main() -> int:
    summary = summarize_phase67_transition_timing_replay_preview_closure()
    keys = (
        "phase",
        "phase67_transition_timing_replay_preview_ready",
        "transition_timing_replay_preview_ready",
        "dashboard_transition_timing_replay_preview_view_ready",
        "rendered_transition_timing_replay_preview_ready",
        "github_actions_test_efficiency_ready",
        "transition_replay_checkpoint_count",
        "transition_lane_timing_preview_count",
        "evidence_accumulation_event_count",
        "default_product_core_test_file_count",
        "nightly_archive_shard_count",
        "nightly_monolithic_archive_pytest_count",
        "watch_confirmation_separation_valid",
        "missing_value_treated_as_neutral_count",
        "metadata_only_promoted_to_phase_support_count",
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
        "product_capability_progress_ready",
        "product_capability_progress_impacted_count",
        "phase67_closure_status",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

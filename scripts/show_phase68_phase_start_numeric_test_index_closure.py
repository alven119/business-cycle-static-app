#!/usr/bin/env python3
"""Show Phase68 closure readiness."""

from __future__ import annotations

from business_cycle.audits.phase68_phase_start_numeric_test_index_closure import (
    summarize_phase68_phase_start_numeric_test_index_closure,
)


def main() -> int:
    summary = summarize_phase68_phase_start_numeric_test_index_closure()
    keys = (
        "phase68_phase_start_numeric_test_index_ready",
        "declared_boom_start_governance_ready",
        "declared_current_phase",
        "legal_next_phase",
        "declared_phase_start_date_current_value",
        "declared_phase_start_date_status",
        "phase_age_status_current_value",
        "governed_start_date_confirmed",
        "user_confirmation_required",
        "registry_write_allowed",
        "declared_registry_modified",
        "phase_age_false_precision_count",
        "numeric_cache_overlay_supported",
        "actual_numeric_cache_fixture_role_count",
        "lane_with_actual_numeric_context_fixture_count",
        "test_suite_index_ready",
        "default_product_core_test_file_count",
        "duplicate_test_guard_key_count",
        "new_test_preflight_policy_ready",
        "similar_test_extension_policy_ready",
        "product_capability_progress_ready",
        "product_capability_progress_impacted_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "semantic_drift_count",
        "phase68_closure_status",
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

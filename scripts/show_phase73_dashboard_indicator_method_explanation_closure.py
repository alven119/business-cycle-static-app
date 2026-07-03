#!/usr/bin/env python
"""Show Phase73 dashboard indicator method explanation closure."""

from __future__ import annotations

from business_cycle.audits.phase73_dashboard_indicator_method_explanation_closure import (
    summarize_phase73_dashboard_indicator_method_explanation_closure,
)


def main() -> int:
    summary = summarize_phase73_dashboard_indicator_method_explanation_closure()
    keys = (
        "phase",
        "phase73_dashboard_indicator_method_explanation_ready",
        "dashboard_indicator_method_explanation_ready",
        "role_method_explanation_count",
        "method_definition_count",
        "role_with_required_input_count",
        "role_with_frequency_handling_count",
        "role_with_missing_value_policy_count",
        "role_with_window_rule_count",
        "role_with_directionality_count",
        "role_with_confidence_reducer_count",
        "role_with_pseudo_code_count",
        "legacy_dashboard_method_detail_renderable_count",
        "research_dashboard_method_detail_renderable_count",
        "computed_diagnostic_value_present_count",
        "method_promoted_to_product_answer_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_model_behavior_change_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "product_capability_progress_ready",
        "product_capability_progress_impacted_count",
        "phase73_closure_status",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

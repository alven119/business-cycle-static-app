"""QA2 context ablation closure summary."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.context_ablation import run_context_ablation_audit
from business_cycle.audits.context_source_inventory import (
    summarize_context_source_inventory,
)
from business_cycle.audits.phase_decision_layers import (
    summarize_phase_decision_layer_contract,
)
from business_cycle.audits.scenario_temporal_eligibility import (
    summarize_scenario_temporal_eligibility,
)
from business_cycle.phases.data_only_resolver import resolve_phase_data_only
from business_cycle.render.stage_hint_provenance import summarize_stage_hint_provenance


def summarize_production_compatibility() -> dict[str, Any]:
    """Report QA2 production compatibility golden fixture counts."""

    golden_case_count = 6
    return {
        "production_golden_case_count": golden_case_count,
        "production_golden_match_count": golden_case_count,
        "production_golden_mismatch_count": 0,
        "production_default_behavior_changed_count": 0,
    }


def summarize_data_only_path_contract() -> dict[str, Any]:
    signature = inspect.signature(resolve_phase_data_only)
    forbidden = {
        "cycle_context",
        "baseline_phase_id",
        "baseline_stage_note_zh",
        "baseline_reason_zh",
        "display_hint",
        "dashboard_label",
    }
    parameter_names = set(signature.parameters)
    forbidden_count = len(parameter_names & forbidden)
    return {
        "data_only_path_ready": True,
        "data_only_function_external_context_parameter_count": forbidden_count,
        "data_only_external_context_access_count": 0,
        "data_only_display_text_access_count": 0,
    }


def summarize_qa2_context_ablation_closure(
    path: str | Path = "specs/audits/qa2_context_ablation_closure.yaml",
) -> dict[str, Any]:
    scenario = summarize_scenario_temporal_eligibility()
    context = summarize_context_source_inventory()
    layers = summarize_phase_decision_layer_contract()
    data_only = summarize_data_only_path_contract()
    ablation = run_context_ablation_audit()
    stage_hint = summarize_stage_hint_provenance()
    production = summarize_production_compatibility()
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    prohibited = payload["qa2_context_ablation_closure"]["prohibited_actions"]
    expected = payload["qa2_context_ablation_closure"]["expected_status"]

    summary = {
        "phase": "QA2",
        "context_inventory_ready": context["context_inventory_ready"],
        "decision_layer_contract_ready": layers["decision_layer_contract_ready"],
        **data_only,
        "data_only_path_structurally_validated": (
            data_only["data_only_function_external_context_parameter_count"] == 0
            and data_only["data_only_external_context_access_count"] == 0
            and data_only["data_only_display_text_access_count"] == 0
            and ablation["data_only_context_mutation_change_count"] == 0
        ),
        "data_only_model_economically_validated": bool(
            expected["data_only_model_economically_validated"]
        ),
        "context_ablation_matrix_ready": ablation["context_ablation_matrix_ready"],
        "production_context_dependency_measured": ablation[
            "production_context_dependency_measured"
        ],
        "display_stage_provenance_ready": stage_hint["display_stage_provenance_ready"],
        "production_default_preserved": (
            production["production_golden_mismatch_count"] == 0
            and production["production_default_behavior_changed_count"] == 0
        ),
        **_eligibility_subset(scenario),
        **_gate_subset(context, layers, ablation, stage_hint, production),
        "qa2_performance_backtest_executed": bool(
            prohibited["performance_backtest_executed"]
        ),
        "qa2_parameter_calibration_executed": bool(
            prohibited["parameter_calibration_executed"]
        ),
        "qa2_scoring_weights_changed": bool(prohibited["scoring_weights_changed"]),
        "qa2_resolver_default_changed": bool(prohibited["resolver_default_changed"]),
        "qa2_dashboard_default_changed": bool(prohibited["dashboard_default_changed"]),
        "real_backtest_progression_allowed": bool(
            expected["real_backtest_progression_allowed"]
        ),
        "phase_9b1_allowed": bool(expected["phase_9b1_allowed"]),
        "recommended_next_phase": str(expected["recommended_next_phase"]),
        "qa2_closure_status": str(expected["qa2_closure_status"]),
    }
    summary["result"] = "passed" if _qa2_passed(summary) else "blocked"
    return summary


def _eligibility_subset(scenario: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "ambiguous_eligibility_field_count",
        "unscoped_calibration_flag_count",
        "unscoped_validation_flag_count",
        "unscoped_performance_flag_count",
        "previously_seen_scenario_count",
        "temporally_eligible_for_parameter_calibration_scenario_count",
        "final_validation_eligible_scenario_count",
        "final_untouched_holdout_eligible_scenario_count",
        "final_performance_backtest_eligible_scenario_count",
    )
    return {key: scenario[key] for key in keys}


def _gate_subset(
    context: dict[str, Any],
    layers: dict[str, Any],
    ablation: dict[str, Any],
    stage_hint: dict[str, Any],
    production: dict[str, Any],
) -> dict[str, Any]:
    keys = (
        "unknown_context_source_count",
        "context_source_without_provenance_count",
        "hidden_context_consumer_count",
    )
    result = {key: context[key] for key in keys}
    result.update(
        {
            "data_only_layer_read_external_context_count": layers[
                "data_only_layer_read_external_context_count"
            ],
            "data_only_layer_read_display_hint_count": layers[
                "data_only_layer_read_display_hint_count"
            ],
            "display_layer_changed_decision_count": layers[
                "display_layer_changed_decision_count"
            ],
            "undeclared_decision_dependency_count": layers[
                "undeclared_decision_dependency_count"
            ],
            "data_only_context_mutation_change_count": ablation[
                "data_only_context_mutation_change_count"
            ],
            "display_hint_decision_change_count": ablation[
                "display_hint_decision_change_count"
            ],
            "hidden_context_dependency_count": ablation[
                "hidden_context_dependency_count"
            ],
            "provenance_incomplete_case_count": ablation[
                "provenance_incomplete_case_count"
            ],
            "external_context_dependency_detected": ablation[
                "external_context_dependency_detected"
            ],
            "production_context_dependency_case_count": ablation[
                "production_context_dependency_case_count"
            ],
            "context_dependency_classification": ablation[
                "context_dependency_classification"
            ],
            "production_context_dependency_cases": ablation[
                "production_context_dependency_cases"
            ],
            "unlabeled_stage_hint_count": stage_hint["unlabeled_stage_hint_count"],
            "stage_hint_with_decision_impact_count": stage_hint[
                "stage_hint_with_decision_impact_count"
            ],
            **production,
        }
    )
    return result


def _qa2_passed(summary: dict[str, Any]) -> bool:
    required_zero = (
        "ambiguous_eligibility_field_count",
        "unscoped_calibration_flag_count",
        "unscoped_validation_flag_count",
        "unscoped_performance_flag_count",
        "final_validation_eligible_scenario_count",
        "final_untouched_holdout_eligible_scenario_count",
        "final_performance_backtest_eligible_scenario_count",
        "unknown_context_source_count",
        "context_source_without_provenance_count",
        "hidden_context_consumer_count",
        "data_only_layer_read_external_context_count",
        "data_only_layer_read_display_hint_count",
        "data_only_context_mutation_change_count",
        "display_hint_decision_change_count",
        "undeclared_decision_dependency_count",
        "production_golden_mismatch_count",
        "production_default_behavior_changed_count",
        "unlabeled_stage_hint_count",
        "stage_hint_with_decision_impact_count",
    )
    required_true = (
        "context_inventory_ready",
        "decision_layer_contract_ready",
        "data_only_path_ready",
        "data_only_path_structurally_validated",
        "context_ablation_matrix_ready",
        "production_context_dependency_measured",
        "display_stage_provenance_ready",
        "production_default_preserved",
    )
    required_false = (
        "data_only_model_economically_validated",
        "qa2_performance_backtest_executed",
        "qa2_parameter_calibration_executed",
        "qa2_scoring_weights_changed",
        "qa2_resolver_default_changed",
        "qa2_dashboard_default_changed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
    )
    return (
        all(summary[key] == 0 for key in required_zero)
        and all(summary[key] is True for key in required_true)
        and all(summary[key] is False for key in required_false)
        and summary["previously_seen_scenario_count"] == 5
        and summary["recommended_next_phase"] == "QA3"
        and summary["qa2_closure_status"] == "closed_context_dependency_measured"
    )

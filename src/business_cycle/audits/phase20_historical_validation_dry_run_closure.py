"""Phase 20 controlled historical validation dry-run closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_validation_dry_run_results import (
    summarize_historical_validation_dry_run_results,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase19_validation_execution_readiness_closure import (
    summarize_phase19_validation_execution_readiness_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_historical_dry_run_freeze import (
    summarize_shadow_historical_dry_run_freeze,
)
from business_cycle.validation.historical_validation_dry_run import (
    summarize_historical_validation_dry_run,
)


DEFAULT_PHASE20_CLOSURE_PATH = Path(
    "specs/audits/phase20_historical_validation_dry_run_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_label_blind_historical_dry_run_results_generated_no_metrics"
)


def summarize_phase20_historical_validation_dry_run_closure(
    path: str | Path = DEFAULT_PHASE20_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    dry_run = summarize_historical_validation_dry_run()
    result_registry = summarize_historical_validation_dry_run_results()
    freeze = summarize_shadow_historical_dry_run_freeze()
    phase19 = summarize_phase19_validation_execution_readiness_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "20",
        "phase_id": 20,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C5_HISTORICAL_REPLAY_AND_BACKTEST",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W6_HISTORICAL_REPLAY",
            "W7_DATA_LINEAGE",
            "W8_BACKTEST_RESEARCH",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "historical_accuracy_metrics_not_computed",
            "economic_performance_not_computed",
            "holdout_not_registered",
            "candidate_model_disabled",
        ],
        "semantic_drift_count": 0,
        "historical_validation_dry_run_contract_ready": dry_run[
            "historical_validation_dry_run_contract_ready"
        ],
        "historical_validation_dry_run_executed": dry_run[
            "historical_validation_dry_run_executed"
        ],
        "scenario_count": dry_run["scenario_count"],
        "scenario_dry_run_result_count": dry_run[
            "scenario_dry_run_result_count"
        ],
        "locked_execution_plan_used": dry_run["locked_execution_plan_used"],
        "label_blind_execution_verified": dry_run[
            "label_blind_execution_verified"
        ],
        "label_used_by_runtime_count": dry_run["label_used_by_runtime_count"],
        "model_execution_count": dry_run["model_execution_count"],
        "real_historical_validation_executed": dry_run[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": dry_run[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": dry_run[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": dry_run["metric_computation_enabled"],
        "backtest_execution_enabled": dry_run["backtest_execution_enabled"],
        "holdout_registered": dry_run["holdout_registered"],
        "candidate_selection_enabled": dry_run["candidate_selection_enabled"],
        "candidate_phase_emitted": dry_run["candidate_phase_emitted"],
        "current_phase_emitted": dry_run["current_phase_emitted"],
        "prohibited_result_field_count": dry_run[
            "prohibited_result_field_count"
        ],
        "production_behavior_change_count": dry_run[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": dry_run[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": dry_run[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": dry_run["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": dry_run[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": dry_run["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "alpha16_freeze_hash_valid": freeze["alpha16_freeze_hash_valid"],
        "alpha15_parent_preserved": freeze["alpha15_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": "dry_run_results_generated_no_metrics",
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 21,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase20_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase20_generates_label_blind_dry_run_artifacts_without_metrics"
        ),
        "dry_run": dry_run,
        "result_registry": result_registry,
        "freeze": freeze,
        "phase19_closure": phase19,
        "qa12_closure": qa12,
        "leakage": leakage,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["result_registry"][
            "historical_validation_dry_run_result_registry_ready"
        ]
        is True
        and summary["freeze"]["historical_dry_run_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase19_closure"]["result"] == "passed"
        and summary["qa12_closure"]["result"] == "passed"
        and summary["qa12_closure"]["real_registry_record_count"] == 0
        and summary["qa12_closure"]["real_registry_write_attempt_count"] == 0
        and summary["qa12_closure"]["prospective_protocol_started"] is False
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase20_historical_validation_dry_run_closure"
    ]["expected"]

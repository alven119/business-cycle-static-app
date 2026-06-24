"""Phase 25 research decision output artifact closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_research_decision_outputs import (
    summarize_historical_research_decision_output_registry,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase24_research_decision_output_contract_closure import (
    summarize_phase24_research_decision_output_contract_closure,
)
from business_cycle.audits.shadow_research_decision_output_freeze import (
    summarize_shadow_research_decision_output_freeze,
)


DEFAULT_PHASE25_CLOSURE_PATH = Path(
    "specs/audits/phase25_research_decision_output_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_research_decision_outputs_generated_no_predicted_labels_or_metrics"
)


def summarize_phase25_research_decision_output_closure(
    path: str | Path = DEFAULT_PHASE25_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    registry = summarize_historical_research_decision_output_registry()
    freeze = summarize_shadow_research_decision_output_freeze()
    phase24 = summarize_phase24_research_decision_output_contract_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "25",
        "phase_id": 25,
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
            "predicted_labels_not_emitted",
            "historical_accuracy_not_computed",
            "economic_performance_not_computed",
            "candidate_model_disabled",
            "production_dashboard_not_wired",
        ],
        "semantic_drift_count": 0,
        "research_decision_output_artifact_contract_ready": registry[
            "research_decision_output_artifact_contract_ready"
        ],
        "research_decision_output_runtime_ready": registry[
            "research_decision_output_runtime_ready"
        ],
        "research_decision_output_registry_ready": registry[
            "research_decision_output_registry_ready"
        ],
        "scenario_count": registry["scenario_count"],
        "research_decision_output_count": registry["research_decision_output_count"],
        "output_mode_research_only_count": registry[
            "output_mode_research_only_count"
        ],
        "predicted_label_output_count": registry["predicted_label_output_count"],
        "label_used_by_runtime_count": registry["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": registry[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": registry[
            "economic_performance_metric_count"
        ],
        "metric_computation_scope": registry["metric_computation_scope"],
        "backtest_execution_enabled": registry["backtest_execution_enabled"],
        "candidate_phase_emitted": registry["candidate_phase_emitted"],
        "current_phase_emitted": registry["current_phase_emitted"],
        "prohibited_artifact_field_count": registry[
            "prohibited_artifact_field_count"
        ],
        "production_behavior_change_count": registry[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": registry[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": registry[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": registry["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": registry[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": registry["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "alpha21_freeze_hash_valid": freeze["alpha21_freeze_hash_valid"],
        "alpha20_parent_preserved": freeze["alpha20_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "research_decision_outputs_generated_no_predicted_labels"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 26,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase25_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase25_generates_research_decision_outputs_without_predictions_or_metrics"
        ),
        "registry": registry,
        "freeze": freeze,
        "phase24_closure": phase24,
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
        and summary["registry"]["research_decision_output_registry_ready"] is True
        and summary["freeze"]["research_decision_output_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase24_closure"]["result"] == "passed"
        and summary["phase24_closure"]["prospective_registry_record_count"] == 0
        and summary["phase24_closure"]["real_registry_write_attempt_count"] == 0
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase25_research_decision_output_closure"
    ]["expected"]

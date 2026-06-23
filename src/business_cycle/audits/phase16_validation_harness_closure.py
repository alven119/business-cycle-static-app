"""Phase 16 validation harness scaffolding closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase15_validation_protocol_closure import (
    summarize_phase15_validation_protocol_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_validation_harness_freeze import (
    summarize_shadow_validation_harness_freeze,
)
from business_cycle.validation.validation_harness import (
    summarize_validation_harness_dry_run,
)


DEFAULT_PHASE16_CLOSURE_PATH = Path(
    "specs/audits/phase16_validation_harness_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_validation_harness_scaffolded_synthetic_dry_run_only_no_validation_execution"
)


def summarize_phase16_validation_harness_closure(
    path: str | Path = DEFAULT_PHASE16_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    harness = summarize_validation_harness_dry_run()
    freeze = summarize_shadow_validation_harness_freeze()
    phase15 = summarize_phase15_validation_protocol_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "16",
        "phase_id": 16,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C5_HISTORICAL_REPLAY_AND_BACKTEST",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W8_BACKTEST_RESEARCH",
            "W13_MODEL_GOVERNANCE",
            "W14_PROSPECTIVE_MONITORING",
        ],
        "deferred_capability_gaps": [
            "real_historical_validation_not_executed",
            "economic_validation_not_started",
            "metrics_disabled",
            "holdout_not_registered",
        ],
        "semantic_drift_count": 0,
        "validation_harness_contract_ready": harness[
            "validation_harness_contract_ready"
        ],
        "validation_harness_runtime_ready": harness[
            "validation_harness_runtime_ready"
        ],
        "validation_artifact_contract_ready": harness[
            "validation_artifact_contract_ready"
        ],
        "synthetic_fixture_count": harness["synthetic_fixture_count"],
        "synthetic_dry_run_executed": harness["synthetic_dry_run_executed"],
        "real_historical_validation_executed": harness[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": harness[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": harness[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": harness["metric_computation_enabled"],
        "backtest_execution_enabled": harness["backtest_execution_enabled"],
        "holdout_registered": harness["holdout_registered"],
        "candidate_selection_enabled": harness["candidate_selection_enabled"],
        "candidate_phase_emitted": harness["candidate_phase_emitted"],
        "current_phase_emitted": harness["current_phase_emitted"],
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": harness[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": harness[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": harness["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": harness[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": harness["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "alpha12_freeze_hash_valid": freeze["alpha12_freeze_hash_valid"],
        "alpha11_parent_preserved": freeze["alpha11_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": "not_started",
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 17,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase16_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase16_scaffolds_validation_harness_synthetic_dry_run_only"
        ),
        "harness": harness,
        "freeze": freeze,
        "phase15_closure": phase15,
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
        summary["synthetic_fixture_count"] > 0
        and summary["semantic_drift_count"] == 0
        and summary["freeze"]["validation_harness_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase15_closure"]["result"] == "passed"
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
        "phase16_validation_harness_closure"
    ]["expected"]

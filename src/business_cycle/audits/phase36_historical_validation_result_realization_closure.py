"""Phase 36 historical validation result realization closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase36_historical_validation_result_realization import (
    summarize_phase36_historical_validation_result_realization,
)
from business_cycle.audits.shadow_historical_validation_result_realization_freeze import (
    summarize_shadow_historical_validation_result_realization_freeze,
)


DEFAULT_PHASE36_CLOSURE_PATH = Path(
    "specs/audits/phase36_historical_validation_result_realization_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_historical_validation_results_generated_remaining_recession_recovery_"
    "genuine_non_comparable"
)


@lru_cache(maxsize=1)
def summarize_phase36_historical_validation_result_realization_closure(
    path: str | Path = DEFAULT_PHASE36_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase36_historical_validation_result_realization()
    freeze = summarize_shadow_historical_validation_result_realization_freeze()
    development_next_phase: int | str = (
        37
        if audit["post_comparable_scenario_count"]
        > audit["pre_comparable_scenario_count"]
        else "PHASE_36_REVIEW"
    )
    summary = {
        "phase": "36",
        "phase_id": 36,
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
            "remaining recession/recovery scenarios require complete evidence",
            "economic performance metrics not computed",
            "portfolio backtest not executed",
            "candidate model disabled",
            "current phase disabled",
            "production dashboard not wired",
        ],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "historical_validation_result_runtime_ready",
                "recession_recovery_comparability_unblock_ready",
                "post_validation_result_rerun_ready",
                "attempted_fix_iteration_count",
                "scenario_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "comparable_scenario_count",
                "historical_validation_result_artifact_count",
                "safe_fixable_recession_recovery_gap_count",
                "unresolved_safe_fixable_recession_recovery_gap_count",
                "all_remaining_recession_recovery_non_comparable_reasons_are_genuine",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
                "scenario_promoted_by_taxonomy_only_count",
                "scenario_promoted_by_modern_proxy_count",
                "evidence_rule_modified_count",
                "predicted_mapping_rule_modified_count",
                "formal_decision_contract_modified_count",
                "threshold_modified_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "metric_computation_scope",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "phase36_validation_progress_status",
            )
        },
        "alpha32_freeze_hash_valid": freeze["alpha32_freeze_hash_valid"],
        "alpha31_parent_preserved": freeze["alpha31_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "historical_validation_results_generated_research_only_no_performance"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": development_next_phase,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase36_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase36_generates_research_only_validation_result_summary_and_"
            "documents_remaining_recession_recovery_comparability_limits"
        ),
        "remaining_non_comparable_evidence": audit[
            "remaining_non_comparable_evidence"
        ],
        "comparable_scenario_ids": audit["comparable_scenario_ids"],
        "recession_recovery_scenario_profiles": audit[
            "recession_recovery_scenario_profiles"
        ],
        "historical_validation_result_artifact": audit[
            "historical_validation_result_artifact"
        ],
        "audit": audit,
        "freeze": freeze,
        "phase35_parent_freeze": freeze["parent_freeze"],
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    acceptable_stop = (
        summary["post_comparable_scenario_count"] == 2
        and summary["attempted_fix_iteration_count"] >= 2
        and summary[
            "all_remaining_recession_recovery_non_comparable_reasons_are_genuine"
        ]
        is True
    )
    preferred_stop = (
        summary["post_comparable_scenario_count"]
        > summary["pre_comparable_scenario_count"]
    )
    return (
        summary["semantic_drift_count"] == 0
        and (preferred_stop or acceptable_stop)
        and summary["audit"]["result"] == "passed"
        and summary["freeze"][
            "historical_validation_result_realization_freeze_ready"
        ]
        is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase35_parent_freeze"][
            "historical_comparability_realization_freeze_ready"
        ]
        is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase36_historical_validation_result_realization_closure"
    ]["expected"]

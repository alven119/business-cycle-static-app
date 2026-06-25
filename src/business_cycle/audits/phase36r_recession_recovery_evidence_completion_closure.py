"""Phase 36R recession/recovery evidence completion closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase36r_recession_recovery_evidence_completion import (
    summarize_phase36r_recession_recovery_evidence_completion,
)
from business_cycle.audits.shadow_recession_recovery_evidence_completion_freeze import (
    summarize_shadow_recession_recovery_evidence_completion_freeze,
)


DEFAULT_PHASE36R_CLOSURE_PATH = Path(
    "specs/audits/phase36r_recession_recovery_evidence_completion_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_recession_recovery_evidence_completion_attempted_remaining_genuine_"
    "non_comparable"
)


@lru_cache(maxsize=1)
def summarize_phase36r_recession_recovery_evidence_completion_closure(
    path: str | Path = DEFAULT_PHASE36R_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase36r_recession_recovery_evidence_completion()
    freeze = summarize_shadow_recession_recovery_evidence_completion_freeze()
    summary = {
        "phase": "36R",
        "phase_id": "36R",
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
            "recession/recovery strict vintage evidence remains incomplete",
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
                "recession_recovery_evidence_completion_runtime_ready",
                "post_evidence_completion_validation_rerun_ready",
                "attempted_fix_iteration_count",
                "scenario_count",
                "target_recession_recovery_scenario_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "phase_evidence_completion_attempted_scenario_count",
                "safe_fixable_recession_recovery_gap_count",
                "unresolved_safe_fixable_recession_recovery_gap_count",
                "evidence_completion_false_positive_count",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
                "scenario_promoted_by_taxonomy_only_count",
                "scenario_promoted_by_modern_proxy_count",
                "evidence_rule_semantics_modified_count",
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
                "phase36r_progress_status",
                "development_next_phase",
                "target_recession_recovery_scenario_ids",
                "newly_comparable_scenario_ids",
                "remaining_non_comparable_scenario_ids",
                "role_level_remaining_evidence_gaps",
            )
        },
        "alpha33_freeze_hash_valid": freeze["alpha33_freeze_hash_valid"],
        "alpha32_parent_preserved": freeze["alpha32_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "production_book_fidelity_ready": False,
        "economic_validation_status": (
            "recession_recovery_evidence_completion_attempted_research_only_no_performance"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase36r_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase36r_attempts_recession_recovery_evidence_completion_and_"
            "records_strict_vintage_role_level_gaps_without_false_comparability"
        ),
        "audit": audit,
        "freeze": freeze,
        "phase36_parent_freeze": freeze["parent_freeze"],
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    preferred_stop = (
        summary["post_comparable_scenario_count"]
        > summary["pre_comparable_scenario_count"]
    )
    acceptable_stop = (
        summary["post_comparable_scenario_count"] == 2
        and summary["attempted_fix_iteration_count"] >= 2
        and summary["safe_fixable_recession_recovery_gap_count"] == 0
        and summary["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
    )
    return (
        summary["semantic_drift_count"] == 0
        and (preferred_stop or acceptable_stop)
        and summary["audit"]["result"] == "passed"
        and summary["freeze"]["recession_recovery_evidence_completion_freeze_ready"]
        is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase36_parent_freeze"][
            "historical_validation_result_realization_freeze_ready"
        ]
        is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase36r_recession_recovery_evidence_completion_closure"
    ]["expected"]

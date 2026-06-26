"""Phase 37 recession/recovery PIT remediation closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase37_recession_recovery_pit_remediation import (
    summarize_phase37_recession_recovery_pit_remediation,
)
from business_cycle.audits.shadow_recession_recovery_pit_remediation_freeze import (
    summarize_shadow_recession_recovery_pit_remediation_freeze,
)


DEFAULT_PHASE37_CLOSURE_PATH = Path(
    "specs/audits/phase37_recession_recovery_pit_remediation_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_recession_recovery_pit_remediation_reduced_pit_gaps_no_false_"
    "comparability"
)


@lru_cache(maxsize=1)
def summarize_phase37_recession_recovery_pit_remediation_closure(
    path: str | Path = DEFAULT_PHASE37_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase37_recession_recovery_pit_remediation()
    freeze = summarize_shadow_recession_recovery_pit_remediation_freeze()
    summary = {
        "phase": "37",
        "phase_id": 37,
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
            "recession confirmation PIT cache remains unavailable for five roles",
            "early dotcom claims history remains officially insufficient",
            "weekly claims noise-filter rule remains unresolved by data remediation",
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
                "recession_recovery_pit_gap_matrix_ready",
                "recession_recovery_pit_remediation_runtime_ready",
                "controlled_pit_backfill_ready",
                "post_pit_remediation_validation_rerun_ready",
                "attempted_fix_iteration_count",
                "scenario_count",
                "target_recession_recovery_scenario_count",
                "pre_insufficient_point_in_time_role_gap_count",
                "post_insufficient_point_in_time_role_gap_count",
                "safe_fixable_pit_gap_count",
                "unresolved_safe_fixable_pit_gap_count",
                "official_history_insufficient_gap_count",
                "genuine_source_unavailable_gap_count",
                "rule_unresolved_gap_count",
                "revised_fallback_used_count",
                "proxy_fallback_used_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "cache_remediated_pit_role_gap_count",
                "cache_remediated_pit_role_ids",
                "newly_comparable_scenario_ids",
                "remaining_non_comparable_scenario_ids",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
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
                "phase37_progress_status",
                "development_next_phase",
            )
        },
        "alpha34_freeze_hash_valid": freeze["alpha34_freeze_hash_valid"],
        "alpha33_parent_preserved": freeze["alpha33_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "production_book_fidelity_ready": False,
        "economic_validation_status": (
            "recession_recovery_pit_remediation_attempted_research_only_no_performance"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase37_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase37_reduces_strict_vintage_input_gaps_for_recession_recovery_"
            "research_validation_without_false_comparability_or_production_wiring"
        ),
        "audit": audit,
        "freeze": freeze,
        "phase36r_parent_freeze": freeze["parent_freeze"],
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["post_insufficient_point_in_time_role_gap_count"]
        < summary["pre_insufficient_point_in_time_role_gap_count"]
        and summary["post_comparable_scenario_count"]
        >= summary["pre_comparable_scenario_count"]
        and summary["false_comparability_count"] == 0
        and summary["audit"]["result"] == "passed"
        and summary["freeze"]["recession_recovery_pit_remediation_freeze_ready"]
        is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase36r_parent_freeze"][
            "recession_recovery_evidence_completion_freeze_ready"
        ]
        is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase37_recession_recovery_pit_remediation_closure"
    ]["expected"]

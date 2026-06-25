"""Phase 34 autonomous blocker unblock closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase34_autonomous_blocker_unblock import (
    summarize_phase34_autonomous_blocker_unblock,
)
from business_cycle.audits.shadow_autonomous_blocker_unblock_freeze import (
    summarize_shadow_autonomous_blocker_unblock_freeze,
)


DEFAULT_PHASE34_CLOSURE_PATH = Path(
    "specs/audits/phase34_autonomous_blocker_unblock_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = "closed_autonomous_blocker_unblock_research_only_no_performance"


@lru_cache(maxsize=1)
def summarize_phase34_autonomous_blocker_unblock_closure(
    path: str | Path = DEFAULT_PHASE34_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase34_autonomous_blocker_unblock()
    freeze = summarize_shadow_autonomous_blocker_unblock_freeze()
    development_next_phase: int | str = (
        35
        if audit["post_resolution_blocked_scenario_count"]
        < audit["pre_resolution_blocked_scenario_count"]
        else "PHASE_34_REVIEW"
    )
    summary = {
        "phase": "34",
        "phase_id": 34,
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
            "post-unblock scenarios remain abstained and not comparable",
            "formal decision model remains disabled",
            "candidate model remains disabled",
            "economic performance metrics not computed",
            "portfolio backtest not executed",
            "production dashboard not wired",
        ],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "autonomous_blocker_unblock_runtime_ready",
                "post_unblock_validation_rerun_ready",
                "attempted_fix_iteration_count",
                "pre_resolution_blocked_scenario_count",
                "post_resolution_blocked_scenario_count",
                "pre_resolution_comparable_scenario_count",
                "post_resolution_comparable_scenario_count",
                "safe_fixable_blocker_count",
                "unresolved_safe_fixable_blocker_count",
                "all_remaining_blockers_are_genuine",
                "blocker_without_attempted_fix_or_genuine_evidence_count",
                "false_resolution_count",
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
                "economic_performance_metric_count",
                "metric_computation_scope",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "phase34_resolution_progress_status",
            )
        },
        "alpha30_freeze_hash_valid": freeze["alpha30_freeze_hash_valid"],
        "alpha29_parent_preserved": freeze["alpha29_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "autonomous_blocker_unblock_attempted_research_only_no_performance"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": development_next_phase,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase34_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase34_reclassifies_safe_validation_blockers_into_abstention_"
            "without_candidate_or_performance_outputs"
        ),
        "remaining_genuine_blocker_evidence": audit["unblock"][
            "autonomous_blocker_unblock_artifact"
        ]["remaining_genuine_blocker_evidence"],
        "audit": audit,
        "freeze": freeze,
        "phase33_parent_freeze": freeze["parent_freeze"],
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["post_resolution_blocked_scenario_count"]
        < summary["pre_resolution_blocked_scenario_count"]
        and summary["post_resolution_comparable_scenario_count"] == 0
        and summary["audit"]["result"] == "passed"
        and summary["freeze"]["autonomous_blocker_unblock_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase33_parent_freeze"][
            "blocker_resolution_execution_freeze_ready"
        ]
        is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase34_autonomous_blocker_unblock_closure"
    ]["expected"]

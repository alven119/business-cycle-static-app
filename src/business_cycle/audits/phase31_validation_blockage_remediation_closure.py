"""Phase 31 validation blockage remediation closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.shadow_validation_blockage_remediation_freeze import (
    summarize_shadow_validation_blockage_remediation_freeze,
)
from business_cycle.audits.validation_blockage_remediation_readiness import (
    summarize_validation_blockage_remediation_readiness,
)


DEFAULT_PHASE31_CLOSURE_PATH = Path(
    "specs/audits/phase31_validation_blockage_remediation_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_validation_blockage_remediation_reviewed_safe_fixes_only_no_performance"
)


@lru_cache(maxsize=1)
def summarize_phase31_validation_blockage_remediation_closure(
    path: str | Path = DEFAULT_PHASE31_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    readiness = summarize_validation_blockage_remediation_readiness()
    freeze = summarize_shadow_validation_blockage_remediation_freeze()
    summary = {
        "phase": "31",
        "phase_id": 31,
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
            "genuine validation blockers remain unresolved",
            "economic performance metrics not computed",
            "portfolio backtest not executed",
            "candidate model disabled",
            "current phase disabled",
            "production dashboard not wired",
        ],
        "semantic_drift_count": 0,
        **{
            key: readiness[key]
            for key in (
                "validation_blockage_remediation_contract_ready",
                "validation_blockage_remediation_runtime_ready",
                "validation_blockage_remediation_readiness_ready",
                "scenario_count",
                "pre_remediation_blocked_scenario_count",
                "post_remediation_blocked_scenario_count",
                "reviewed_blocker_count",
                "safe_remediation_candidate_count",
                "safe_remediation_executed_count",
                "genuine_blocker_count",
                "unresolved_blocker_count",
                "false_resolution_count",
                "remediation_action_executed",
                "rule_modified_count",
                "evidence_rule_modified_count",
                "mapping_rule_modified_count",
                "threshold_modified_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "metric_computation_scope",
                "backtest_execution_enabled",
                "label_used_by_runtime_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
            )
        },
        "alpha27_freeze_hash_valid": freeze["alpha27_freeze_hash_valid"],
        "alpha26_parent_preserved": freeze["alpha26_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "validation_blockage_remediation_reviewed_safe_fixes_only_no_performance"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 32,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase31_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase31_reviews_validation_blockers_without_false_resolution"
        ),
        "readiness": readiness,
        "freeze": freeze,
        "phase30_parent_freeze": freeze["parent_freeze"],
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["readiness"]["validation_blockage_remediation_readiness_ready"]
        is True
        and summary["freeze"]["validation_blockage_remediation_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase30_parent_freeze"][
            "validation_blockage_diagnostics_freeze_ready"
        ]
        is True
        and summary["phase30_parent_freeze"]["economic_performance_metric_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase31_validation_blockage_remediation_closure"
    ]["expected"]

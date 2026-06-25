"""Phase 34 autonomous validation blocker unblock audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.autonomous_blocker_unblock import (
    summarize_autonomous_blocker_unblock,
)
from business_cycle.validation.post_unblock_validation_rerun import (
    summarize_post_unblock_validation_rerun,
)


DEFAULT_PHASE34_AUDIT_PATH = Path(
    "specs/audits/phase34_autonomous_blocker_unblock.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase34_autonomous_blocker_unblock(
    path: str | Path = DEFAULT_PHASE34_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    unblock = summarize_autonomous_blocker_unblock()
    rerun = summarize_post_unblock_validation_rerun()
    summary = {
        "phase": "34",
        **{
            key: unblock[key]
            for key in (
                "autonomous_blocker_unblock_runtime_ready",
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
        "post_unblock_validation_rerun_ready": rerun[
            "post_unblock_validation_rerun_ready"
        ],
        "updated_predicted_label_artifact_count": rerun[
            "updated_predicted_label_artifact_count"
        ],
        "updated_comparison_artifact_count": rerun[
            "updated_comparison_artifact_count"
        ],
        "updated_blockage_diagnostic_scenario_count": rerun[
            "updated_blockage_diagnostic_scenario_count"
        ],
        "updated_scenario_trace_count": rerun["updated_scenario_trace_count"],
        "unblock": unblock,
        "rerun": rerun,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        summary["attempted_fix_iteration_count"]
        >= expected["attempted_fix_iteration_count_minimum"]
        and summary["post_resolution_blocked_scenario_count"]
        <= expected["pre_resolution_blocked_scenario_count"]
        and all(
            summary[key] == value
            for key, value in expected.items()
            if key not in {"attempted_fix_iteration_count_minimum"}
        )
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase34_autonomous_blocker_unblock"
    ]["expected"]

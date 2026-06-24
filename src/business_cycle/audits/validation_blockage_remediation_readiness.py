"""Phase 31 validation blockage remediation readiness audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase30_validation_blockage_diagnostics_closure import (
    summarize_phase30_validation_blockage_diagnostics_closure,
)
from business_cycle.validation.validation_blockage_remediation import (
    summarize_validation_blockage_remediation,
)


DEFAULT_REMEDIATION_READINESS_PATH = Path(
    "specs/audits/validation_blockage_remediation_readiness.yaml"
)


@lru_cache(maxsize=1)
def summarize_validation_blockage_remediation_readiness(
    path: str | Path = DEFAULT_REMEDIATION_READINESS_PATH,
) -> dict[str, Any]:
    spec = _load_spec(path)
    expected = spec["expected_counters"]
    remediation = summarize_validation_blockage_remediation()
    phase30 = summarize_phase30_validation_blockage_diagnostics_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "31",
        "readiness_id": spec["readiness_id"],
        "readiness_version": spec["readiness_version"],
        **{
            key: remediation[key]
            for key in (
                "validation_blockage_remediation_contract_ready",
                "validation_blockage_remediation_runtime_ready",
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
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "remediation": remediation,
        "phase30_closure": phase30,
        "leakage": leakage,
    }
    summary["validation_blockage_remediation_readiness_ready"] = _matches_expected(
        summary,
        expected,
    )
    return summary


def _matches_expected(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "validation_blockage_remediation_readiness_ready":
            continue
        if summary.get(key) != value:
            return False
    return (
        summary["phase30_closure"]["result"] == "passed"
        and summary["phase30_closure"]["blocked_scenario_count"] == 5
        and summary["remediation"]["false_resolution_count"] == 0
        and (
            summary["safe_remediation_executed_count"]
            == summary["safe_remediation_candidate_count"]
        )
        and (
            summary["genuine_blocker_count"]
            + summary["safe_remediation_candidate_count"]
            == summary["reviewed_blocker_count"]
        )
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "validation_blockage_remediation_readiness"
    ]

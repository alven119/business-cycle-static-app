"""Phase 32 validation blocker resolution readiness."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.genuine_validation_blocker_work_packages import (
    summarize_genuine_validation_blocker_work_packages,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase31_validation_blockage_remediation_closure import (
    summarize_phase31_validation_blockage_remediation_closure,
)


DEFAULT_RESOLUTION_READINESS_PATH = Path(
    "specs/audits/validation_blocker_resolution_readiness.yaml"
)


@lru_cache(maxsize=1)
def summarize_validation_blocker_resolution_readiness(
    path: str | Path = DEFAULT_RESOLUTION_READINESS_PATH,
) -> dict[str, Any]:
    spec = _load_spec(path)
    expected = spec["expected_counters"]
    packages = summarize_genuine_validation_blocker_work_packages()
    phase31 = summarize_phase31_validation_blockage_remediation_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "32",
        "readiness_id": spec["readiness_id"],
        "readiness_version": spec["readiness_version"],
        **{
            key: packages[key]
            for key in (
                "genuine_blocker_resolution_protocol_ready",
                "genuine_blocker_work_package_registry_ready",
                "reviewed_genuine_blocker_count",
                "work_package_count",
                "blocker_without_work_package_count",
                "work_package_without_source_blocker_count",
                "work_package_without_allowed_action_count",
                "work_package_without_prohibited_action_count",
                "work_package_without_completion_gate_count",
                "false_resolution_count",
                "blocker_resolution_executed",
                "scenario_promoted_to_comparable_count",
                "evidence_rule_modified_count",
                "predicted_mapping_rule_modified_count",
                "formal_decision_contract_modified_count",
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
        "work_packages": packages,
        "phase31_closure": phase31,
        "leakage": leakage,
    }
    summary["validation_blocker_resolution_readiness_ready"] = _matches_expected(
        summary,
        expected,
    )
    return summary


def _matches_expected(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "validation_blocker_resolution_readiness_ready":
            continue
        if summary.get(key) != value:
            return False
    return (
        summary["work_package_count"] >= expected["reviewed_genuine_blocker_count"]
        and summary["phase31_closure"]["result"] == "passed"
        and summary["phase31_closure"]["genuine_blocker_count"] == 5
        and summary["phase31_closure"]["false_resolution_count"] == 0
        and summary["work_packages"]["genuine_blocker_work_package_registry_ready"]
        is True
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "validation_blocker_resolution_readiness"
    ]

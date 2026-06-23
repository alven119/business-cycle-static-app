"""Phase 17 historical validation manifest readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


DEFAULT_READINESS_PATH = Path("specs/audits/historical_validation_readiness.yaml")


def load_historical_validation_readiness(
    path: str | Path = DEFAULT_READINESS_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation readiness must be a mapping")
    readiness = payload.get("historical_validation_readiness")
    if not isinstance(readiness, dict):
        raise ValueError("historical_validation_readiness must be a mapping")
    return readiness


def summarize_historical_validation_readiness(
    path: str | Path = DEFAULT_READINESS_PATH,
) -> dict[str, Any]:
    registry = load_historical_validation_readiness(path)
    manifest = summarize_historical_validation_manifest()
    label_policy = summarize_validation_label_policy()
    gates = registry["readiness_gates"]
    execution = registry["execution_counters"]
    safety = registry["safety_counters"]
    no_execution = (
        execution["real_historical_validation_executed"] is False
        and execution["historical_accuracy_metric_count"] == 0
        and execution["economic_performance_metric_count"] == 0
        and execution["metric_computation_enabled"] is False
        and execution["backtest_execution_enabled"] is False
        and execution["holdout_registered"] is False
        and execution["candidate_selection_enabled"] is False
        and execution["candidate_phase_emitted"] is False
        and execution["current_phase_emitted"] is False
        and execution["prospective_registry_record_count"] == 0
        and execution["real_registry_write_attempt_count"] == 0
    )
    ready = (
        gates["historical_validation_manifest_contract_ready"] is True
        and manifest["historical_validation_manifest_contract_ready"] is True
        and gates["historical_validation_scenario_manifest_ready"] is True
        and manifest["historical_validation_scenario_manifest_ready"] is True
        and gates["validation_label_policy_ready"] is True
        and label_policy["validation_label_policy_ready"] is True
        and gates["point_in_time_requirement_present"] is True
        and manifest["point_in_time_requirement_present"] is True
        and gates["label_provenance_complete"] is True
        and label_policy["label_provenance_complete"] is True
        and gates["label_runtime_usage_prohibited"] is True
        and label_policy["label_runtime_usage_prohibited"] is True
        and gates["no_tuning_after_manifest_rule_present"] is True
        and manifest["no_tuning_after_manifest_rule_present"] is True
        and no_execution
        and all(value == 0 for value in safety.values())
    )
    return {
        "phase": "17",
        "historical_validation_readiness_ready": ready,
        "historical_validation_manifest_contract_ready": manifest[
            "historical_validation_manifest_contract_ready"
        ],
        "historical_validation_scenario_manifest_ready": manifest[
            "historical_validation_scenario_manifest_ready"
        ],
        "validation_label_policy_ready": label_policy[
            "validation_label_policy_ready"
        ],
        "scenario_count": manifest["scenario_count"],
        "point_in_time_requirement_present": manifest[
            "point_in_time_requirement_present"
        ],
        "label_provenance_complete": (
            manifest["label_provenance_complete"]
            and label_policy["label_provenance_complete"]
        ),
        "label_runtime_usage_prohibited": (
            manifest["label_runtime_usage_prohibited"]
            and label_policy["label_runtime_usage_prohibited"]
        ),
        "no_tuning_after_manifest_rule_present": manifest[
            "no_tuning_after_manifest_rule_present"
        ],
        "real_historical_validation_executed": execution[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": execution[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": execution[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": execution["metric_computation_enabled"],
        "backtest_execution_enabled": execution["backtest_execution_enabled"],
        "holdout_registered": execution["holdout_registered"],
        "candidate_selection_enabled": execution["candidate_selection_enabled"],
        "candidate_phase_emitted": execution["candidate_phase_emitted"],
        "current_phase_emitted": execution["current_phase_emitted"],
        "prospective_registry_record_count": execution[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": execution[
            "real_registry_write_attempt_count"
        ],
        "production_behavior_change_count": safety["production_behavior_change_count"],
        "numeric_weight_added_count": safety["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": safety[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": safety["role_count_voting_added_count"],
        "historical_tuning_leakage_count": safety[
            "historical_tuning_leakage_count"
        ],
        "registry": registry,
        "manifest": manifest,
        "label_policy": label_policy,
    }

"""Phase 30 historical validation blockage readiness audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.render.research_artifact_explorer import (
    summarize_research_artifact_explorer,
)
from business_cycle.validation.historical_validation_blockage_diagnostics import (
    summarize_historical_validation_blockage_diagnostics,
)
from business_cycle.validation.scenario_validation_trace import (
    summarize_scenario_validation_trace,
)


DEFAULT_BLOCKAGE_READINESS_PATH = Path(
    "specs/audits/historical_validation_blockage_readiness.yaml"
)


@lru_cache(maxsize=1)
def summarize_historical_validation_blockage_readiness(
    path: str | Path = DEFAULT_BLOCKAGE_READINESS_PATH,
) -> dict[str, Any]:
    spec = _load_spec(path)
    expected = spec["expected_counters"]
    trace = summarize_scenario_validation_trace()
    diagnostics = summarize_historical_validation_blockage_diagnostics()
    explorer = summarize_research_artifact_explorer()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "30",
        "readiness_id": spec["readiness_id"],
        "readiness_version": spec["readiness_version"],
        "historical_validation_blockage_diagnostics_contract_ready": diagnostics[
            "historical_validation_blockage_diagnostics_contract_ready"
        ],
        "historical_validation_blockage_diagnostics_runtime_ready": diagnostics[
            "historical_validation_blockage_diagnostics_runtime_ready"
        ],
        "scenario_validation_trace_contract_ready": trace[
            "scenario_validation_trace_contract_ready"
        ],
        "scenario_validation_trace_runtime_ready": trace[
            "scenario_validation_trace_runtime_ready"
        ],
        "research_artifact_explorer_contract_ready": explorer[
            "research_artifact_explorer_contract_ready"
        ],
        "research_artifact_explorer_runtime_ready": explorer[
            "research_artifact_explorer_runtime_ready"
        ],
        "scenario_count": diagnostics["scenario_count"],
        "scenario_trace_count": trace["scenario_trace_count"],
        "blockage_diagnostic_scenario_count": diagnostics[
            "blockage_diagnostic_scenario_count"
        ],
        "comparable_scenario_count": diagnostics["comparable_scenario_count"],
        "non_comparable_scenario_count": diagnostics[
            "non_comparable_scenario_count"
        ],
        "abstained_scenario_count": diagnostics["abstained_scenario_count"],
        "blocked_scenario_count": diagnostics["blocked_scenario_count"],
        "taxonomy_mismatch_count": diagnostics["taxonomy_mismatch_count"],
        "blockage_reason_summary_ready": diagnostics[
            "blockage_reason_summary_ready"
        ],
        "remediation_plan_registry_ready": diagnostics[
            "remediation_plan_registry_ready"
        ],
        "remediation_action_executed": diagnostics[
            "remediation_action_executed"
        ],
        "rule_modified_count": diagnostics["rule_modified_count"],
        "mapping_rule_modified_count": diagnostics["mapping_rule_modified_count"],
        "threshold_modified_count": diagnostics["threshold_modified_count"],
        "numeric_weight_added_count": diagnostics["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": diagnostics[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": diagnostics["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "historical_accuracy_metric_count": diagnostics[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": diagnostics[
            "new_accuracy_metric_computed_count"
        ],
        "economic_performance_metric_count": diagnostics[
            "economic_performance_metric_count"
        ],
        "metric_computation_scope": diagnostics["metric_computation_scope"],
        "backtest_execution_enabled": diagnostics["backtest_execution_enabled"],
        "label_used_by_runtime_count": diagnostics["label_used_by_runtime_count"],
        "candidate_phase_emitted": diagnostics["candidate_phase_emitted"],
        "current_phase_emitted": diagnostics["current_phase_emitted"],
        "prohibited_explorer_field_count": explorer[
            "prohibited_explorer_field_count"
        ],
        "explorer_written_to_public_count": explorer[
            "explorer_written_to_public_count"
        ],
        "forbidden_repo_output_count": diagnostics["forbidden_repo_output_count"],
        "production_behavior_change_count": diagnostics[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": diagnostics[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": diagnostics[
            "real_registry_write_attempt_count"
        ],
        "trace": trace,
        "diagnostics": diagnostics,
        "explorer": explorer,
        "leakage": leakage,
    }
    summary["historical_validation_blockage_readiness_ready"] = _matches_expected(
        summary,
        expected,
    )
    return summary


def _matches_expected(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "historical_validation_blockage_readiness_ready":
            continue
        if summary.get(key) != value:
            return False
    return (
        summary["trace"]["scenario_validation_trace_runtime_ready"] is True
        and summary["diagnostics"][
            "historical_validation_blockage_diagnostics_runtime_ready"
        ]
        is True
        and summary["explorer"]["research_artifact_explorer_runtime_ready"] is True
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "historical_validation_blockage_readiness"
    ]

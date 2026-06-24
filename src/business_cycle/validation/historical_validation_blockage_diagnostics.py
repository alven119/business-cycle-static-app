"""Phase 30 historical validation blockage diagnostics."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
)
from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
)


DEFAULT_BLOCKAGE_DIAGNOSTICS_CONTRACT_PATH = Path(
    "specs/common/historical_validation_blockage_diagnostics_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase30_historical_validation_blockage_diagnostics_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"


def load_historical_validation_blockage_diagnostics_contract(
    path: str | Path = DEFAULT_BLOCKAGE_DIAGNOSTICS_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation blockage contract must map")
    contract = payload.get("historical_validation_blockage_diagnostics_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_validation_blockage_diagnostics_contract must be a mapping"
        )
    return contract


def build_historical_validation_blockage_diagnostics(
    *,
    trace_run: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if trace_run is None:
        return _build_historical_validation_blockage_diagnostics_cached()
    return _build_historical_validation_blockage_diagnostics_uncached(
        trace_run=trace_run
    )


@lru_cache(maxsize=1)
def _build_historical_validation_blockage_diagnostics_cached() -> dict[str, Any]:
    return _build_historical_validation_blockage_diagnostics_uncached(
        trace_run=build_scenario_validation_trace()
    )


def _build_historical_validation_blockage_diagnostics_uncached(
    *,
    trace_run: dict[str, Any],
) -> dict[str, Any]:
    contract = load_historical_validation_blockage_diagnostics_contract()
    metric_run = trace_run["accuracy_metric_run"]
    if not metric_run:
        metric_run = compute_historical_accuracy_metrics()
    diagnostic_artifact = _build_diagnostic_artifact(
        contract=contract,
        trace_run=trace_run,
        metric_run=metric_run,
    )
    validation = validate_historical_validation_blockage_diagnostics_artifact(
        diagnostic_artifact,
        contract=contract,
    )
    contract_validation = validate_historical_validation_blockage_diagnostics_contract(
        contract
    )
    return {
        "phase": "30",
        "run_id": RUN_ID,
        "historical_validation_blockage_diagnostics_contract_ready": (
            contract_validation["contract_schema_valid"]
        ),
        "historical_validation_blockage_diagnostics_runtime_ready": validation[
            "artifact_schema_valid"
        ],
        "scenario_count": trace_run["scenario_count"],
        "scenario_trace_count": trace_run["scenario_trace_count"],
        "blockage_diagnostic_scenario_count": len(
            diagnostic_artifact["scenario_blockage_profiles"]
        ),
        "comparable_scenario_count": diagnostic_artifact[
            "comparable_scenario_count"
        ],
        "non_comparable_scenario_count": diagnostic_artifact[
            "non_comparable_scenario_count"
        ],
        "abstained_scenario_count": diagnostic_artifact[
            "abstained_scenario_count"
        ],
        "blocked_scenario_count": diagnostic_artifact["blocked_scenario_count"],
        "taxonomy_mismatch_count": diagnostic_artifact["taxonomy_mismatch_count"],
        "blockage_reason_summary_ready": bool(
            diagnostic_artifact["blockage_reason_summary"]
        ),
        "remediation_plan_registry_ready": bool(
            diagnostic_artifact["remediation_plan_registry"]
        ),
        "remediation_action_executed": False,
        "rule_modified_count": 0,
        "mapping_rule_modified_count": 0,
        "threshold_modified_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "historical_accuracy_metric_count": metric_run[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_scope": contract["metric_computation_scope"],
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "prohibited_artifact_field_count": validation[
            "prohibited_artifact_field_count"
        ],
        "production_behavior_change_count": contract["output_restrictions"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["output_restrictions"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["output_restrictions"][
            "real_registry_write_attempt_count"
        ],
        "forbidden_repo_output_count": 0,
        "blockage_diagnostics_artifact": diagnostic_artifact,
        "artifact_validation": validation,
        "contract_validation": contract_validation,
        "trace_run": trace_run,
        "metric_run": metric_run,
        "contract": contract,
    }


@lru_cache(maxsize=1)
def summarize_historical_validation_blockage_diagnostics() -> dict[str, Any]:
    contract = load_historical_validation_blockage_diagnostics_contract()
    run = build_historical_validation_blockage_diagnostics()
    gates = contract["readiness_gates"]
    ready = (
        run["historical_validation_blockage_diagnostics_contract_ready"] is True
        and run["historical_validation_blockage_diagnostics_runtime_ready"] is True
        and run["scenario_count"] == gates["scenario_count_required"]
        and run["blockage_diagnostic_scenario_count"]
        == gates["blockage_diagnostic_scenario_count_required"]
        and run["blocked_scenario_count"]
        == gates["blocked_scenario_count_required"]
        and run["blockage_reason_summary_ready"]
        is gates["blockage_reason_summary_ready"]
        and run["remediation_plan_registry_ready"]
        is gates["remediation_plan_registry_ready"]
        and run["prohibited_artifact_field_count"]
        == gates["prohibited_artifact_field_count_required"]
        and run["remediation_action_executed"] is False
        and run["new_accuracy_metric_computed_count"] == 0
        and run["economic_performance_metric_count"] == 0
        and run["metric_computation_scope"] == "diagnostic_summary_only"
        and run["backtest_execution_enabled"] is False
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "30",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_validation_blockage_diagnostics_contract_ready": ready,
        "historical_validation_blockage_diagnostics_runtime_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "scenario_trace_count",
                "blockage_diagnostic_scenario_count",
                "comparable_scenario_count",
                "non_comparable_scenario_count",
                "abstained_scenario_count",
                "blocked_scenario_count",
                "taxonomy_mismatch_count",
                "blockage_reason_summary_ready",
                "remediation_plan_registry_ready",
                "remediation_action_executed",
                "rule_modified_count",
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
                "prohibited_artifact_field_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
            )
        },
        "blockage_diagnostics_artifact": run["blockage_diagnostics_artifact"],
        "diagnostic_run": run,
    }


def validate_historical_validation_blockage_diagnostics_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_accuracy_metric_freeze_id",
        "source_scenario_trace_contract_id",
        "artifact_version",
        "metric_computation_scope",
        "allowed_inputs",
        "prohibited_inputs",
        "allowed_artifact_fields",
        "forbidden_artifact_fields",
        "remediation_registry_policy",
        "output_restrictions",
        "output_policy",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    remediation = contract.get("remediation_registry_policy", {})
    output = contract.get("output_policy", {})
    restrictions = contract.get("output_restrictions", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "blockage_diagnostics_allowed_no_remediation_or_performance"
        and contract.get("metric_computation_scope") == "diagnostic_summary_only"
        and remediation.get("descriptive_only") is True
        and remediation.get("automatic_rule_change_allowed") is False
        and remediation.get("automatic_mapping_change_allowed") is False
        and remediation.get("threshold_change_allowed") is False
        and remediation.get("weight_change_allowed") is False
        and remediation.get("historical_result_tuning_allowed") is False
        and restrictions.get("remediation_action_executed") is False
        and restrictions.get("rule_modified_count") == 0
        and restrictions.get("mapping_rule_modified_count") == 0
        and restrictions.get("threshold_modified_count") == 0
        and restrictions.get("new_accuracy_metric_computed_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("backtest_execution_enabled") is False
        and restrictions.get("label_used_by_runtime_count") == 0
        and output.get("tmp_output_allowed") is True
        and output.get("public_output_allowed") is False
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_historical_validation_blockage_diagnostics_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_historical_validation_blockage_diagnostics_contract()
    allowed = set(contract["allowed_artifact_fields"])
    forbidden = set(contract["forbidden_artifact_fields"])
    keys = set(artifact)
    missing = allowed.difference(keys)
    unexpected = keys.difference(allowed)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden)
    remediation_items_valid = all(
        item.get("status") == "descriptive_only_not_executed"
        and item.get("requires_new_preregistered_contract") is True
        and item.get("tuning_leakage_risk") == "must_not_use_historical_results"
        for item in artifact.get("remediation_plan_registry", [])
    )
    schema_valid = (
        not missing
        and not unexpected
        and not forbidden_paths
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and remediation_items_valid
        and artifact.get("provenance", {}).get("remediation_action_executed")
        is False
        and artifact.get("provenance", {}).get("label_used_by_runtime") is False
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing),
        "unexpected_field_count": len(unexpected),
        "prohibited_artifact_field_count": len(forbidden_paths),
        "forbidden_artifact_paths": forbidden_paths,
    }


def write_historical_validation_blockage_diagnostics(
    diagnostic_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": diagnostic_run["run_id"],
        "phase": diagnostic_run["phase"],
        "blockage_diagnostics_artifact": diagnostic_run[
            "blockage_diagnostics_artifact"
        ],
        "scenario_count": diagnostic_run["scenario_count"],
        "blockage_diagnostic_scenario_count": diagnostic_run[
            "blockage_diagnostic_scenario_count"
        ],
        "blocked_scenario_count": diagnostic_run["blocked_scenario_count"],
        "metric_computation_scope": diagnostic_run["metric_computation_scope"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "remediation_action_executed": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "blockage_diagnostics_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_diagnostic_artifact(
    *,
    contract: dict[str, Any],
    trace_run: dict[str, Any],
    metric_run: dict[str, Any],
) -> dict[str, Any]:
    traces = trace_run["scenario_validation_traces"]
    status_counts = Counter(trace["comparison_status"] for trace in traces)
    blockage_reason_counter = Counter(
        reason
        for trace in traces
        for reason in trace["blocked_reason_codes"]
    )
    blockage_reason_scenarios = {
        reason: [
            trace["scenario_id"]
            for trace in traces
            if reason in trace["blocked_reason_codes"]
        ]
        for reason in blockage_reason_counter
    }
    abstention_counter = Counter(trace["abstention_state"] for trace in traces)
    skip_counter = Counter(
        result.get("skip_reason")
        for result in metric_run["metric_results"]
        if result["result_status"] != "computed" and result.get("skip_reason")
    )
    profiles = [_build_scenario_profile(trace) for trace in traces]
    remediation_registry = _build_remediation_registry(
        blockage_reason_counter,
        blockage_reason_scenarios,
    )
    return {
        "artifact_version": contract["artifact_version"],
        "diagnostic_run_id": RUN_ID,
        "source_research_decision_output_set_id": trace_run[
            "research_decision_output_run"
        ]["run_id"],
        "source_predicted_label_artifact_set_id": trace_run[
            "predicted_label_artifact_run"
        ]["run_id"],
        "source_comparison_artifact_set_id": trace_run["comparison_artifact_run"][
            "run_id"
        ],
        "source_accuracy_metric_artifact_id": metric_run["run_id"],
        "scenario_count": trace_run["scenario_count"],
        "comparable_scenario_count": status_counts["comparable"],
        "non_comparable_scenario_count": status_counts["not_comparable"],
        "abstained_scenario_count": status_counts["abstained"],
        "blocked_scenario_count": status_counts["blocked"],
        "taxonomy_mismatch_count": status_counts["taxonomy_mismatch"],
        "scenario_blockage_profiles": profiles,
        "blockage_reason_summary": dict(sorted(blockage_reason_counter.items())),
        "abstention_reason_summary": dict(sorted(abstention_counter.items())),
        "comparison_status_summary": dict(sorted(status_counts.items())),
        "metric_skip_reason_summary": dict(sorted(skip_counter.items())),
        "remediation_plan_registry": remediation_registry,
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "automatic_remediation",
            "model_tuning",
            "economic_validation_claim",
            "portfolio_or_trade_decision",
            "production_dashboard_output",
        ],
        "provenance": {
            "scenario_trace_run_id": trace_run["run_id"],
            "accuracy_metric_run_id": metric_run["run_id"],
            "remediation_action_executed": False,
            "label_used_by_runtime": False,
            "rule_modified_count": 0,
            "mapping_rule_modified_count": 0,
            "threshold_modified_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
    }


def _build_scenario_profile(trace: dict[str, Any]) -> dict[str, Any]:
    skipped_metrics = [
        state
        for state in trace["metric_result_states"]
        if state["result_status"] != "computed"
    ]
    return {
        "scenario_id": trace["scenario_id"],
        "as_of": trace["as_of"],
        "data_mode": trace["data_mode"],
        "decision_state": trace["decision_state"],
        "predicted_label": trace["predicted_label"],
        "comparison_status": trace["comparison_status"],
        "comparable": trace["comparable"],
        "abstention_state": trace["abstention_state"],
        "blocked_reason_codes": list(trace["blocked_reason_codes"]),
        "blocked_reason_count": len(trace["blocked_reason_codes"]),
        "metric_skip_reasons": [
            item.get("skip_reason") for item in skipped_metrics if item.get("skip_reason")
        ],
        "provenance_chain": list(trace["provenance_chain"]),
    }


def _build_remediation_registry(
    blockage_reason_counter: Counter[str],
    blockage_reason_scenarios: dict[str, list[str]],
) -> list[dict[str, Any]]:
    if not blockage_reason_counter:
        return [
            {
                "blocker_id": "no_blockage_detected",
                "scenario_ids": [],
                "blocker_type": "none",
                "affected_artifact_layer": "diagnostics",
                "remediation_category": "none",
                "allowed_next_phase_action": "no_action_required",
                "prohibited_action": [
                    "do_not_modify_rules_without_new_contract",
                    "do_not_tune_from_historical_result",
                ],
                "requires_new_preregistered_contract": True,
                "tuning_leakage_risk": "must_not_use_historical_results",
                "status": "descriptive_only_not_executed",
            }
        ]
    return [
        {
            "blocker_id": f"phase30_blocker:{reason}",
            "scenario_ids": blockage_reason_scenarios[reason],
            "blocker_type": reason,
            "affected_artifact_layer": "predicted_label_comparison",
            "remediation_category": "future_contract_or_input_remediation",
            "allowed_next_phase_action": (
                "preregister_remediation_contract_before_any_rule_or_mapping_change"
            ),
            "prohibited_action": [
                "do_not_modify_rules_from_metric_result",
                "do_not_modify_mapping_from_comparison_result",
                "do_not_add_threshold_or_weight",
            ],
            "requires_new_preregistered_contract": True,
            "tuning_leakage_risk": "must_not_use_historical_results",
            "status": "descriptive_only_not_executed",
        }
        for reason in sorted(blockage_reason_counter)
    ]


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 30 blockage diagnostics output must be under /tmp: {output}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved


def _find_forbidden_output_paths(
    value: Any,
    forbidden: set[str],
    *,
    prefix: str = "",
) -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden:
                found.append(path)
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]"
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    return []

"""Phase 30 scenario-level validation trace generation."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
)
from business_cycle.validation.historical_research_decision_outputs import (
    build_historical_research_decision_outputs,
)
from business_cycle.validation.offline_predicted_label_artifacts import (
    build_offline_predicted_label_artifacts,
)
from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
)


DEFAULT_SCENARIO_VALIDATION_TRACE_CONTRACT_PATH = Path(
    "specs/common/scenario_validation_trace_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase30_scenario_validation_trace_v1"


def load_scenario_validation_trace_contract(
    path: str | Path = DEFAULT_SCENARIO_VALIDATION_TRACE_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("scenario validation trace contract must map")
    contract = payload.get("scenario_validation_trace_contract")
    if not isinstance(contract, dict):
        raise ValueError("scenario_validation_trace_contract must be a mapping")
    return contract


@lru_cache(maxsize=1)
def build_scenario_validation_trace() -> dict[str, Any]:
    contract = load_scenario_validation_trace_contract()
    research_run = build_historical_research_decision_outputs()
    predicted_run = build_offline_predicted_label_artifacts(
        research_decision_output_run=research_run,
    )
    comparison_run = build_predicted_label_comparison_artifacts(
        predicted_label_artifact_run=predicted_run,
    )
    metric_run = compute_historical_accuracy_metrics(
        comparison_artifact_run=comparison_run,
    )
    traces = _build_traces(
        research_run=research_run,
        predicted_run=predicted_run,
        comparison_run=comparison_run,
        metric_run=metric_run,
    )
    validations = [
        validate_scenario_validation_trace(trace, contract=contract)
        for trace in traces
    ]
    prohibited_trace_field_count = sum(
        validation["prohibited_trace_field_count"] for validation in validations
    )
    label_runtime_usage_detected = any(
        trace["label_runtime_usage_detected"] for trace in traces
    )
    candidate_phase_emitted = any(
        trace["candidate_phase_emitted"] for trace in traces
    )
    current_phase_emitted = any(trace["current_phase_emitted"] for trace in traces)
    return {
        "phase": "30",
        "run_id": RUN_ID,
        "scenario_validation_trace_contract_ready": (
            validate_scenario_validation_trace_contract(contract)[
                "contract_schema_valid"
            ]
        ),
        "scenario_validation_trace_runtime_ready": all(
            validation["trace_schema_valid"] for validation in validations
        ),
        "scenario_count": research_run["scenario_count"],
        "scenario_trace_count": len(traces),
        "prohibited_trace_field_count": prohibited_trace_field_count,
        "label_used_by_runtime_count": int(label_runtime_usage_detected),
        "candidate_phase_emitted": candidate_phase_emitted,
        "current_phase_emitted": current_phase_emitted,
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_scope": "diagnostic_summary_only",
        "backtest_execution_enabled": False,
        "production_behavior_change_count": contract["output_restrictions"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["output_restrictions"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["output_restrictions"][
            "real_registry_write_attempt_count"
        ],
        "scenario_validation_traces": traces,
        "trace_validations": validations,
        "research_decision_output_run": research_run,
        "predicted_label_artifact_run": predicted_run,
        "comparison_artifact_run": comparison_run,
        "accuracy_metric_run": metric_run,
        "contract": contract,
    }


@lru_cache(maxsize=1)
def summarize_scenario_validation_trace() -> dict[str, Any]:
    contract = load_scenario_validation_trace_contract()
    run = build_scenario_validation_trace()
    gates = contract["readiness_gates"]
    ready = (
        run["scenario_validation_trace_contract_ready"] is True
        and run["scenario_validation_trace_runtime_ready"] is True
        and run["scenario_count"] == contract["scenario_count_required"]
        and run["scenario_trace_count"] == gates["scenario_trace_count_required"]
        and run["prohibited_trace_field_count"]
        == gates["prohibited_trace_field_count_required"]
        and run["label_used_by_runtime_count"] == 0
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "30",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "scenario_validation_trace_contract_ready": ready,
        "scenario_validation_trace_runtime_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "scenario_trace_count",
                "prohibited_trace_field_count",
                "label_used_by_runtime_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "metric_computation_scope",
                "backtest_execution_enabled",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
            )
        },
        "trace_run": run,
    }


def validate_scenario_validation_trace_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_accuracy_metric_freeze_id",
        "artifact_version",
        "allowed_inputs",
        "prohibited_inputs",
        "allowed_trace_fields",
        "forbidden_trace_fields",
        "output_restrictions",
        "output_policy",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    restrictions = contract.get("output_restrictions", {})
    output = contract.get("output_policy", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "trace_generation_allowed_research_only_no_runtime_execution"
        and restrictions.get("model_runtime_execution_count") == 0
        and restrictions.get("new_accuracy_metric_computed_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("backtest_execution_enabled") is False
        and restrictions.get("label_used_by_runtime_count") == 0
        and restrictions.get("candidate_phase_emitted") is False
        and restrictions.get("current_phase_emitted") is False
        and output.get("tmp_output_allowed") is True
        and output.get("public_output_allowed") is False
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_scenario_validation_trace(
    trace: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_scenario_validation_trace_contract()
    allowed = set(contract["allowed_trace_fields"])
    forbidden = set(contract["forbidden_trace_fields"])
    keys = set(trace)
    missing = allowed.difference(keys)
    unexpected = keys.difference(allowed)
    forbidden_paths = _find_forbidden_output_paths(trace, forbidden)
    schema_valid = (
        not missing
        and not unexpected
        and not forbidden_paths
        and trace.get("label_runtime_usage_detected") is False
        and trace.get("candidate_phase_emitted") is False
        and trace.get("current_phase_emitted") is False
        and isinstance(trace.get("provenance_chain"), list)
    )
    return {
        "trace_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing),
        "unexpected_field_count": len(unexpected),
        "prohibited_trace_field_count": len(forbidden_paths),
        "forbidden_trace_paths": forbidden_paths,
    }


def write_scenario_validation_trace(
    trace_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": trace_run["run_id"],
        "phase": trace_run["phase"],
        "scenario_validation_traces": trace_run["scenario_validation_traces"],
        "scenario_count": trace_run["scenario_count"],
        "scenario_trace_count": trace_run["scenario_trace_count"],
        "metric_computation_scope": trace_run["metric_computation_scope"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "allowed_uses": [
            "research_validation_trace_review",
            "blockage_diagnostics_input",
            "lineage_and_provenance_review",
        ],
        "prohibited_uses": [
            "runtime_decision_logic",
            "model_tuning",
            "economic_validation_claim",
            "portfolio_or_trade_decision",
            "production_dashboard_output",
        ],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "scenario_validation_trace_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_traces(
    *,
    research_run: dict[str, Any],
    predicted_run: dict[str, Any],
    comparison_run: dict[str, Any],
    metric_run: dict[str, Any],
) -> list[dict[str, Any]]:
    research = {
        artifact["scenario_id"]: artifact
        for artifact in research_run["research_decision_outputs"]
    }
    predicted = {
        artifact["scenario_id"]: artifact
        for artifact in predicted_run["offline_predicted_label_artifacts"]
    }
    comparison = {
        artifact["scenario_id"]: artifact
        for artifact in comparison_run["predicted_label_comparison_artifacts"]
    }
    metric_artifact = metric_run["accuracy_metric_artifact"]
    metric_states = [
        {
            "metric_id": result["metric_id"],
            "result_status": result["result_status"],
            "skip_reason": result.get("skip_reason"),
        }
        for result in metric_run["metric_results"]
    ]
    traces = []
    for scenario_id in sorted(research):
        research_artifact = research[scenario_id]
        predicted_artifact = predicted[scenario_id]
        comparison_artifact = comparison[scenario_id]
        provenance_chain = [
            research_artifact["research_output_id"],
            _predicted_ref(predicted_artifact),
            _comparison_ref(comparison_artifact),
            metric_artifact["metric_run_id"],
        ]
        traces.append(
            {
                "scenario_id": scenario_id,
                "as_of": research_artifact["as_of"],
                "data_mode": research_artifact["data_mode"],
                "research_decision_output_ref": research_artifact[
                    "research_output_id"
                ],
                "predicted_label_artifact_ref": _predicted_ref(
                    predicted_artifact
                ),
                "comparison_artifact_ref": _comparison_ref(comparison_artifact),
                "metric_artifact_ref": metric_artifact["metric_run_id"],
                "decision_state": research_artifact["decision_state"],
                "predicted_label": predicted_artifact["predicted_label"],
                "comparison_status": comparison_artifact["comparison_status"],
                "comparable": comparison_artifact["comparable"],
                "abstention_state": research_artifact["abstention_state"],
                "blocked_reason_codes": list(
                    research_artifact["blocked_reason_codes"]
                ),
                "metric_result_states": metric_states,
                "provenance_chain": provenance_chain,
                "label_runtime_usage_detected": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
    return traces


def _predicted_ref(artifact: dict[str, Any]) -> str:
    return f"phase27_predicted_label:{artifact['scenario_id']}:{artifact['as_of']}"


def _comparison_ref(artifact: dict[str, Any]) -> str:
    return f"phase28_comparison:{artifact['scenario_id']}:{artifact['as_of']}"


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 30 scenario trace output must be under /tmp: {output}")
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

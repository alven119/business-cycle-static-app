"""Phase 36 research-only historical validation result artifacts."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.validation.recession_recovery_comparability_unblock import (
    build_recession_recovery_comparability_unblock,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase36_historical_validation_results_v1"
GENERATED_AT_UTC = "2026-06-25T00:00:00Z"
FORBIDDEN_RESULT_FIELDS = {
    "portfolio_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "economic_return",
    "sharpe",
    "drawdown",
    "CAGR",
    "candidate_phase",
    "current_phase",
    "production_phase",
    "production_ready",
    "investment_ready",
}


@lru_cache(maxsize=1)
def build_historical_validation_results() -> dict[str, Any]:
    unblock = build_recession_recovery_comparability_unblock()
    artifact = _build_result_artifact(unblock)
    validation = validate_historical_validation_result_artifact(artifact)
    comparable_count = artifact["comparable_scenario_count"]
    ready = (
        validation["artifact_schema_valid"] is True
        and artifact["scenario_count"] == 5
        and comparable_count == unblock["post_comparable_scenario_count"]
        and comparable_count >= 2
        and artifact["economic_performance_metric_count"] == 0
        and artifact["metric_scope"] == "historical_accuracy_only"
    )
    return {
        "phase": "36",
        "run_id": RUN_ID,
        "historical_validation_result_runtime_ready": ready,
        "scenario_count": artifact["scenario_count"],
        "comparable_scenario_count": comparable_count,
        "non_comparable_scenario_count": artifact["non_comparable_scenario_count"],
        "historical_validation_result_artifact_count": 1,
        "historical_accuracy_metric_count": unblock["historical_accuracy_metric_count"],
        "new_accuracy_metric_computed_count": 0,
        "metric_computation_scope": artifact["metric_scope"],
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "prohibited_result_field_count": validation["prohibited_result_field_count"],
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "historical_validation_result_artifact": artifact,
        "artifact_validation": validation,
        "unblock_run": unblock,
    }


def summarize_historical_validation_results() -> dict[str, Any]:
    run = build_historical_validation_results()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "historical_validation_result_runtime_ready",
            "scenario_count",
            "comparable_scenario_count",
            "non_comparable_scenario_count",
            "historical_validation_result_artifact_count",
            "historical_accuracy_metric_count",
            "new_accuracy_metric_computed_count",
            "metric_computation_scope",
            "economic_performance_metric_count",
            "backtest_execution_enabled",
            "label_used_by_runtime_count",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "prohibited_result_field_count",
            "production_behavior_change_count",
            "prospective_registry_record_count",
            "real_registry_write_attempt_count",
            "forbidden_repo_output_count",
            "historical_validation_result_artifact",
        )
    }


def validate_historical_validation_result_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "artifact_version",
        "validation_result_run_id",
        "scenario_count",
        "comparable_scenario_count",
        "non_comparable_scenario_count",
        "comparable_scenario_results",
        "non_comparable_scenario_evidence",
        "historical_accuracy_metric_results",
        "metric_scope",
        "economic_performance_metric_count",
        "research_only",
        "validation_only",
        "prohibited_uses",
        "provenance",
    }
    missing = sorted(required.difference(artifact))
    forbidden_paths = _find_forbidden_output_paths(artifact, FORBIDDEN_RESULT_FIELDS)
    comparable_errors = [
        result.get("scenario_id")
        for result in artifact.get("comparable_scenario_results", [])
        if result.get("comparison_status") != "comparable"
        or result.get("predicted_label") not in {"recession", "recovery", "growth", "boom", "abstained"}
        or not result.get("provenance_chain")
    ]
    provenance = artifact.get("provenance", {})
    schema_valid = (
        not missing
        and not forbidden_paths
        and not comparable_errors
        and artifact.get("scenario_count") == 5
        and artifact.get("comparable_scenario_count", 0) >= 2
        and artifact.get("non_comparable_scenario_count", 0)
        == artifact.get("scenario_count", 0) - artifact.get("comparable_scenario_count", 0)
        and artifact.get("metric_scope") == "historical_accuracy_only"
        and artifact.get("economic_performance_metric_count") == 0
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and provenance.get("label_used_by_runtime_count") == 0
        and provenance.get("new_accuracy_metric_computed_count") == 0
        and provenance.get("economic_performance_metric_count") == 0
        and provenance.get("candidate_phase_emitted") is False
        and provenance.get("current_phase_emitted") is False
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_field_count": len(missing),
        "missing_fields": missing,
        "prohibited_result_field_count": len(forbidden_paths),
        "forbidden_result_paths": forbidden_paths,
        "comparable_result_error_count": len(comparable_errors),
        "comparable_result_errors": comparable_errors,
    }


def write_historical_validation_results(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run["run_id"],
        "phase": run["phase"],
        "historical_validation_result_runtime_ready": run[
            "historical_validation_result_runtime_ready"
        ],
        "historical_validation_result_artifact": run[
            "historical_validation_result_artifact"
        ],
        "scenario_count": run["scenario_count"],
        "comparable_scenario_count": run["comparable_scenario_count"],
        "non_comparable_scenario_count": run["non_comparable_scenario_count"],
        "historical_validation_result_artifact_count": run[
            "historical_validation_result_artifact_count"
        ],
        "historical_accuracy_metric_count": run["historical_accuracy_metric_count"],
        "new_accuracy_metric_computed_count": 0,
        "metric_computation_scope": run["metric_computation_scope"],
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "historical_validation_result_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_result_artifact(unblock: dict[str, Any]) -> dict[str, Any]:
    comparison_artifacts = unblock["post_comparison_run"][
        "predicted_label_comparison_artifacts"
    ]
    traces = _by_scenario(unblock["post_trace_run"]["scenario_validation_traces"])
    metric_results = list(unblock["post_metric_run"]["metric_results"])
    comparable_results = [
        _comparable_result(
            comparison=artifact,
            trace=traces[artifact["scenario_id"]],
            metric_results=metric_results,
        )
        for artifact in comparison_artifacts
        if artifact["comparable"] is True
    ]
    non_comparable_evidence = _non_comparable_evidence(unblock)
    return {
        "artifact_version": "phase36_historical_validation_result_v1",
        "validation_result_run_id": RUN_ID,
        "source_recession_recovery_unblock_run_id": unblock["run_id"],
        "source_comparison_artifact_set_id": unblock["post_comparison_run"]["run_id"],
        "source_metric_artifact_id": unblock["post_metric_run"]["run_id"],
        "scenario_count": unblock["scenario_count"],
        "comparable_scenario_count": len(comparable_results),
        "non_comparable_scenario_count": len(non_comparable_evidence),
        "comparable_scenario_results": comparable_results,
        "non_comparable_scenario_evidence": non_comparable_evidence,
        "historical_accuracy_metric_results": metric_results,
        "metric_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
        "provenance": {
            "label_used_by_runtime_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "metric_registry_reused": True,
            "comparison_artifacts_are_only_runtime_input": True,
            "evidence_rule_modified_count": 0,
            "predicted_mapping_rule_modified_count": 0,
            "threshold_modified_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
            "production_behavior_change_count": 0,
            "prospective_registry_record_count": 0,
            "real_registry_write_attempt_count": 0,
        },
    }


def _comparable_result(
    *,
    comparison: dict[str, Any],
    trace: dict[str, Any],
    metric_results: list[dict[str, Any]],
) -> dict[str, Any]:
    label_match = next(
        item for item in metric_results if item["metric_id"] == "label_match_rate"
    )
    correctness_state = (
        "not_computed_reference_label_values_unmaterialized"
        if label_match["result_status"] != "computed"
        else "computed_by_preregistered_metric_registry"
    )
    return {
        "scenario_id": comparison["scenario_id"],
        "reference_label_family": comparison["reference_label_set"][
            "scenario_family"
        ],
        "predicted_label": comparison["predicted_label"],
        "comparison_status": comparison["comparison_status"],
        "metric_result_state": [
            {
                "metric_id": item["metric_id"],
                "result_status": item["result_status"],
            }
            for item in metric_results
        ],
        "correctness_state": correctness_state,
        "abstention_state": comparison["abstention_state"],
        "evidence_summary": {
            "comparison_status_reason": comparison["comparison_status_reason"],
            "label_values_materialized": comparison["reference_label_set"][
                "label_values_materialized"
            ],
            "reference_only": comparison["reference_label_set"]["reference_only"],
            "blocked_reason_count": len(comparison["blocked_reason_codes"]),
        },
        "provenance_chain": trace["provenance_chain"],
    }


def _non_comparable_evidence(unblock: dict[str, Any]) -> list[dict[str, Any]]:
    comparison_by_id = _by_scenario(
        unblock["post_comparison_run"]["predicted_label_comparison_artifacts"]
    )
    evidence = []
    remaining = unblock["recession_recovery_unblock_artifact"][
        "remaining_recession_recovery_non_comparable_evidence"
    ]
    for scenario_id, rows in sorted(remaining.items()):
        comparison = comparison_by_id[scenario_id]
        evidence.append(
            {
                "scenario_id": scenario_id,
                "reference_label_family": comparison["reference_label_set"][
                    "scenario_family"
                ],
                "predicted_label": comparison["predicted_label"],
                "comparison_status": comparison["comparison_status"],
                "abstention_state": comparison["abstention_state"],
                "blocked_reason_codes": comparison["blocked_reason_codes"],
                "genuine_non_comparable_reasons": rows,
            }
        )
    return evidence


def _by_scenario(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["scenario_id"]: item for item in items}


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 36 historical validation result output must be under /tmp: {output}"
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

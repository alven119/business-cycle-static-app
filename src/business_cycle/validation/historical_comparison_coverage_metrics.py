"""Phase 23 comparison-coverage metrics, excluding accuracy and performance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_label_joiner import (
    build_historical_label_comparison_artifacts,
)


DEFAULT_COMPARISON_COVERAGE_METRICS_CONTRACT_PATH = Path(
    "specs/common/historical_comparison_coverage_metrics_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
COVERAGE_METRIC_FIELDS = (
    "label_join_success_count",
    "label_join_coverage_rate",
    "label_provenance_verified_count",
    "label_provenance_coverage_rate",
    "runtime_result_available_count",
    "runtime_result_availability_rate",
    "abstention_result_count",
    "abstention_result_rate",
    "blocked_result_count",
    "blocked_result_rate",
    "comparable_artifact_count",
    "comparable_artifact_rate",
    "non_comparable_artifact_count",
    "non_comparable_artifact_rate",
)


def load_historical_comparison_coverage_metrics_contract(
    path: str | Path = DEFAULT_COMPARISON_COVERAGE_METRICS_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical comparison coverage metrics contract must map")
    contract = payload.get("historical_comparison_coverage_metrics_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_comparison_coverage_metrics_contract must be a mapping"
        )
    return contract


def run_historical_comparison_coverage_metrics() -> dict[str, Any]:
    contract = load_historical_comparison_coverage_metrics_contract()
    artifact_run = build_historical_label_comparison_artifacts()
    artifacts = artifact_run["label_comparison_artifacts"]
    scenario_count = artifact_run["scenario_count"]
    label_join_success_count = sum(
        artifact["label_join_status"] == "joined" for artifact in artifacts
    )
    label_provenance_verified_count = sum(
        artifact["label_provenance_verified"] is True for artifact in artifacts
    )
    runtime_result_available_count = sum(
        bool(artifact.get("runtime_result_summary")) for artifact in artifacts
    )
    abstention_result_count = sum(
        artifact["abstention_status"] == "abstained" for artifact in artifacts
    )
    blocked_result_count = sum(
        bool(artifact["blocked_reason_codes"]) for artifact in artifacts
    )
    comparable_artifact_count = sum(
        artifact["label_join_status"] == "joined"
        and artifact["label_provenance_verified"] is True
        and artifact["label_used_by_runtime"] is False
        and bool(artifact["runtime_result_summary"])
        for artifact in artifacts
    )
    non_comparable_artifact_count = scenario_count - comparable_artifact_count
    coverage_metrics = {
        "scenario_count": scenario_count,
        "label_comparison_artifact_count": len(artifacts),
        "label_join_success_count": label_join_success_count,
        "label_join_coverage_rate": _rate(label_join_success_count, scenario_count),
        "label_provenance_verified_count": label_provenance_verified_count,
        "label_provenance_coverage_rate": _rate(
            label_provenance_verified_count,
            scenario_count,
        ),
        "runtime_result_available_count": runtime_result_available_count,
        "runtime_result_availability_rate": _rate(
            runtime_result_available_count,
            scenario_count,
        ),
        "abstention_result_count": abstention_result_count,
        "abstention_result_rate": _rate(abstention_result_count, scenario_count),
        "blocked_result_count": blocked_result_count,
        "blocked_result_rate": _rate(blocked_result_count, scenario_count),
        "comparable_artifact_count": comparable_artifact_count,
        "comparable_artifact_rate": _rate(comparable_artifact_count, scenario_count),
        "non_comparable_artifact_count": non_comparable_artifact_count,
        "non_comparable_artifact_rate": _rate(
            non_comparable_artifact_count,
            scenario_count,
        ),
        "metric_computation_scope": contract["metric_computation_scope"],
        "accuracy_metric_enabled": False,
        "economic_performance_metric_enabled": False,
    }
    validation = validate_historical_comparison_coverage_metrics(
        coverage_metrics,
        contract=contract,
    )
    return {
        "phase": "23",
        "run_id": "phase23_historical_comparison_coverage_metrics_v1",
        "comparison_coverage_metrics_contract_ready": (
            contract["contract_status"]
            == "coverage_metrics_allowed_no_accuracy_or_performance"
        ),
        "comparison_coverage_metrics_runtime_ready": validation[
            "metric_schema_valid"
        ],
        "scenario_count": scenario_count,
        "label_comparison_artifact_count": len(artifacts),
        "label_provenance_verified_count": label_provenance_verified_count,
        "label_used_by_runtime_count": artifact_run["label_used_by_runtime_count"],
        "comparison_coverage_metric_count": len(COVERAGE_METRIC_FIELDS),
        "metric_computation_enabled": True,
        "metric_computation_scope": contract["metric_computation_scope"],
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "prohibited_metric_field_count": validation[
            "prohibited_metric_field_count"
        ],
        "predicted_label_output_count": validation["predicted_label_output_count"],
        "candidate_phase_emitted": artifact_run["candidate_phase_emitted"],
        "current_phase_emitted": artifact_run["current_phase_emitted"],
        "backtest_execution_enabled": False,
        "holdout_registered": False,
        "production_behavior_change_count": contract["output_restrictions"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["output_restrictions"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["output_restrictions"][
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(
            contract["disabled_runtime_guards"]["numeric_weight_added"]
        ),
        "arbitrary_threshold_added_count": int(
            contract["disabled_runtime_guards"]["arbitrary_threshold_added"]
        ),
        "role_count_voting_added_count": int(
            contract["disabled_runtime_guards"]["role_count_voting_added"]
        ),
        "historical_tuning_leakage_count": int(
            contract["disabled_runtime_guards"]["historical_tuning_used"]
        ),
        "coverage_metrics": coverage_metrics,
        "metric_validation": validation,
        "artifact_run": artifact_run,
        "contract": contract,
    }


def summarize_historical_comparison_coverage_metrics() -> dict[str, Any]:
    contract = load_historical_comparison_coverage_metrics_contract()
    run = run_historical_comparison_coverage_metrics()
    gates = contract["readiness_gates"]
    ready = (
        run["comparison_coverage_metrics_contract_ready"] is True
        and run["comparison_coverage_metrics_runtime_ready"] is True
        and run["scenario_count"] == contract["scenario_count_required"]
        and run["label_comparison_artifact_count"] == run["scenario_count"]
        and run["label_provenance_verified_count"] == run["scenario_count"]
        and run["label_used_by_runtime_count"] == 0
        and run["comparison_coverage_metric_count"] > 0
        and run["metric_computation_enabled"] is True
        and run["metric_computation_scope"] == "comparison_coverage_only"
        and run["historical_accuracy_metric_count"] == 0
        and run["economic_performance_metric_count"] == 0
        and run["prohibited_metric_field_count"] == 0
        and run["predicted_label_output_count"] == 0
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and all(
            value is True
            for key, value in gates.items()
            if key != "prohibited_metric_field_count_required"
        )
        and gates["prohibited_metric_field_count_required"] == 0
        and all(
            value is False
            for value in contract["disabled_runtime_guards"].values()
        )
    )
    return {
        "phase": "23",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "comparison_coverage_metrics_contract_ready": ready,
        "comparison_coverage_metrics_runtime_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "label_comparison_artifact_count",
                "label_provenance_verified_count",
                "label_used_by_runtime_count",
                "comparison_coverage_metric_count",
                "metric_computation_enabled",
                "metric_computation_scope",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "prohibited_metric_field_count",
                "predicted_label_output_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "backtest_execution_enabled",
                "holdout_registered",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
            )
        },
        "coverage_metrics": run["coverage_metrics"],
        "metric_run": run,
    }


def validate_historical_comparison_coverage_metrics(
    metrics: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_historical_comparison_coverage_metrics_contract()
    allowed_fields = set(contract["allowed_metric_fields"])
    forbidden_fields = set(contract["forbidden_metric_fields"])
    output_keys = set(metrics)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    forbidden_paths = _find_forbidden_output_paths(metrics, forbidden_fields)
    predicted_label_paths = _find_forbidden_output_paths(metrics, {"predicted_label"})
    schema_valid = (
        not missing_allowed_fields
        and not unexpected_fields
        and not forbidden_paths
        and metrics.get("metric_computation_scope") == "comparison_coverage_only"
        and metrics.get("accuracy_metric_enabled") is False
        and metrics.get("economic_performance_metric_enabled") is False
    )
    return {
        "metric_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_metric_field_count": len(forbidden_paths),
        "predicted_label_output_count": len(predicted_label_paths),
        "forbidden_metric_paths": forbidden_paths,
    }


def write_historical_comparison_coverage_metrics(
    metric_run: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_dir(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": metric_run["run_id"],
        "phase": metric_run["phase"],
        "coverage_metrics": metric_run["coverage_metrics"],
        "metric_computation_enabled": metric_run["metric_computation_enabled"],
        "metric_computation_scope": metric_run["metric_computation_scope"],
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": metric_run["candidate_phase_emitted"],
        "current_phase_emitted": metric_run["current_phase_emitted"],
        "allowed_uses": [
            "comparison_coverage_readiness_review",
            "label_join_pipeline_quality_review",
        ],
        "prohibited_uses": [
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "production_dashboard_output",
        ],
    }
    output_file = output_path / "comparison_coverage_metrics.json"
    output_file.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output_dir": str(output_path),
        "metric_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_file)],
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 23 comparison-coverage output must be under /tmp: {output_dir}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
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

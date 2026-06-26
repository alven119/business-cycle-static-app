"""Phase 37 post-PIT-remediation validation rerun bundle."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.render.research_artifact_explorer import (
    render_research_artifact_explorer,
)
from business_cycle.validation.controlled_pit_backfill import (
    build_controlled_pit_backfill_plan,
    write_controlled_pit_backfill,
)
from business_cycle.validation.historical_accuracy_metrics import (
    write_historical_accuracy_metrics,
)
from business_cycle.validation.historical_research_decision_outputs import (
    write_historical_research_decision_outputs,
)
from business_cycle.validation.historical_validation_blockage_diagnostics import (
    write_historical_validation_blockage_diagnostics,
)
from business_cycle.validation.offline_predicted_label_artifacts import (
    write_offline_predicted_label_artifacts,
)
from business_cycle.validation.predicted_label_comparison_artifacts import (
    write_predicted_label_comparison_artifacts,
)
from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    summarize_recession_recovery_pit_gap_matrix,
)
from business_cycle.validation.recession_recovery_pit_remediation import (
    build_recession_recovery_pit_remediation,
    write_recession_recovery_pit_remediation,
)
from business_cycle.validation.scenario_validation_trace import (
    write_scenario_validation_trace,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase37_post_pit_remediation_validation_rerun_v1"
GENERATED_AT_UTC = "2026-06-26T00:00:00Z"


@lru_cache(maxsize=1)
def build_post_pit_remediation_validation_rerun() -> dict[str, Any]:
    remediation = build_recession_recovery_pit_remediation()
    backfill = build_controlled_pit_backfill_plan()
    result_run = _build_historical_validation_result_run(remediation)
    ready = (
        remediation["recession_recovery_pit_remediation_runtime_ready"] is True
        and backfill["controlled_pit_backfill_ready"] is True
        and remediation["post_predicted_run"]["predicted_label_artifact_count"] == 5
        and remediation["post_comparison_run"]["label_comparison_artifact_count"] == 5
        and remediation["post_metric_run"]["historical_accuracy_metric_count"] == 5
        and remediation["post_trace_run"]["scenario_trace_count"] == 5
        and result_run["historical_validation_result_artifact_count"] == 1
        and remediation["post_metric_run"]["economic_performance_metric_count"] == 0
        and remediation["post_metric_run"]["candidate_phase_emitted"] is False
        and remediation["post_metric_run"]["current_phase_emitted"] is False
    )
    return {
        "phase": "37",
        "run_id": RUN_ID,
        "post_pit_remediation_validation_rerun_ready": ready,
        "updated_research_decision_output_count": remediation["post_research_run"][
            "research_decision_output_count"
        ],
        "updated_predicted_label_artifact_count": remediation["post_predicted_run"][
            "predicted_label_artifact_count"
        ],
        "updated_comparison_artifact_count": remediation["post_comparison_run"][
            "label_comparison_artifact_count"
        ],
        "updated_historical_accuracy_metric_count": remediation["post_metric_run"][
            "historical_accuracy_metric_count"
        ],
        "updated_blockage_diagnostic_scenario_count": remediation[
            "post_diagnostics_run"
        ]["blockage_diagnostic_scenario_count"],
        "updated_scenario_trace_count": remediation["post_trace_run"][
            "scenario_trace_count"
        ],
        "historical_validation_result_artifact_count": result_run[
            "historical_validation_result_artifact_count"
        ],
        "pre_comparable_scenario_count": remediation["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": remediation["post_comparable_scenario_count"],
        "pre_insufficient_point_in_time_role_gap_count": remediation[
            "pre_insufficient_point_in_time_role_gap_count"
        ],
        "post_insufficient_point_in_time_role_gap_count": remediation[
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "false_comparability_count": remediation["false_comparability_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "forbidden_repo_output_count": 0,
        "remediation_run": remediation,
        "backfill_run": backfill,
        "research_run": remediation["post_research_run"],
        "predicted_run": remediation["post_predicted_run"],
        "comparison_run": remediation["post_comparison_run"],
        "metric_run": remediation["post_metric_run"],
        "trace_run": remediation["post_trace_run"],
        "diagnostics_run": remediation["post_diagnostics_run"],
        "result_run": result_run,
    }


def summarize_post_pit_remediation_validation_rerun() -> dict[str, Any]:
    run = build_post_pit_remediation_validation_rerun()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "post_pit_remediation_validation_rerun_ready",
            "updated_research_decision_output_count",
            "updated_predicted_label_artifact_count",
            "updated_comparison_artifact_count",
            "updated_historical_accuracy_metric_count",
            "updated_blockage_diagnostic_scenario_count",
            "updated_scenario_trace_count",
            "historical_validation_result_artifact_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
            "pre_insufficient_point_in_time_role_gap_count",
            "post_insufficient_point_in_time_role_gap_count",
            "false_comparability_count",
            "new_accuracy_metric_computed_count",
            "economic_performance_metric_count",
            "backtest_execution_enabled",
            "label_used_by_runtime_count",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "forbidden_repo_output_count",
        )
    }


def write_post_pit_remediation_validation_rerun(
    rerun: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    root = _validated_output_dir(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    matrix_path = root / "phase37_pit_gap_matrix.json"
    remediation_path = root / "phase37_pit_remediation.json"
    backfill_path = root / "phase37_controlled_pit_backfill.json"
    research_dir = root / "phase37_research_decision_outputs"
    predicted_path = root / "phase37_predicted_label_artifacts.json"
    comparison_path = root / "phase37_predicted_label_comparison_artifacts.json"
    metric_path = root / "phase37_historical_accuracy_metrics.json"
    trace_path = root / "phase37_scenario_validation_trace.json"
    diagnostics_path = root / "phase37_blockage_diagnostics.json"
    result_path = root / "phase37_historical_validation_results.json"
    explorer_path = root / "phase37_research_artifact_explorer.html"
    summary_path = root / "phase37_post_pit_summary.json"

    written: list[str] = []
    matrix_payload = summarize_recession_recovery_pit_gap_matrix()
    matrix_path.write_text(
        json.dumps(matrix_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written.append(str(matrix_path))
    write_result = write_recession_recovery_pit_remediation(
        rerun["remediation_run"],
        output=remediation_path,
    )
    written.extend(write_result["written_files"])
    write_result = write_controlled_pit_backfill(
        rerun["backfill_run"],
        output=backfill_path,
    )
    written.extend(write_result["written_files"])
    write_result = write_historical_research_decision_outputs(
        rerun["research_run"],
        output_dir=research_dir,
    )
    written.extend(write_result["written_files"])
    write_result = write_offline_predicted_label_artifacts(
        rerun["predicted_run"],
        output=predicted_path,
    )
    written.extend(write_result["written_files"])
    write_result = write_predicted_label_comparison_artifacts(
        rerun["comparison_run"],
        output=comparison_path,
    )
    written.extend(write_result["written_files"])
    write_result = write_historical_accuracy_metrics(
        rerun["metric_run"],
        output=metric_path,
    )
    written.extend(write_result["written_files"])
    write_result = write_scenario_validation_trace(
        rerun["trace_run"],
        output=trace_path,
    )
    written.extend(write_result["written_files"])
    write_result = write_historical_validation_blockage_diagnostics(
        rerun["diagnostics_run"],
        output=diagnostics_path,
    )
    written.extend(write_result["written_files"])
    result_path.write_text(
        json.dumps(_result_payload(rerun["result_run"]), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written.append(str(result_path))
    explorer = render_research_artifact_explorer(
        output=explorer_path,
        diagnostics_input=diagnostics_path,
        trace_input=trace_path,
        post_validation_result_input=result_path,
        post_pit_input=remediation_path,
    )
    written.append(explorer["output"])
    summary_path.write_text(
        json.dumps(summarize_post_pit_remediation_validation_rerun(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written.append(str(summary_path))
    return {
        "output_dir": str(root),
        "post_pit_remediation_validation_rerun_written": True,
        "written_file_count": len(written),
        "written_files": written,
        "forbidden_repo_output_count": 0,
    }


def _build_historical_validation_result_run(
    remediation: dict[str, Any],
) -> dict[str, Any]:
    comparison_artifacts = remediation["post_comparison_run"][
        "predicted_label_comparison_artifacts"
    ]
    metric_results = list(remediation["post_metric_run"]["metric_results"])
    comparison_by_id = _by_scenario(comparison_artifacts)
    comparable = [
        {
            "scenario_id": item["scenario_id"],
            "reference_label_family": item["reference_label_set"]["scenario_family"],
            "predicted_label": item["predicted_label"],
            "comparison_status": item["comparison_status"],
            "metric_result_state": [
                {
                    "metric_id": metric["metric_id"],
                    "result_status": metric["result_status"],
                }
                for metric in metric_results
            ],
            "correctness_state": "not_computed_reference_label_values_unmaterialized",
        }
        for item in comparison_artifacts
        if item["comparable"] is True
    ]
    remaining = remediation["pit_remediation_artifact"]["remaining_pit_gap_evidence"]
    non_comparable_evidence = [
        {
            "scenario_id": scenario_id,
            "reference_label_family": comparison_by_id[scenario_id][
                "reference_label_set"
            ]["scenario_family"],
            "predicted_label": comparison_by_id[scenario_id]["predicted_label"],
            "comparison_status": comparison_by_id[scenario_id]["comparison_status"],
            "abstention_state": comparison_by_id[scenario_id]["abstention_state"],
            "blocked_reason_codes": comparison_by_id[scenario_id][
                "blocked_reason_codes"
            ],
            "genuine_non_comparable_reasons": rows,
        }
        for scenario_id, rows in sorted(remaining.items())
    ]
    artifact = {
        "artifact_version": "phase37_historical_validation_result_v1",
        "validation_result_run_id": "phase37_historical_validation_results_v1",
        "source_pit_remediation_run_id": RUN_ID,
        "scenario_count": remediation["scenario_count"],
        "comparable_scenario_count": len(comparable),
        "non_comparable_scenario_count": remediation["scenario_count"] - len(comparable),
        "comparable_scenario_results": comparable,
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
            "evidence_rule_semantics_modified_count": 0,
            "predicted_mapping_rule_modified_count": 0,
            "threshold_modified_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
    }
    return {
        "phase": "37",
        "run_id": "phase37_historical_validation_results_v1",
        "historical_validation_result_runtime_ready": (
            artifact["scenario_count"] == 5
            and artifact["comparable_scenario_count"]
            == remediation["post_comparable_scenario_count"]
            and artifact["metric_scope"] == "historical_accuracy_only"
            and artifact["economic_performance_metric_count"] == 0
        ),
        "scenario_count": artifact["scenario_count"],
        "comparable_scenario_count": artifact["comparable_scenario_count"],
        "non_comparable_scenario_count": artifact["non_comparable_scenario_count"],
        "historical_validation_result_artifact_count": 1,
        "historical_accuracy_metric_count": remediation["post_metric_run"][
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "metric_computation_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "historical_validation_result_artifact": artifact,
    }


def _result_payload(result_run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": result_run["run_id"],
        "phase": result_run["phase"],
        "historical_validation_result_runtime_ready": result_run[
            "historical_validation_result_runtime_ready"
        ],
        "historical_validation_result_artifact": result_run[
            "historical_validation_result_artifact"
        ],
        "scenario_count": result_run["scenario_count"],
        "comparable_scenario_count": result_run["comparable_scenario_count"],
        "non_comparable_scenario_count": result_run["non_comparable_scenario_count"],
        "historical_validation_result_artifact_count": result_run[
            "historical_validation_result_artifact_count"
        ],
        "historical_accuracy_metric_count": result_run["historical_accuracy_metric_count"],
        "new_accuracy_metric_computed_count": 0,
        "metric_computation_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in rows}


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 37 output must be under /tmp: {output_dir}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
    return resolved

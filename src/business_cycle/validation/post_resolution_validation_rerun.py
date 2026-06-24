"""Phase 33 post-resolution research artifact rerun."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.render.research_artifact_explorer import (
    render_research_artifact_explorer,
)
from business_cycle.validation.genuine_blocker_resolution_execution import (
    build_genuine_blocker_resolution_execution,
    write_genuine_blocker_resolution_execution,
)
from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
    write_historical_accuracy_metrics,
)
from business_cycle.validation.historical_research_decision_outputs import (
    build_historical_research_decision_outputs,
)
from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
    write_historical_validation_blockage_diagnostics,
)
from business_cycle.validation.offline_predicted_label_artifacts import (
    build_offline_predicted_label_artifacts,
    write_offline_predicted_label_artifacts,
)
from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
    write_predicted_label_comparison_artifacts,
)
from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
    write_scenario_validation_trace,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase33_post_resolution_validation_rerun_v1"


@lru_cache(maxsize=1)
def build_post_resolution_validation_rerun() -> dict[str, Any]:
    execution_run = build_genuine_blocker_resolution_execution()
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
    trace_run = build_scenario_validation_trace()
    diagnostics_run = build_historical_validation_blockage_diagnostics(
        trace_run=trace_run,
    )
    execution_artifact = execution_run["genuine_blocker_resolution_execution_artifact"]
    ready = (
        execution_run["genuine_blocker_resolution_execution_ready"] is True
        and predicted_run["predicted_label_artifact_count"] == 5
        and comparison_run["label_comparison_artifact_count"] == 5
        and metric_run["historical_accuracy_metric_count"] == 5
        and diagnostics_run["blocked_scenario_count"]
        == execution_artifact["post_resolution_blocked_scenario_count"]
        and trace_run["scenario_trace_count"] == 5
        and metric_run["economic_performance_metric_count"] == 0
        and metric_run["candidate_phase_emitted"] is False
        and metric_run["current_phase_emitted"] is False
    )
    return {
        "phase": "33",
        "run_id": RUN_ID,
        "post_resolution_validation_rerun_ready": ready,
        "updated_predicted_label_artifact_count": predicted_run[
            "predicted_label_artifact_count"
        ],
        "updated_comparison_artifact_count": comparison_run[
            "label_comparison_artifact_count"
        ],
        "updated_historical_accuracy_metric_count": metric_run[
            "historical_accuracy_metric_count"
        ],
        "updated_blockage_diagnostic_scenario_count": diagnostics_run[
            "blockage_diagnostic_scenario_count"
        ],
        "updated_scenario_trace_count": trace_run["scenario_trace_count"],
        "pre_resolution_blocked_scenario_count": execution_run[
            "pre_resolution_blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": execution_run[
            "post_resolution_blocked_scenario_count"
        ],
        "pre_resolution_comparable_scenario_count": execution_run[
            "pre_resolution_comparable_scenario_count"
        ],
        "post_resolution_comparable_scenario_count": execution_run[
            "post_resolution_comparable_scenario_count"
        ],
        "false_resolution_count": execution_run["false_resolution_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "forbidden_repo_output_count": 0,
        "execution_run": execution_run,
        "research_run": research_run,
        "predicted_run": predicted_run,
        "comparison_run": comparison_run,
        "metric_run": metric_run,
        "trace_run": trace_run,
        "diagnostics_run": diagnostics_run,
    }


def summarize_post_resolution_validation_rerun() -> dict[str, Any]:
    run = build_post_resolution_validation_rerun()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "post_resolution_validation_rerun_ready",
            "updated_predicted_label_artifact_count",
            "updated_comparison_artifact_count",
            "updated_historical_accuracy_metric_count",
            "updated_blockage_diagnostic_scenario_count",
            "updated_scenario_trace_count",
            "pre_resolution_blocked_scenario_count",
            "post_resolution_blocked_scenario_count",
            "pre_resolution_comparable_scenario_count",
            "post_resolution_comparable_scenario_count",
            "false_resolution_count",
            "new_accuracy_metric_computed_count",
            "economic_performance_metric_count",
            "backtest_execution_enabled",
            "label_used_by_runtime_count",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "forbidden_repo_output_count",
        )
    }


def write_post_resolution_validation_rerun(
    rerun: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    root = _validated_output_dir(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    execution_path = root / "phase33_resolution_execution.json"
    predicted_path = root / "phase33_predicted_label_artifacts.json"
    comparison_path = root / "phase33_predicted_label_comparison_artifacts.json"
    metric_path = root / "phase33_historical_accuracy_metrics.json"
    trace_path = root / "phase33_scenario_validation_trace.json"
    diagnostics_path = root / "phase33_blockage_diagnostics.json"
    explorer_path = root / "phase33_research_artifact_explorer.html"
    summary_path = root / "phase33_post_resolution_summary.json"

    written: list[str] = []
    write_result = write_genuine_blocker_resolution_execution(
        rerun["execution_run"],
        output=execution_path,
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
    explorer = render_research_artifact_explorer(
        output=explorer_path,
        diagnostics_input=diagnostics_path,
        trace_input=trace_path,
        post_resolution_input=execution_path,
    )
    written.append(explorer["output"])
    summary_payload = {
        "run_id": rerun["run_id"],
        "phase": rerun["phase"],
        "post_resolution_validation_rerun_ready": rerun[
            "post_resolution_validation_rerun_ready"
        ],
        "updated_predicted_label_artifact_count": rerun[
            "updated_predicted_label_artifact_count"
        ],
        "updated_comparison_artifact_count": rerun[
            "updated_comparison_artifact_count"
        ],
        "updated_historical_accuracy_metric_count": rerun[
            "updated_historical_accuracy_metric_count"
        ],
        "updated_blockage_diagnostic_scenario_count": rerun[
            "updated_blockage_diagnostic_scenario_count"
        ],
        "updated_scenario_trace_count": rerun["updated_scenario_trace_count"],
        "pre_resolution_blocked_scenario_count": rerun[
            "pre_resolution_blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": rerun[
            "post_resolution_blocked_scenario_count"
        ],
        "false_resolution_count": rerun["false_resolution_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    summary_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written.append(str(summary_path))
    return {
        "output_dir": str(root),
        "post_resolution_validation_rerun_written": True,
        "research_artifact_explorer_written": explorer[
            "research_artifact_explorer_written"
        ],
        "written_file_count": len(written),
        "written_files": written,
    }


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 33 rerun output dir must be under /tmp: {output_dir}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
    return resolved

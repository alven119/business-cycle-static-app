"""Phase 35 post-comparability validation rerun bundle."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.render.research_artifact_explorer import (
    render_research_artifact_explorer,
)
from business_cycle.validation.autonomous_comparability_realization import (
    build_autonomous_comparability_realization,
    write_autonomous_comparability_realization,
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
from business_cycle.validation.scenario_validation_trace import (
    write_scenario_validation_trace,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase35_post_comparability_validation_rerun_v1"


@lru_cache(maxsize=1)
def build_post_comparability_validation_rerun() -> dict[str, Any]:
    comparability = build_autonomous_comparability_realization()
    ready = (
        comparability["autonomous_comparability_realization_ready"] is True
        and comparability["post_predicted_run"]["predicted_label_artifact_count"] == 5
        and comparability["post_comparison_run"][
            "label_comparison_artifact_count"
        ]
        == 5
        and comparability["post_metric_run"]["historical_accuracy_metric_count"] == 5
        and comparability["post_trace_run"]["scenario_trace_count"] == 5
        and comparability["post_diagnostics_run"]["blocked_scenario_count"] == 0
        and comparability["post_diagnostics_run"]["comparable_scenario_count"]
        == comparability["post_comparable_scenario_count"]
        and comparability["post_metric_run"]["economic_performance_metric_count"] == 0
        and comparability["post_metric_run"]["candidate_phase_emitted"] is False
        and comparability["post_metric_run"]["current_phase_emitted"] is False
    )
    return {
        "phase": "35",
        "run_id": RUN_ID,
        "post_comparability_validation_rerun_ready": ready,
        "updated_research_decision_output_count": comparability[
            "post_research_run"
        ]["research_decision_output_count"],
        "updated_predicted_label_artifact_count": comparability[
            "post_predicted_run"
        ]["predicted_label_artifact_count"],
        "updated_comparison_artifact_count": comparability["post_comparison_run"][
            "label_comparison_artifact_count"
        ],
        "updated_historical_accuracy_metric_count": comparability[
            "post_metric_run"
        ]["historical_accuracy_metric_count"],
        "updated_blockage_diagnostic_scenario_count": comparability[
            "post_diagnostics_run"
        ]["blockage_diagnostic_scenario_count"],
        "updated_scenario_trace_count": comparability["post_trace_run"][
            "scenario_trace_count"
        ],
        "pre_blocked_scenario_count": comparability["pre_blocked_scenario_count"],
        "post_blocked_scenario_count": comparability["post_blocked_scenario_count"],
        "pre_comparable_scenario_count": comparability[
            "pre_comparable_scenario_count"
        ],
        "post_comparable_scenario_count": comparability[
            "post_comparable_scenario_count"
        ],
        "false_comparability_count": comparability["false_comparability_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "forbidden_repo_output_count": 0,
        "comparability_run": comparability,
        "research_run": comparability["post_research_run"],
        "predicted_run": comparability["post_predicted_run"],
        "comparison_run": comparability["post_comparison_run"],
        "metric_run": comparability["post_metric_run"],
        "trace_run": comparability["post_trace_run"],
        "diagnostics_run": comparability["post_diagnostics_run"],
    }


def summarize_post_comparability_validation_rerun() -> dict[str, Any]:
    run = build_post_comparability_validation_rerun()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "post_comparability_validation_rerun_ready",
            "updated_research_decision_output_count",
            "updated_predicted_label_artifact_count",
            "updated_comparison_artifact_count",
            "updated_historical_accuracy_metric_count",
            "updated_blockage_diagnostic_scenario_count",
            "updated_scenario_trace_count",
            "pre_blocked_scenario_count",
            "post_blocked_scenario_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
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


def write_post_comparability_validation_rerun(
    rerun: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    root = _validated_output_dir(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    comparability_path = root / "phase35_comparability_realization.json"
    research_dir = root / "phase35_research_decision_outputs"
    predicted_path = root / "phase35_predicted_label_artifacts.json"
    comparison_path = root / "phase35_predicted_label_comparison_artifacts.json"
    metric_path = root / "phase35_historical_accuracy_metrics.json"
    trace_path = root / "phase35_scenario_validation_trace.json"
    diagnostics_path = root / "phase35_blockage_diagnostics.json"
    explorer_path = root / "phase35_research_artifact_explorer.html"
    summary_path = root / "phase35_post_comparability_summary.json"

    written: list[str] = []
    write_result = write_autonomous_comparability_realization(
        rerun["comparability_run"],
        output=comparability_path,
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
    explorer = render_research_artifact_explorer(
        output=explorer_path,
        diagnostics_input=diagnostics_path,
        trace_input=trace_path,
        post_comparability_input=comparability_path,
    )
    written.append(explorer["output"])
    summary_payload = {
        "run_id": rerun["run_id"],
        "phase": rerun["phase"],
        "post_comparability_validation_rerun_ready": rerun[
            "post_comparability_validation_rerun_ready"
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
        "pre_blocked_scenario_count": rerun["pre_blocked_scenario_count"],
        "post_blocked_scenario_count": rerun["post_blocked_scenario_count"],
        "pre_comparable_scenario_count": rerun["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": rerun["post_comparable_scenario_count"],
        "false_comparability_count": rerun["false_comparability_count"],
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
        "post_comparability_validation_rerun_written": True,
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
        raise ValueError(
            f"Phase 35 post-comparability output must be under /tmp: {output_dir}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
    return resolved

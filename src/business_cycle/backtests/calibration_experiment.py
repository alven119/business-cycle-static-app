"""Run calibration experiments comparing baseline and transition controls."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from business_cycle.backtests.attribution import write_transition_attribution
from business_cycle.backtests.calibration import load_calibration_plan
from business_cycle.backtests.catalog import get_scenario, load_backtest_scenario_catalog
from business_cycle.backtests.report import write_backtest_report
from business_cycle.backtests.runner import BacktestRunConfig, BacktestRunResult, run_backtest
from business_cycle.backtests.specs import BacktestScenario, BacktestScenarioCatalog, BacktestScenarioError

CAVEATS_ZH = [
    "使用修訂後歷史資料，不等同當時投資人可見資料。",
    "此為模型校準實驗，不代表正式模型已更新。",
    "不構成投資建議。",
]

BacktestRunner = Callable[[BacktestRunConfig], BacktestRunResult]
ReportWriter = Callable[[str | Path, str | Path], str | Path]
AttributionWriter = Callable[..., Path]


class CalibrationExperimentError(ValueError):
    """Raised when calibration experiment inputs are invalid."""


def run_calibration_experiment(
    *,
    experiment_id: str,
    catalog_path: str | Path = Path("specs/backtests/scenarios.yaml"),
    controls_config_path: str | Path = Path("specs/backtests/transition_controls_enabled_experiment.yaml"),
    output_dir: str | Path = Path("data/backtests/calibration"),
    max_periods: int | None = None,
    scenario_id: str | None = None,
    calibration_plan_path: str | Path = Path("specs/backtests/calibration_plan.yaml"),
    backtest_runner: BacktestRunner | None = None,
    report_writer: ReportWriter | None = None,
    attribution_writer: AttributionWriter | None = None,
) -> dict[str, Any]:
    """Run baseline and enabled-controls backtests and write a comparison summary."""

    if not experiment_id:
        raise CalibrationExperimentError("experiment_id must be non-empty")
    controls_path = Path(controls_config_path)
    if not controls_path.exists():
        raise CalibrationExperimentError(f"transition controls config does not exist: {controls_path}")
    catalog = load_backtest_scenario_catalog(catalog_path)
    scenarios = _selected_scenarios(catalog, scenario_id)
    out_of_sample = _out_of_sample_scenarios(calibration_plan_path)
    experiment_root = Path(output_dir) / experiment_id
    summary = build_calibration_experiment_summary(
        experiment_id=experiment_id,
        scenarios=scenarios,
        experiment_root=experiment_root,
        controls_config_path=controls_path,
        max_periods=max_periods,
        out_of_sample_scenarios=out_of_sample,
        backtest_runner=backtest_runner or run_backtest,
        report_writer=report_writer or write_backtest_report,
        attribution_writer=attribution_writer or write_transition_attribution,
    )
    output_path = experiment_root / "calibration_summary.json"
    summary["output_path"] = str(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_calibration_experiment_summary(
    *,
    experiment_id: str,
    scenarios: list[BacktestScenario],
    experiment_root: Path,
    controls_config_path: Path,
    max_periods: int | None,
    out_of_sample_scenarios: set[str],
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
    attribution_writer: AttributionWriter,
) -> dict[str, Any]:
    """Build a calibration experiment summary across scenarios."""

    scenario_summaries = [
        _run_scenario_pair(
            scenario=scenario,
            experiment_root=experiment_root,
            controls_config_path=controls_config_path,
            max_periods=max_periods,
            out_of_sample_scenarios=out_of_sample_scenarios,
            backtest_runner=backtest_runner,
            report_writer=report_writer,
            attribution_writer=attribution_writer,
        )
        for scenario in scenarios
    ]
    return {
        "experiment_id": experiment_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_mode": _summary_data_mode(scenarios),
        "controls_config_path": str(controls_config_path),
        "scenario_count": len(scenario_summaries),
        "max_periods": max_periods,
        "scenarios": scenario_summaries,
        "aggregate": _aggregate(scenario_summaries),
        "caveats_zh": CAVEATS_ZH,
    }


def _run_scenario_pair(
    *,
    scenario: BacktestScenario,
    experiment_root: Path,
    controls_config_path: Path,
    max_periods: int | None,
    out_of_sample_scenarios: set[str],
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
    attribution_writer: AttributionWriter,
) -> dict[str, Any]:
    base = {
        "scenario_id": scenario.scenario_id,
        "display_name_zh": scenario.display_name_zh,
        "baseline": {},
        "experiment": {},
        "delta": {},
        "acceptance_checks": {},
        "notes_zh": [],
    }
    try:
        baseline = _run_variant(
            scenario=scenario,
            output_dir=experiment_root / "baseline",
            max_periods=max_periods,
            transition_controls_path=None,
            backtest_runner=backtest_runner,
            report_writer=report_writer,
            attribution_writer=attribution_writer,
        )
        experiment = _run_variant(
            scenario=scenario,
            output_dir=experiment_root / "experiment",
            max_periods=max_periods,
            transition_controls_path=controls_config_path,
            backtest_runner=backtest_runner,
            report_writer=report_writer,
            attribution_writer=attribution_writer,
        )
    except Exception as exc:  # noqa: BLE001 - summary should record scenario failure.
        return {
            **base,
            "failure_count": 1,
            "scenario_failure": {
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
        }
    delta = _delta(baseline, experiment)
    checks = _acceptance_checks(
        scenario_id=scenario.scenario_id,
        baseline=baseline,
        experiment=experiment,
        delta=delta,
        out_of_sample_scenarios=out_of_sample_scenarios,
    )
    return {
        **base,
        "baseline": baseline,
        "experiment": experiment,
        "delta": delta,
        "acceptance_checks": checks,
        "failure_count": 0,
    }


def _run_variant(
    *,
    scenario: BacktestScenario,
    output_dir: Path,
    max_periods: int | None,
    transition_controls_path: Path | None,
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
    attribution_writer: AttributionWriter,
) -> dict[str, Any]:
    result = backtest_runner(
        BacktestRunConfig(
            scenario_id=scenario.scenario_id,
            scenario=scenario,
            output_dir=output_dir,
            max_periods=max_periods,
            data_mode=scenario.data_mode,
            transition_controls_path=transition_controls_path,
        )
    )
    scenario_dir = output_dir / scenario.scenario_id
    report_path = Path(report_writer(result.output_path, scenario_dir / "report.json"))
    attribution_writer(
        timeline_path=result.output_path,
        report_path=report_path,
        intermediate_dir=scenario_dir / "intermediate",
        output_path=scenario_dir / "transition_attribution.json",
    )
    report = _load_json_mapping(report_path)
    return _report_summary(report)


def _report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "plausibility_warning_count": int(report.get("plausibility_warning_count") or 0),
        "transition_event_count": len(_list(report.get("transition_events"))),
        "first_recession_current_as_of": report.get("first_recession_current_as_of"),
        "phase_segment_count": len(_list(report.get("phase_segments"))),
        "failure_count": int(report.get("failure_count") or 0),
    }


def _delta(baseline: dict[str, Any], experiment: dict[str, Any]) -> dict[str, int]:
    keys = ("plausibility_warning_count", "transition_event_count", "phase_segment_count")
    return {
        key: int(experiment.get(key) or 0) - int(baseline.get(key) or 0)
        for key in keys
    }


def _acceptance_checks(
    *,
    scenario_id: str,
    baseline: dict[str, Any],
    experiment: dict[str, Any],
    delta: dict[str, int],
    out_of_sample_scenarios: set[str],
) -> dict[str, bool]:
    no_new_false_recession = True
    if scenario_id in out_of_sample_scenarios:
        no_new_false_recession = not (
            baseline.get("first_recession_current_as_of") is None
            and experiment.get("first_recession_current_as_of") is not None
        )
    return {
        "reduced_warnings": delta["plausibility_warning_count"] < 0,
        "no_new_failure": int(experiment.get("failure_count") or 0) <= int(baseline.get("failure_count") or 0),
        "no_new_false_recession_for_out_of_sample": no_new_false_recession,
    }


def _aggregate(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_total = sum(_nested_int(item, "baseline", "plausibility_warning_count") for item in scenarios)
    experiment_total = sum(_nested_int(item, "experiment", "plausibility_warning_count") for item in scenarios)
    deltas = [int(item.get("delta", {}).get("plausibility_warning_count") or 0) for item in scenarios]
    return {
        "baseline_total_plausibility_warning_count": baseline_total,
        "experiment_total_plausibility_warning_count": experiment_total,
        "delta_total_plausibility_warning_count": experiment_total - baseline_total,
        "scenario_improved_count": sum(1 for value in deltas if value < 0),
        "scenario_regressed_count": sum(1 for value in deltas if value > 0),
        "scenario_unchanged_count": sum(1 for value in deltas if value == 0),
        "scenario_with_failures_count": sum(1 for item in scenarios if int(item.get("failure_count") or 0) > 0),
    }


def _selected_scenarios(
    catalog: BacktestScenarioCatalog,
    scenario_id: str | None,
) -> list[BacktestScenario]:
    if scenario_id is None:
        return list(catalog.scenarios)
    try:
        return [get_scenario(catalog, scenario_id)]
    except BacktestScenarioError as exc:
        raise CalibrationExperimentError(str(exc)) from exc


def _out_of_sample_scenarios(path: str | Path) -> set[str]:
    try:
        plan = load_calibration_plan(path)
    except Exception:  # noqa: BLE001 - experiment can still run without plan metadata.
        return set()
    return set(plan.calibration_scenarios["out_of_sample"])


def _summary_data_mode(scenarios: list[BacktestScenario]) -> str:
    modes = sorted({scenario.data_mode for scenario in scenarios})
    if len(modes) == 1:
        return modes[0]
    return "mixed"


def _nested_int(item: dict[str, Any], section: str, key: str) -> int:
    value = item.get(section)
    if not isinstance(value, dict):
        return 0
    return int(value.get(key) or 0)


def _load_json_mapping(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Calibration experiment JSON must be a mapping: {path}")
    return payload


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]

"""Run limited smoke backtests across scenario catalogs."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from business_cycle.backtests.catalog import (
    get_scenario,
    load_backtest_scenario_catalog,
)
from business_cycle.backtests.report import write_backtest_report
from business_cycle.backtests.runner import BacktestRunConfig, BacktestRunResult, run_backtest
from business_cycle.backtests.specs import (
    BacktestScenario,
    BacktestScenarioCatalog,
    BacktestScenarioError,
)

CAVEATS_ZH = [
    "使用修訂後歷史資料。",
    "不等同當時投資人可見資料。",
    "不構成投資建議。",
]

BacktestRunner = Callable[[BacktestRunConfig], BacktestRunResult]
ReportWriter = Callable[[str | Path, str | Path], str | Path]


class BacktestSmokeError(ValueError):
    """Raised when smoke backtest inputs are invalid."""


def run_backtest_smoke(
    *,
    catalog_path: str | Path = Path("specs/backtests/scenarios.yaml"),
    output_dir: str | Path = Path("data/backtests"),
    output_path: str | Path = Path("data/backtests/smoke_summary.json"),
    max_periods: int = 24,
    scenario_id: str | None = None,
    backtest_runner: BacktestRunner | None = None,
    report_writer: ReportWriter | None = None,
) -> dict[str, Any]:
    """Run limited backtests and write an aggregate smoke summary JSON."""

    catalog = load_backtest_scenario_catalog(catalog_path)
    scenarios = _selected_scenarios(catalog, scenario_id)
    summary = build_backtest_smoke_summary(
        scenarios=scenarios,
        output_dir=Path(output_dir),
        max_periods=max_periods,
        backtest_runner=backtest_runner or run_backtest,
        report_writer=report_writer or write_backtest_report,
    )
    output = Path(output_path)
    summary["output_path"] = str(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_backtest_smoke_summary(
    *,
    scenarios: list[BacktestScenario],
    output_dir: Path,
    max_periods: int,
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
) -> dict[str, Any]:
    """Build a smoke summary by running each selected scenario."""

    scenario_summaries: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_summaries.append(
            _run_one_scenario(
                scenario=scenario,
                output_dir=output_dir,
                max_periods=max_periods,
                backtest_runner=backtest_runner,
                report_writer=report_writer,
            )
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_mode": _summary_data_mode(scenarios),
        "scenario_count": len(scenario_summaries),
        "max_periods": max_periods,
        "scenarios": scenario_summaries,
        "aggregate": _aggregate(scenario_summaries),
        "caveats_zh": CAVEATS_ZH,
    }


def _run_one_scenario(
    *,
    scenario: BacktestScenario,
    output_dir: Path,
    max_periods: int,
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
) -> dict[str, Any]:
    timeline_path = output_dir / scenario.scenario_id / "timeline.json"
    report_path = output_dir / scenario.scenario_id / "report.json"
    base = {
        "scenario_id": scenario.scenario_id,
        "display_name_zh": scenario.display_name_zh,
        "period_count": 0,
        "phase_segment_count": 0,
        "transition_event_count": 0,
        "first_transition_watch_as_of": None,
        "first_recession_watch_as_of": None,
        "first_recession_current_as_of": None,
        "plausibility_warning_count": 0,
        "plausibility_warning_kinds": [],
        "failure_count": 0,
        "warning_count": 0,
        "timeline_path": str(timeline_path),
        "report_path": str(report_path),
    }
    try:
        config = BacktestRunConfig(
            scenario_id=scenario.scenario_id,
            scenario=scenario,
            output_dir=output_dir,
            max_periods=max_periods,
            data_mode=scenario.data_mode,
        )
        result = backtest_runner(config)
        timeline_path = result.output_path
        report_path = Path(report_writer(timeline_path, report_path))
        report = _load_report(report_path)
    except Exception as exc:  # noqa: BLE001 - keep smoke summary useful across scenarios.
        return {
            **base,
            "failure_count": 1,
            "scenario_failure": {
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
        }

    return {
        **base,
        "period_count": int(report.get("period_count") or 0),
        "phase_segment_count": len(_list(report.get("phase_segments"))),
        "transition_event_count": len(_list(report.get("transition_events"))),
        "first_transition_watch_as_of": report.get("first_transition_watch_as_of"),
        "first_recession_watch_as_of": report.get("first_recession_watch_as_of"),
        "first_recession_current_as_of": report.get("first_recession_current_as_of"),
        "plausibility_warning_count": int(report.get("plausibility_warning_count") or 0),
        "plausibility_warning_kinds": sorted(
            {
                str(warning.get("kind"))
                for warning in _list(report.get("plausibility_warnings"))
                if warning.get("kind") is not None
            }
        ),
        "failure_count": int(report.get("failure_count") or 0),
        "warning_count": int(report.get("warning_count") or 0),
        "timeline_path": str(timeline_path),
        "report_path": str(report_path),
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
        raise BacktestSmokeError(str(exc)) from exc


def _load_report(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Backtest report JSON must be a mapping: {path}")
    return payload


def _aggregate(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    warning_kind_counts: Counter[str] = Counter()
    for scenario in scenarios:
        warning_kind_counts.update(str(kind) for kind in scenario.get("plausibility_warning_kinds", []))
    return {
        "scenario_with_failures_count": sum(1 for item in scenarios if int(item.get("failure_count") or 0) > 0),
        "scenario_with_plausibility_warnings_count": sum(
            1 for item in scenarios if int(item.get("plausibility_warning_count") or 0) > 0
        ),
        "total_plausibility_warning_count": sum(
            int(item.get("plausibility_warning_count") or 0) for item in scenarios
        ),
        "warning_kind_counts": dict(sorted(warning_kind_counts.items())),
    }


def _summary_data_mode(scenarios: list[BacktestScenario]) -> str:
    modes = sorted({scenario.data_mode for scenario in scenarios})
    if len(modes) == 1:
        return modes[0]
    return "mixed"


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]

"""Aggregate transition attribution diagnostics across scenarios."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from business_cycle.backtests.attribution import (
    attribution_quality_counts,
    write_transition_attribution,
)
from business_cycle.backtests.catalog import get_scenario, load_backtest_scenario_catalog
from business_cycle.backtests.report import write_backtest_report
from business_cycle.backtests.runner import BacktestRunConfig, BacktestRunResult, run_backtest
from business_cycle.backtests.specs import BacktestScenario, BacktestScenarioCatalog, BacktestScenarioError

CAVEATS_ZH = [
    "使用修訂後歷史資料。",
    "不等同當時投資人可見資料。",
    "不構成投資建議。",
]

BacktestRunner = Callable[[BacktestRunConfig], BacktestRunResult]
ReportWriter = Callable[[str | Path, str | Path], str | Path]
AttributionWriter = Callable[..., Path]


class AttributionSmokeError(ValueError):
    """Raised when attribution smoke inputs are invalid."""


def run_attribution_smoke(
    *,
    catalog_path: str | Path = Path("specs/backtests/scenarios.yaml"),
    output_dir: str | Path = Path("data/backtests"),
    output_path: str | Path = Path("data/backtests/attribution_summary.json"),
    max_periods: int | None = None,
    scenario_id: str | None = None,
    reuse_existing: bool = False,
    backtest_runner: BacktestRunner | None = None,
    report_writer: ReportWriter | None = None,
    attribution_writer: AttributionWriter | None = None,
) -> dict[str, Any]:
    """Run attribution smoke summary and write aggregate JSON."""

    catalog = load_backtest_scenario_catalog(catalog_path)
    scenarios = _selected_scenarios(catalog, scenario_id)
    summary = build_attribution_smoke_summary(
        scenarios=scenarios,
        output_dir=Path(output_dir),
        max_periods=max_periods,
        reuse_existing=reuse_existing,
        backtest_runner=backtest_runner or run_backtest,
        report_writer=report_writer or write_backtest_report,
        attribution_writer=attribution_writer or write_transition_attribution,
    )
    output = Path(output_path)
    summary["output_path"] = str(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_attribution_smoke_summary(
    *,
    scenarios: list[BacktestScenario],
    output_dir: Path,
    max_periods: int | None,
    reuse_existing: bool,
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
    attribution_writer: AttributionWriter,
) -> dict[str, Any]:
    """Build aggregate attribution diagnostics across scenarios."""

    scenario_summaries = [
        _scenario_summary(
            scenario=scenario,
            output_dir=output_dir,
            max_periods=max_periods,
            reuse_existing=reuse_existing,
            backtest_runner=backtest_runner,
            report_writer=report_writer,
            attribution_writer=attribution_writer,
        )
        for scenario in scenarios
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_mode": _summary_data_mode(scenarios),
        "scenario_count": len(scenario_summaries),
        "scenarios": scenario_summaries,
        "aggregate": _aggregate(scenario_summaries),
        "caveats_zh": CAVEATS_ZH,
        "warnings": [],
    }


def _scenario_summary(
    *,
    scenario: BacktestScenario,
    output_dir: Path,
    max_periods: int | None,
    reuse_existing: bool,
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
    attribution_writer: AttributionWriter,
) -> dict[str, Any]:
    scenario_dir = output_dir / scenario.scenario_id
    timeline_path = scenario_dir / "timeline.json"
    report_path = scenario_dir / "report.json"
    intermediate_dir = scenario_dir / "intermediate"
    attribution_path = scenario_dir / "transition_attribution.json"
    base = {
        "scenario_id": scenario.scenario_id,
        "display_name_zh": scenario.display_name_zh,
        "transition_count": 0,
        "diagnostic_count": 0,
        "attribution_quality_counts": {},
        "top_phase_score_delta": None,
        "top_indicator_delta": None,
        "top_repeated_indicator_ids": [],
        "linked_plausibility_warning_count": 0,
        "output_path": str(attribution_path),
        "warnings": [],
    }
    try:
        if not reuse_existing or not attribution_path.exists():
            timeline_path, report_path = _ensure_timeline_and_report(
                scenario=scenario,
                output_dir=output_dir,
                timeline_path=timeline_path,
                report_path=report_path,
                max_periods=max_periods,
                reuse_existing=reuse_existing,
                backtest_runner=backtest_runner,
                report_writer=report_writer,
            )
            attribution_path = Path(
                attribution_writer(
                    timeline_path=timeline_path,
                    report_path=report_path,
                    intermediate_dir=intermediate_dir,
                    output_path=attribution_path,
                )
            )
        payload = _load_json_mapping(attribution_path)
    except Exception as exc:  # noqa: BLE001 - summarize failure without hiding it.
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
        "transition_count": int(payload.get("transition_count") or 0),
        "diagnostic_count": len(_list(payload.get("diagnostics"))),
        "attribution_quality_counts": attribution_quality_counts(payload),
        "top_phase_score_delta": _top_phase_score_delta(payload),
        "top_indicator_delta": _top_indicator_delta(payload),
        "top_repeated_indicator_ids": _top_repeated_indicator_ids(payload),
        "linked_plausibility_warning_count": len(_list(payload.get("plausibility_warnings_linked"))),
        "output_path": str(attribution_path),
        "warnings": [str(item) for item in payload.get("warnings", []) if item],
        "failure_count": 0,
    }


def _ensure_timeline_and_report(
    *,
    scenario: BacktestScenario,
    output_dir: Path,
    timeline_path: Path,
    report_path: Path,
    max_periods: int | None,
    reuse_existing: bool,
    backtest_runner: BacktestRunner,
    report_writer: ReportWriter,
) -> tuple[Path, Path]:
    if not timeline_path.exists():
        if reuse_existing:
            raise FileNotFoundError(f"Backtest timeline does not exist: {timeline_path}")
        result = backtest_runner(
            BacktestRunConfig(
                scenario_id=scenario.scenario_id,
                scenario=scenario,
                output_dir=output_dir,
                max_periods=max_periods,
                data_mode=scenario.data_mode,
            )
        )
        timeline_path = result.output_path
    if not report_path.exists():
        if reuse_existing:
            raise FileNotFoundError(f"Backtest report does not exist: {report_path}")
        report_path = Path(report_writer(timeline_path, report_path))
    return timeline_path, report_path


def _top_phase_score_delta(payload: dict[str, Any]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for diagnostic in _list(payload.get("diagnostics")):
        as_of = diagnostic.get("as_of")
        for change in _list(diagnostic.get("phase_score_changes")):
            delta = _float_or_none(change.get("delta"))
            if delta is None:
                continue
            candidate = {"as_of": as_of, "phase_id": change.get("phase_id"), "delta": delta}
            if best is None or abs(delta) > abs(float(best["delta"])):
                best = candidate
    return best


def _top_indicator_delta(payload: dict[str, Any]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for diagnostic in _list(payload.get("diagnostics")):
        as_of = diagnostic.get("as_of")
        for change in _list(diagnostic.get("top_indicator_score_changes")):
            delta = _float_or_none(change.get("delta"))
            if delta is None:
                continue
            candidate = {"as_of": as_of, "indicator_id": change.get("indicator_id"), "delta": delta}
            if best is None or abs(delta) > abs(float(best["delta"])):
                best = candidate
    return best


def _top_repeated_indicator_ids(payload: dict[str, Any]) -> list[str]:
    counts: Counter[str] = Counter()
    for diagnostic in _list(payload.get("diagnostics")):
        for change in _list(diagnostic.get("top_indicator_score_changes")):
            indicator_id = change.get("indicator_id")
            if indicator_id is not None:
                counts[str(indicator_id)] += 1
    return [indicator_id for indicator_id, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]]


def _aggregate(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    quality_counts: Counter[str] = Counter()
    indicator_frequency: Counter[str] = Counter()
    phase_frequency: Counter[str] = Counter()
    warning_kind_counts: Counter[str] = Counter()
    for scenario in scenarios:
        quality_counts.update(
            {
                str(key): int(value)
                for key, value in dict(scenario.get("attribution_quality_counts") or {}).items()
            }
        )
        payload = _scenario_attribution_payload(scenario)
        indicator_frequency.update(_indicator_delta_ids(payload))
        phase_frequency.update(_phase_delta_ids(payload))
        warning_kind_counts.update(str(item["kind"]) for item in _list(payload.get("plausibility_warnings_linked")))
    return {
        "scenario_with_attribution_count": sum(1 for item in scenarios if int(item.get("diagnostic_count") or 0) > 0),
        "scenario_with_failures_count": sum(1 for item in scenarios if int(item.get("failure_count") or 0) > 0),
        "total_diagnostic_count": sum(int(item.get("diagnostic_count") or 0) for item in scenarios),
        "attribution_quality_counts": dict(sorted(quality_counts.items())),
        "indicator_delta_frequency": dict(sorted(indicator_frequency.items())),
        "phase_delta_frequency": dict(sorted(phase_frequency.items())),
        "linked_plausibility_warning_kind_counts": dict(sorted(warning_kind_counts.items())),
    }


def _scenario_attribution_payload(scenario: dict[str, Any]) -> dict[str, Any]:
    path = scenario.get("output_path")
    if not path:
        return {}
    try:
        return _load_json_mapping(Path(str(path)))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {}


def _indicator_delta_ids(payload: dict[str, Any]) -> list[str]:
    indicator_ids: list[str] = []
    for diagnostic in _list(payload.get("diagnostics")):
        for change in _list(diagnostic.get("top_indicator_score_changes")):
            indicator_id = change.get("indicator_id")
            if indicator_id is not None:
                indicator_ids.append(str(indicator_id))
    return indicator_ids


def _phase_delta_ids(payload: dict[str, Any]) -> list[str]:
    phase_ids: list[str] = []
    for diagnostic in _list(payload.get("diagnostics")):
        for change in _list(diagnostic.get("phase_score_changes")):
            phase_id = change.get("phase_id")
            if phase_id is not None:
                phase_ids.append(str(phase_id))
    return phase_ids


def _selected_scenarios(
    catalog: BacktestScenarioCatalog,
    scenario_id: str | None,
) -> list[BacktestScenario]:
    if scenario_id is None:
        return list(catalog.scenarios)
    try:
        return [get_scenario(catalog, scenario_id)]
    except BacktestScenarioError as exc:
        raise AttributionSmokeError(str(exc)) from exc


def _summary_data_mode(scenarios: list[BacktestScenario]) -> str:
    modes = sorted({scenario.data_mode for scenario in scenarios})
    if len(modes) == 1:
        return modes[0]
    return "mixed"


def _load_json_mapping(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Attribution smoke JSON must be a mapping: {path}")
    return payload


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None

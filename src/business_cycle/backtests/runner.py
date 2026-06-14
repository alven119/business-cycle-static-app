"""Historical backtest runner skeleton."""

from __future__ import annotations

import calendar
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

from business_cycle.backtests.specs import BacktestScenario

CAVEATS_ZH = [
    "使用修訂後歷史資料。",
    "不等同當時投資人可見資料。",
    "不構成投資建議。",
]


@dataclass(frozen=True)
class BacktestRunConfig:
    """Configuration for one scenario backtest run."""

    scenario_id: str
    scenario: BacktestScenario
    output_dir: Path
    period_frequency: str = "monthly"
    max_periods: int | None = None
    catalog_path: Path = Path("specs/indicator_catalog.yaml")
    phase_specs_dir: Path = Path("specs/phases")
    state_machine_config_path: Path = Path("specs/common/phase_state_machine.yaml")
    raw_data_dir: Path = Path("data/raw/fred")
    data_mode: str = "revised"


@dataclass(frozen=True)
class BacktestPeriodResult:
    """Summary of one historical as-of period."""

    as_of: str
    previous_phase_id: str | None
    current_phase_id: str | None
    candidate_phase_id: str | None
    decision_status: str
    confidence: float
    phase_scores: list[dict[str, Any]]
    indicator_summary: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class BacktestRunResult:
    """Timeline output for one scenario backtest run."""

    scenario_id: str
    display_name_zh: str
    window_start: str
    window_end: str
    data_mode: str
    generated_at: str
    period_count: int
    timeline: list[BacktestPeriodResult]
    output_path: Path
    warnings: list[str]
    failures: list[dict[str, Any]]


PeriodRunner = Callable[[BacktestRunConfig, str, str | None, Path], BacktestPeriodResult]


def generate_monthly_periods(
    window_start: date,
    window_end: date,
    max_periods: int | None = None,
) -> list[str]:
    """Generate month-end as-of dates inside an inclusive date window."""

    if window_start > window_end:
        raise ValueError("window_start must be <= window_end")
    periods: list[str] = []
    year = window_start.year
    month = window_start.month
    while (year, month) <= (window_end.year, window_end.month):
        last_day = calendar.monthrange(year, month)[1]
        month_end = date(year, month, last_day)
        if window_start <= month_end <= window_end:
            periods.append(month_end.isoformat())
            if max_periods is not None and len(periods) >= max_periods:
                break
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return periods


def run_backtest(
    config: BacktestRunConfig,
    period_runner: PeriodRunner | None = None,
) -> BacktestRunResult:
    """Run a scenario over monthly periods and write timeline JSON."""

    if config.period_frequency != "monthly":
        raise ValueError("Only monthly period_frequency is currently supported")
    periods = generate_monthly_periods(
        config.scenario.window_start,
        config.scenario.window_end,
        max_periods=config.max_periods,
    )
    scenario_output_dir = Path(config.output_dir) / config.scenario_id
    timeline_path = scenario_output_dir / "timeline.json"
    runner = period_runner or _run_period_with_scripts

    previous_phase_id: str | None = config.scenario.baseline_phase_id
    timeline: list[BacktestPeriodResult] = []
    warnings: list[str] = []
    failures: list[dict[str, Any]] = []

    for as_of in periods:
        period_output_dir = scenario_output_dir / "intermediate" / as_of
        period_result = runner(config, as_of, previous_phase_id, period_output_dir)
        timeline.append(period_result)
        warnings.extend(period_result.warnings)
        failures.extend(period_result.failures)
        previous_phase_id = period_result.current_phase_id or previous_phase_id

    result = BacktestRunResult(
        scenario_id=config.scenario.scenario_id,
        display_name_zh=config.scenario.display_name_zh,
        window_start=config.scenario.window_start.isoformat(),
        window_end=config.scenario.window_end.isoformat(),
        data_mode=config.data_mode,
        generated_at=datetime.now(timezone.utc).isoformat(),
        period_count=len(timeline),
        timeline=timeline,
        output_path=timeline_path,
        warnings=warnings,
        failures=failures,
    )
    _write_timeline_json(result)
    return result


def serialize_backtest_run_result(result: BacktestRunResult) -> dict[str, Any]:
    """Convert a backtest run result into timeline JSON payload."""

    return {
        "scenario_id": result.scenario_id,
        "display_name_zh": result.display_name_zh,
        "window_start": result.window_start,
        "window_end": result.window_end,
        "data_mode": result.data_mode,
        "generated_at": result.generated_at,
        "period_count": result.period_count,
        "periods": [_serialize_period(period) for period in result.timeline],
        "caveats_zh": CAVEATS_ZH,
        "warnings": result.warnings,
        "failures": result.failures,
    }


def _run_period_with_scripts(
    config: BacktestRunConfig,
    as_of: str,
    previous_phase_id: str | None,
    period_output_dir: Path,
) -> BacktestPeriodResult:
    period_output_dir.mkdir(parents=True, exist_ok=True)
    indicator_scores_path = period_output_dir / "indicator_scores.json"
    phase_scores_path = period_output_dir / "phase_scores.json"
    current_phase_decision_path = period_output_dir / "current_phase_decision.json"
    no_cycle_context_path = period_output_dir / "no_cycle_context.yaml"

    failures: list[dict[str, Any]] = []
    commands = [
        [
            "score_indicators.py",
            "--catalog-path",
            str(config.catalog_path),
            "--input-dir",
            str(config.raw_data_dir),
            "--output-path",
            str(indicator_scores_path),
            "--as-of",
            as_of,
        ],
        [
            "score_phases.py",
            "--indicator-scores-path",
            str(indicator_scores_path),
            "--phase-specs-path",
            str(config.phase_specs_dir),
            "--output-path",
            str(phase_scores_path),
            "--as-of",
            as_of,
        ],
        [
            "resolve_current_phase.py",
            "--phase-scores-path",
            str(phase_scores_path),
            "--config-path",
            str(config.state_machine_config_path),
            "--output-path",
            str(current_phase_decision_path),
            "--previous-phase-source",
            "cli" if previous_phase_id else "none",
            "--cycle-context-path",
            str(no_cycle_context_path),
        ],
    ]
    if previous_phase_id:
        commands[2].extend(["--previous-phase-id", previous_phase_id])

    for command in commands:
        exit_code, stderr = _run_script(command)
        if exit_code != 0:
            failures.append(
                {
                    "as_of": as_of,
                    "step": command[0].removesuffix(".py"),
                    "error_type": "BacktestStepFailed",
                    "message": stderr or f"exit_code={exit_code}",
                }
            )
            return _failed_period(as_of, previous_phase_id, failures)

    return _period_result_from_outputs(
        as_of=as_of,
        previous_phase_id=previous_phase_id,
        indicator_scores_path=indicator_scores_path,
        phase_scores_path=phase_scores_path,
        current_phase_decision_path=current_phase_decision_path,
    )


def _run_script(args: list[str]) -> tuple[int, str]:
    project_root = _project_root()
    script_path = project_root / "scripts" / args[0]
    env = dict(os.environ)
    src_dir = str(project_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src_dir if not existing_pythonpath else f"{src_dir}{os.pathsep}{existing_pythonpath}"
    completed = subprocess.run(  # noqa: S603 - script names are selected by this module.
        [sys.executable, str(script_path), *args[1:]],
        cwd=project_root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stderr.strip()


def _period_result_from_outputs(
    *,
    as_of: str,
    previous_phase_id: str | None,
    indicator_scores_path: Path,
    phase_scores_path: Path,
    current_phase_decision_path: Path,
) -> BacktestPeriodResult:
    indicator_payload = _load_json_mapping(indicator_scores_path)
    phase_payload = _load_json_mapping(phase_scores_path)
    decision = _load_json_mapping(current_phase_decision_path)
    indicator_summary = _int_summary(indicator_payload.get("summary"))
    phase_failures = _list_of_mappings(phase_payload.get("failures"))
    indicator_failures = _list_of_mappings(indicator_payload.get("failures"))
    failures = indicator_failures + phase_failures
    warnings: list[str] = []
    if indicator_summary.get("failed_indicators", 0) > 0:
        warnings.append("indicator scoring had failures; cached raw CSV may be missing or insufficient.")
    if phase_failures:
        warnings.append("phase scoring had failures.")

    return BacktestPeriodResult(
        as_of=as_of,
        previous_phase_id=previous_phase_id,
        current_phase_id=_optional_str(decision.get("current_phase_id")),
        candidate_phase_id=_optional_str(decision.get("candidate_phase_id")),
        decision_status=str(decision.get("decision_status") or "unknown"),
        confidence=float(decision.get("confidence") or 0.0),
        phase_scores=_phase_score_summaries(phase_payload),
        indicator_summary=indicator_summary,
        warnings=warnings,
        failures=failures,
    )


def _failed_period(
    as_of: str,
    previous_phase_id: str | None,
    failures: list[dict[str, Any]],
) -> BacktestPeriodResult:
    return BacktestPeriodResult(
        as_of=as_of,
        previous_phase_id=previous_phase_id,
        current_phase_id=None,
        candidate_phase_id=None,
        decision_status="failed",
        confidence=0.0,
        phase_scores=[],
        indicator_summary={"total_indicators": 0, "scored_indicators": 0, "failed_indicators": 0},
        warnings=["period failed; confirm cached raw CSV exists before rerunning backtest."],
        failures=failures,
    )


def _write_timeline_json(result: BacktestRunResult) -> Path:
    result.output_path.parent.mkdir(parents=True, exist_ok=True)
    result.output_path.write_text(
        json.dumps(serialize_backtest_run_result(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result.output_path


def _serialize_period(period: BacktestPeriodResult) -> dict[str, Any]:
    return {
        "as_of": period.as_of,
        "previous_phase_id": period.previous_phase_id,
        "current_phase_id": period.current_phase_id,
        "decision_status": period.decision_status,
        "candidate_phase_id": period.candidate_phase_id,
        "confidence": period.confidence,
        "phase_scores": period.phase_scores,
        "indicator_summary": period.indicator_summary,
        "warnings": period.warnings,
        "failures": period.failures,
    }


def _phase_score_summaries(phase_payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "phase_id": str(item.get("phase_id")),
            "score": float(item.get("score") or 0.0),
            "confidence": float(item.get("confidence") or 0.0),
            "available_weight": float(item.get("available_weight") or 0.0),
            "stage_hint": item.get("stage_hint"),
        }
        for item in _list_of_mappings(phase_payload.get("results"))
    ]


def _int_summary(value: Any) -> dict[str, int]:
    summary = value if isinstance(value, dict) else {}
    return {
        "total_indicators": int(summary.get("total_indicators") or 0),
        "scored_indicators": int(summary.get("scored_indicators") or 0),
        "failed_indicators": int(summary.get("failed_indicators") or 0),
    }


def _load_json_mapping(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload must be a mapping: {path}")
    return payload


def _list_of_mappings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _optional_str(value: Any) -> str | None:
    return None if value is None else str(value)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]

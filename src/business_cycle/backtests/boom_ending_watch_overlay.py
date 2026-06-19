"""Full-horizon experimental overlay for boom-ending watch rule."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.backtests.boom_ending_diagnostics import (
    build_boom_ending_group_summary,
    build_boom_ending_point_summary,
    load_experimental_indicator_groups,
)
from business_cycle.backtests.boom_ending_refinement_experiment import (
    _score_refined_candidates,
    load_boom_ending_scoring_refinement_experiment,
)
from business_cycle.backtests.boom_ending_watch_rule import (
    BoomEndingWatchRule,
    classify_boom_ending_watch_status,
    load_boom_ending_watch_rule,
)
from business_cycle.backtests.catalog import load_backtest_scenario_catalog
from business_cycle.backtests.runner import BacktestRunConfig, generate_monthly_periods, run_backtest

DEFAULT_SPEC_PATH = Path("specs/backtests/boom_ending_watch_overlay_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_watch_overlay/"
    "boom_ending_watch_overlay_report.json"
)
DEFAULT_EXISTING_TIMELINE_ROOTS = [
    Path("data/backtests/calibration/transition_controls_v2_breadth_full/experiment"),
    Path("data/backtests/calibration/transition_controls_v1_full/experiment"),
    Path("data/backtests"),
]
ScoreFunction = Callable[..., dict[str, Any]]
TimelineLoader = Callable[[str], dict[str, Any] | None]


class BoomEndingWatchOverlayError(ValueError):
    """Raised when boom-ending watch overlay cannot be built."""


@dataclass(frozen=True)
class BoomEndingWatchOverlayExperiment:
    """Boom-ending watch overlay experiment spec."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    inputs: dict[str, str]
    overlay_policy: dict[str, Any]
    evaluation: dict[str, Any]
    acceptance_targets: list[dict[str, Any]]


def load_boom_ending_watch_overlay_experiment(
    path: str | Path = DEFAULT_SPEC_PATH,
) -> BoomEndingWatchOverlayExperiment:
    """Load and validate boom-ending watch overlay experiment spec."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("boom_ending_watch_overlay_experiment")
    if not isinstance(raw, dict):
        raise BoomEndingWatchOverlayError("boom_ending_watch_overlay_experiment YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise BoomEndingWatchOverlayError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BoomEndingWatchOverlayError("caveats_zh must include no-investment-advice caveat")
    if not any("不等於 confirmed recession" in caveat for caveat in caveats):
        raise BoomEndingWatchOverlayError("caveats_zh must state watch is not confirmed recession")
    if not any("外生衝擊" in caveat for caveat in caveats):
        raise BoomEndingWatchOverlayError("caveats_zh must include exogenous shock caveat")
    experiment = BoomEndingWatchOverlayExperiment(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        objective_zh=str(raw.get("objective_zh", "")),
        caveats_zh=caveats,
        inputs=_str_mapping(raw.get("inputs"), "inputs"),
        overlay_policy=dict(raw.get("overlay_policy") or {}),
        evaluation=dict(raw.get("evaluation") or {}),
        acceptance_targets=_list_of_mappings(raw.get("acceptance_targets"), "acceptance_targets"),
    )
    if experiment.version < 1:
        raise BoomEndingWatchOverlayError("version must be positive")
    return experiment


def build_boom_ending_watch_overlay_report(
    *,
    experiment_id: str = "boom_ending_watch_overlay_v1",
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    output_root: str | Path = "data/backtests/candidate_indicators/boom_ending_watch_overlay",
    cache_dir: str | Path = "data/raw/fred",
    reuse_existing: bool = False,
    force: bool = False,
    score_func: ScoreFunction | None = None,
    timeline_loader: TimelineLoader | None = None,
) -> dict[str, Any]:
    """Build full-horizon boom-ending watch overlay report."""

    experiment = load_boom_ending_watch_overlay_experiment(spec_path)
    rule = load_boom_ending_watch_rule(experiment.inputs["boom_ending_watch_rule"])
    refinement = load_boom_ending_scoring_refinement_experiment(
        experiment.inputs["boom_ending_refinement_experiment"]
    )
    groups = load_experimental_indicator_groups("specs/common/experimental_indicator_groups.yaml")
    groups_by_indicator = _groups_by_indicator(groups)
    catalog = load_backtest_scenario_catalog(experiment.inputs["scenario_spec"])
    scorer = score_func or _score_boom_ending_refined_period
    scenario_summaries: list[dict[str, Any]] = []
    scenario_details: list[dict[str, Any]] = []

    for scenario in catalog.scenarios:
        timeline = _load_or_run_timeline(
            scenario_id=scenario.scenario_id,
            timeline_loader=timeline_loader,
            output_root=Path(output_root),
            scenario=scenario,
            scenario_spec_path=Path(experiment.inputs["scenario_spec"]),
            reuse_existing=reuse_existing,
            force=force,
        )
        periods = [
            _overlay_period(
                period=dict(period),
                rule=rule,
                scorer=scorer,
                cache_dir=cache_dir,
                candidate_spec_path=experiment.inputs["boom_ending_candidate_spec"],
                refined_profile=refinement["refined_profile"],
                groups=groups,
                groups_by_indicator=groups_by_indicator,
            )
            for period in timeline.get("periods", [])
        ]
        summary = _scenario_summary(scenario.scenario_id, scenario.display_name_zh, periods)
        scenario_summaries.append(summary)
        scenario_details.append(
            {
                "scenario_id": scenario.scenario_id,
                "display_name_zh": scenario.display_name_zh,
                "periods": periods,
            }
        )

    acceptance_summary = _acceptance_summary(scenario_summaries)
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": experiment_id,
        "data_mode": experiment.data_mode,
        "scenario_count": len(scenario_summaries),
        "scenario_summaries": scenario_summaries,
        "scenario_details": scenario_details,
        "acceptance_summary": acceptance_summary,
        "global_watch_density_summary": _global_watch_density(scenario_summaries),
        "caveats_zh": experiment.caveats_zh,
    }


def write_boom_ending_watch_overlay_report(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write boom-ending watch overlay report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _score_boom_ending_refined_period(
    *,
    as_of: str,
    cache_dir: str | Path,
    spec_path: str | Path,
    refined_profile: dict[str, Any],
) -> dict[str, Any]:
    return _score_refined_candidates(
        as_of=as_of,
        cache_dir=Path(cache_dir),
        spec_path=spec_path,
        refined_profile=refined_profile,
    )


def _load_or_run_timeline(
    *,
    scenario_id: str,
    timeline_loader: TimelineLoader | None,
    output_root: Path,
    scenario: Any,
    scenario_spec_path: Path,
    reuse_existing: bool,
    force: bool,
) -> dict[str, Any]:
    if timeline_loader is not None:
        loaded = timeline_loader(scenario_id)
        if loaded is None:
            raise BoomEndingWatchOverlayError(f"timeline_loader returned no timeline for {scenario_id}")
        return loaded
    expected_period_count = len(generate_monthly_periods(scenario.window_start, scenario.window_end))
    if not force:
        for root in DEFAULT_EXISTING_TIMELINE_ROOTS:
            path = root / scenario_id / "timeline.json"
            if path.exists():
                timeline = json.loads(path.read_text(encoding="utf-8"))
                if int(timeline.get("period_count", 0)) >= expected_period_count:
                    return timeline
    generated_path = output_root / "timelines" / scenario_id / "timeline.json"
    if reuse_existing and not force and generated_path.exists():
        timeline = json.loads(generated_path.read_text(encoding="utf-8"))
        if int(timeline.get("period_count", 0)) >= expected_period_count:
            return timeline
    result = run_backtest(
        BacktestRunConfig(
            scenario_id=scenario_id,
            scenario=scenario,
            output_dir=output_root / "timelines",
            data_mode=scenario.data_mode,
        )
    )
    return json.loads(result.output_path.read_text(encoding="utf-8"))


def _overlay_period(
    *,
    period: dict[str, Any],
    rule: BoomEndingWatchRule,
    scorer: ScoreFunction,
    cache_dir: str | Path,
    candidate_spec_path: str | Path,
    refined_profile: dict[str, Any],
    groups: dict[str, list[str]],
    groups_by_indicator: dict[str, str],
) -> dict[str, Any]:
    as_of = str(period.get("as_of"))
    failures: list[dict[str, Any]] = []
    try:
        score_payload = scorer(
            as_of=as_of,
            cache_dir=cache_dir,
            spec_path=candidate_spec_path,
            refined_profile=refined_profile,
        )
        scores = list(score_payload.get("scores", []))
        failures = list(score_payload.get("failures", []))
    except Exception as exc:  # noqa: BLE001 - diagnostics must keep producing scenario output.
        scores = []
        failures = [{"error_type": "BoomEndingCandidateScoringError", "message": str(exc)}]
    group_summary = build_boom_ending_group_summary(scores, groups)
    summary = build_boom_ending_point_summary(scores, failures, groups_by_indicator)
    summary["rates_policy_high_signal_count"] = _rates_policy_high_signal_count(group_summary)
    watch_status = classify_boom_ending_watch_status(summary, rule) if not failures else "missing"
    return {
        "as_of": as_of,
        "original_current_phase_id": period.get("current_phase_id"),
        "original_decision_status": period.get("decision_status"),
        "original_candidate_phase_id": period.get("candidate_phase_id"),
        "boom_ending_watch_status": watch_status,
        "weighted_boom_ending_score": summary["weighted_boom_ending_score"],
        "broad_group_count": summary["broad_group_count"],
        "high_signal_count": summary["high_signal_count"],
        "high_confidence_high_signal_count": summary["high_confidence_high_signal_count"],
        "rates_policy_high_signal_count": summary["rates_policy_high_signal_count"],
        "overlay_action": _overlay_action(watch_status),
        "reason_zh": _reason(watch_status),
        "candidate_failures": failures,
    }


def _scenario_summary(scenario_id: str, display_name_zh: str, periods: list[dict[str, Any]]) -> dict[str, Any]:
    watch_periods = [period for period in periods if period["boom_ending_watch_status"] == "watch"]
    strong_periods = [
        period for period in periods if period["boom_ending_watch_status"] == "strong_late_cycle_warning"
    ]
    weak_periods = [period for period in periods if period["boom_ending_watch_status"] == "weak"]
    none_periods = [period for period in periods if period["boom_ending_watch_status"] == "none"]
    original_confirmed = [
        period
        for period in periods
        if period["original_current_phase_id"] == "recession"
        and period["original_decision_status"] == "confirmed"
    ]
    first_watch = _first_as_of(watch_periods + strong_periods)
    first_original_confirmed = _first_as_of(original_confirmed)
    watch_lead_time = _month_delta(first_watch, first_original_confirmed) if first_watch and first_original_confirmed else None
    period_count = len(periods)
    summary = {
        "scenario_id": scenario_id,
        "display_name_zh": display_name_zh,
        "period_count": period_count,
        "watch_count": len(watch_periods),
        "strong_late_cycle_warning_count": len(strong_periods),
        "weak_count": len(weak_periods),
        "none_count": len(none_periods),
        "watch_density_ratio": _ratio(len(watch_periods) + len(strong_periods), period_count),
        "strong_density_ratio": _ratio(len(strong_periods), period_count),
        "first_watch_as_of": first_watch,
        "first_strong_warning_as_of": _first_as_of(strong_periods),
        "first_original_confirmed_recession_as_of": first_original_confirmed,
        "watch_lead_time_months": watch_lead_time,
        "longest_watch_streak_months": _longest_watch_streak(periods),
        "acceptance_status": "pass",
        "notes_zh": [],
    }
    status, notes = _scenario_acceptance(summary)
    summary["acceptance_status"] = status
    summary["notes_zh"] = notes
    return summary


def _scenario_acceptance(summary: dict[str, Any]) -> tuple[str, list[str]]:
    scenario_id = str(summary["scenario_id"])
    notes: list[str] = []
    excessive = _excessive_watch(summary)
    if scenario_id in {"dotcom_bubble", "global_financial_crisis"}:
        if summary["first_original_confirmed_recession_as_of"] and not summary["first_watch_as_of"]:
            return "fail", ["confirmed recession 前沒有 boom ending watch。"]
        if summary["watch_lead_time_months"] is not None and summary["watch_lead_time_months"] <= 0:
            return "fail", ["boom ending watch 沒有早於 confirmed recession。"]
        return "pass", ["confirmed recession 前已出現 boom ending watch。"]
    if scenario_id == "covid_recession":
        notes.append("COVID 屬外生衝擊案例，boom ending watch 可能是同步壓力反映，不代表事前預測。")
        return "warning", notes
    if scenario_id in {"euro_debt_slowdown", "late_cycle_2018"} and excessive:
        return "warning", ["non-recession scenario 出現偏高 watch density 或過長 watch streak。"]
    return "pass", notes


def _acceptance_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {summary["scenario_id"]: summary for summary in summaries}
    return {
        "pass_count": sum(1 for summary in summaries if summary["acceptance_status"] == "pass"),
        "warning_count": sum(1 for summary in summaries if summary["acceptance_status"] == "warning"),
        "fail_count": sum(1 for summary in summaries if summary["acceptance_status"] == "fail"),
        "dotcom_has_pre_recession_watch": _has_pre_recession_watch(by_id.get("dotcom_bubble", {})),
        "gfc_has_pre_recession_watch": _has_pre_recession_watch(by_id.get("global_financial_crisis", {})),
        "euro_debt_excessive_watch": _excessive_watch(by_id.get("euro_debt_slowdown", {})),
        "late_cycle_2018_excessive_watch": _excessive_watch(by_id.get("late_cycle_2018", {})),
    }


def _global_watch_density(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    total_period_count = sum(int(summary["period_count"]) for summary in summaries)
    total_watch_count = sum(int(summary["watch_count"]) for summary in summaries)
    total_strong_count = sum(int(summary["strong_late_cycle_warning_count"]) for summary in summaries)
    return {
        "total_period_count": total_period_count,
        "total_watch_count": total_watch_count,
        "total_strong_count": total_strong_count,
        "watch_density_ratio": _ratio(total_watch_count + total_strong_count, total_period_count),
        "strong_density_ratio": _ratio(total_strong_count, total_period_count),
    }


def _overlay_action(status: str) -> str:
    if status == "strong_late_cycle_warning":
        return "strong_late_cycle_warning"
    if status == "watch":
        return "watch_only"
    if status == "weak":
        return "weak_signal_only"
    if status == "missing":
        return "missing_candidate_data"
    return "no_action"


def _reason(status: str) -> str:
    if status == "strong_late_cycle_warning":
        return "多群組且高信心的 boom ending warning；此訊號不等於 confirmed recession。"
    if status == "watch":
        return "boom ending watch 僅作為 late-cycle early-warning diagnostics，不修改 current phase。"
    if status == "weak":
        return "僅有少數 boom ending 壓力訊號，維持 weak diagnostics。"
    if status == "missing":
        return "candidate data 不足，無法產生 boom ending watch overlay。"
    return "未達 boom ending watch 門檻。"


def _has_pre_recession_watch(summary: dict[str, Any]) -> bool:
    lead_time = summary.get("watch_lead_time_months")
    return lead_time is not None and lead_time > 0


def _excessive_watch(summary: dict[str, Any]) -> bool:
    return float(summary.get("watch_density_ratio", 0.0) or 0.0) > 0.65 or int(
        summary.get("longest_watch_streak_months", 0) or 0
    ) > 18


def _longest_watch_streak(periods: list[dict[str, Any]]) -> int:
    longest = 0
    current = 0
    for period in periods:
        if period["boom_ending_watch_status"] in {"watch", "strong_late_cycle_warning"}:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _first_as_of(periods: list[dict[str, Any]]) -> str | None:
    dates = sorted(str(period["as_of"]) for period in periods if period.get("as_of"))
    return dates[0] if dates else None


def _month_delta(start: str | None, end: str | None) -> int | None:
    if not start or not end:
        return None
    start_year, start_month = [int(part) for part in start[:7].split("-")]
    end_year, end_month = [int(part) for part in end[:7].split("-")]
    return (end_year - start_year) * 12 + (end_month - start_month)


def _rates_policy_high_signal_count(group_summary: list[dict[str, Any]]) -> int:
    for group in group_summary:
        if group.get("group_id") == "rates_policy":
            return int(group.get("high_signal_count", 0) or 0)
    return 0


def _groups_by_indicator(groups: dict[str, list[str]]) -> dict[str, str]:
    return {indicator_id: group_id for group_id, indicator_ids in groups.items() for indicator_id in indicator_ids}


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BoomEndingWatchOverlayError(f"boom ending watch overlay spec does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BoomEndingWatchOverlayError(f"Invalid YAML in boom ending watch overlay spec {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BoomEndingWatchOverlayError("boom ending watch overlay YAML must be a mapping")
    return payload


def _str_mapping(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise BoomEndingWatchOverlayError(f"{field} must be a mapping")
    return {str(key): str(raw) for key, raw in value.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise BoomEndingWatchOverlayError(f"{field} must be a list")
    if not all(isinstance(item, dict) for item in value):
        raise BoomEndingWatchOverlayError(f"{field} must contain mappings")
    return [dict(item) for item in value]


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BoomEndingWatchOverlayError(f"{field} must be a non-empty list")
    return [str(item) for item in value]

"""Full-horizon experimental overlay for recovery watch rule."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.backtests.catalog import load_backtest_scenario_catalog
from business_cycle.backtests.recovery_diagnostics import (
    build_recovery_group_summary,
    build_recovery_point_summary,
    load_experimental_indicator_groups,
)
from business_cycle.backtests.recovery_refinement_experiment import (
    _apply_status_caps,
    _score_refined_candidates,
    _should_raise_caveated_watch,
    load_recovery_scoring_refinement_experiment,
)
from business_cycle.backtests.recovery_watch_rule import (
    RecoveryWatchRule,
    evaluate_recovery_watch,
    load_recovery_watch_rule,
)
from business_cycle.backtests.runner import BacktestRunConfig, generate_monthly_periods, run_backtest
from business_cycle.indicators.experimental import (
    recovery_support_signal_score_cap,
    recession_context_gate_score,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/recovery_watch_overlay_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_watch_overlay/"
    "recovery_watch_overlay_report.json"
)
DEFAULT_EXISTING_TIMELINE_ROOTS = [
    Path("data/backtests/calibration/transition_controls_v2_breadth_full/experiment"),
    Path("data/backtests/calibration/transition_controls_v2_breadth_full/baseline"),
    Path("data/backtests/calibration/transition_controls_v1_full/experiment"),
    Path("data/backtests"),
]
ScoreFunction = Callable[..., dict[str, Any]]
TimelineLoader = Callable[[str], dict[str, Any] | None]


class RecoveryWatchOverlayError(ValueError):
    """Raised when recovery watch overlay cannot be built."""


@dataclass(frozen=True)
class RecoveryWatchOverlayExperiment:
    """Recovery watch overlay experiment spec."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    inputs: dict[str, str]
    overlay_policy: dict[str, Any]
    evaluation: dict[str, Any]
    acceptance_targets: list[dict[str, Any]]


def load_recovery_watch_overlay_experiment(
    path: str | Path = DEFAULT_SPEC_PATH,
) -> RecoveryWatchOverlayExperiment:
    """Load and validate recovery watch overlay experiment spec."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("recovery_watch_overlay_experiment")
    if not isinstance(raw, dict):
        raise RecoveryWatchOverlayError("recovery_watch_overlay_experiment YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    for required in [
        "修訂後歷史資料",
        "recovery watch 不等於正式復甦確認",
        "recovery watch 不是買進訊號",
        "policy easing 不得單獨確認 recovery",
        "financial easing 不得單獨確認 recovery",
        "不構成投資建議",
    ]:
        if not any(required in caveat for caveat in caveats):
            raise RecoveryWatchOverlayError(f"caveats_zh must include {required}")
    experiment = RecoveryWatchOverlayExperiment(
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
        raise RecoveryWatchOverlayError("version must be positive")
    return experiment


def build_recovery_watch_overlay_report(
    *,
    experiment_id: str = "recovery_watch_overlay_v1",
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    output_root: str | Path = "data/backtests/candidate_indicators/recovery_watch_overlay",
    cache_dir: str | Path = "data/raw/fred",
    reuse_existing: bool = False,
    force: bool = False,
    score_func: ScoreFunction | None = None,
    timeline_loader: TimelineLoader | None = None,
) -> dict[str, Any]:
    """Build full-horizon recovery watch overlay report."""

    experiment = load_recovery_watch_overlay_experiment(spec_path)
    rule = load_recovery_watch_rule(experiment.inputs["recovery_watch_rule"])
    refinement = load_recovery_scoring_refinement_experiment(
        experiment.inputs["recovery_refinement_experiment"]
    )
    profile = dict(refinement["refined_profile"])
    groups = load_experimental_indicator_groups("specs/common/experimental_indicator_groups.yaml")
    groups_by_indicator = _groups_by_indicator(groups)
    catalog = load_backtest_scenario_catalog(experiment.inputs["scenario_spec"])
    scorer = score_func or _score_recovery_refined_period
    scenario_summaries: list[dict[str, Any]] = []
    scenario_details: list[dict[str, Any]] = []

    for scenario in catalog.scenarios:
        timeline = _load_or_run_timeline(
            scenario_id=scenario.scenario_id,
            timeline_loader=timeline_loader,
            output_root=Path(output_root),
            scenario=scenario,
            reuse_existing=reuse_existing,
            force=force,
        )
        source_periods = [dict(period) for period in timeline.get("periods", [])]
        exogenous_shock = _scenario_has_exogenous_shock(scenario)
        periods = [
            _overlay_period(
                period=period,
                period_index=index,
                all_periods=source_periods,
                rule=rule,
                scorer=scorer,
                cache_dir=cache_dir,
                candidate_spec_path=experiment.inputs["recovery_candidate_spec"],
                refined_profile=profile,
                groups=groups,
                groups_by_indicator=groups_by_indicator,
                exogenous_shock_caveat=exogenous_shock,
            )
            for index, period in enumerate(source_periods)
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

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": experiment_id,
        "data_mode": experiment.data_mode,
        "scenario_count": len(scenario_summaries),
        "scenario_summaries": scenario_summaries,
        "scenario_details": scenario_details,
        "acceptance_summary": _acceptance_summary(scenario_summaries),
        "global_recovery_watch_density_summary": _global_recovery_watch_density(scenario_summaries),
        "caveats_zh": experiment.caveats_zh,
    }


def write_recovery_watch_overlay_report(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write recovery watch overlay report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _score_recovery_refined_period(
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
    reuse_existing: bool,
    force: bool,
) -> dict[str, Any]:
    if timeline_loader is not None:
        loaded = timeline_loader(scenario_id)
        if loaded is None:
            raise RecoveryWatchOverlayError(f"timeline_loader returned no timeline for {scenario_id}")
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
    period_index: int,
    all_periods: list[dict[str, Any]],
    rule: RecoveryWatchRule,
    scorer: ScoreFunction,
    cache_dir: str | Path,
    candidate_spec_path: str | Path,
    refined_profile: dict[str, Any],
    groups: dict[str, list[str]],
    groups_by_indicator: dict[str, str],
    exogenous_shock_caveat: bool,
) -> dict[str, Any]:
    as_of = str(period.get("as_of"))
    failures: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        score_payload = scorer(
            as_of=as_of,
            cache_dir=cache_dir,
            spec_path=candidate_spec_path,
            refined_profile=refined_profile,
        )
        scores = list(score_payload.get("scores", []))
        failures = list(score_payload.get("failures", []))
        warnings = [str(warning) for warning in score_payload.get("warnings", [])]
    except Exception as exc:  # noqa: BLE001 - overlay should preserve scenario output.
        scores = []
        failures = [{"error_type": "RecoveryCandidateScoringError", "message": str(exc)}]
    context = _recession_context_for_period(
        period_index=period_index,
        periods=all_periods,
        exogenous_shock_caveat=exogenous_shock_caveat,
        lookback_months=int(refined_profile.get("recession_context_gate", {}).get("lookback_months", 12)),
    )
    summary = build_recovery_point_summary(scores, failures, groups_by_indicator)
    group_summary = build_recovery_group_summary(scores, groups)
    support_cap = recovery_support_signal_score_cap(
        scores,
        groups_by_indicator,
        refined_profile.get("support_signal_cap", {}),
    )
    context_gate = recession_context_gate_score(
        context,
        scores,
        {
            **dict(refined_profile.get("recession_context_gate", {})),
            "exogenous_max_status": refined_profile.get("exogenous_shock_profile", {}).get(
                "max_status_without_labor_confirmation",
                "watch",
            ),
        },
    )
    adjusted_status, status_adjustments = _apply_status_caps(
        str(summary["recovery_status"]),
        support_cap,
        context_gate,
    )
    if _should_raise_caveated_watch(context, summary, adjusted_status, refined_profile):
        adjusted_status = "watch"
        status_adjustments.append(
            {
                "kind": "exogenous_shock_caveated_watch_floor",
                "reason_zh": "外生衝擊 trough 附近允許 caveated recovery watch，但不代表一般景氣循環復甦確認。",
            }
        )
    point_summary = {
        **summary,
        "refined_status": adjusted_status,
        "support_signal_cap_applied": bool(support_cap.get("support_only_cap_applied")),
        "context_gate_applied": bool(context_gate.get("context_gate_applied")),
        "recession_context_detected": bool(context_gate.get("recession_context_detected")),
        "exogenous_shock_caveat": bool(context_gate.get("exogenous_shock_caveat")),
        "exogenous_shock_caveated_watch_floor": any(
            adjustment.get("kind") == "exogenous_shock_caveated_watch_floor"
            for adjustment in status_adjustments
        ),
    }
    evaluation = evaluate_recovery_watch(point_summary, rule) if not failures else {
        "experimental_recovery_watch_status": "missing",
        "reason_zh": "candidate data 不足，無法產生 recovery watch overlay。",
    }
    status = str(evaluation["experimental_recovery_watch_status"])
    return {
        "as_of": as_of,
        "original_current_phase_id": period.get("current_phase_id"),
        "original_decision_status": period.get("decision_status"),
        "original_candidate_phase_id": period.get("candidate_phase_id"),
        "recovery_watch_status": status,
        "weighted_recovery_score": summary["weighted_recovery_score"],
        "broad_group_count": summary["broad_group_count"],
        "high_signal_count": summary["high_signal_count"],
        "high_confidence_high_signal_count": summary["high_confidence_high_signal_count"],
        "policy_only_signal": summary["policy_only_signal"],
        "support_signal_cap_applied": point_summary["support_signal_cap_applied"],
        "context_gate_applied": point_summary["context_gate_applied"],
        "recession_context_detected": point_summary["recession_context_detected"],
        "exogenous_shock_caveat": point_summary["exogenous_shock_caveat"],
        "overlay_action": _overlay_action(status),
        "reason_zh": str(evaluation["reason_zh"]),
        "candidate_failures": failures,
        "candidate_warnings": warnings,
        "group_summary": group_summary,
        "status_adjustments": status_adjustments,
    }


def _recession_context_for_period(
    *,
    period_index: int,
    periods: list[dict[str, Any]],
    exogenous_shock_caveat: bool,
    lookback_months: int,
) -> dict[str, Any]:
    window = periods[max(0, period_index - lookback_months + 1) : period_index + 1]
    recent_formal = any(str(period.get("current_phase_id")) == "recession" for period in window)
    recession_scores = [_phase_score(period, "recession") for period in window]
    recession_depth_proxy_score = max(recession_scores) if recession_scores else 0.0
    recent_recession_watch = any(
        str(period.get("current_phase_id")) == "recession"
        or str(period.get("candidate_phase_id")) == "recession"
        and _phase_score(period, "recession") >= 60.0
        for period in window
    )
    return {
        "recent_formal_recession_phase": recent_formal,
        "recent_recession_candidate_watch_or_confirmed": recent_recession_watch,
        "recession_depth_proxy_score": round(recession_depth_proxy_score, 4),
        "exogenous_shock_caveat": exogenous_shock_caveat,
    }


def _scenario_summary(scenario_id: str, display_name_zh: str, periods: list[dict[str, Any]]) -> dict[str, Any]:
    watch_periods = [period for period in periods if period["recovery_watch_status"] == "recovery_watch"]
    strong_periods = [period for period in periods if period["recovery_watch_status"] == "strong_recovery_watch"]
    weak_periods = [period for period in periods if period["recovery_watch_status"] == "weak"]
    none_periods = [period for period in periods if period["recovery_watch_status"] == "none"]
    original_recovery = [period for period in periods if period["original_current_phase_id"] == "recovery"]
    original_confirmed_recession = [
        period
        for period in periods
        if period["original_current_phase_id"] == "recession"
        and period["original_decision_status"] == "confirmed"
    ]
    first_watch = _first_as_of(watch_periods + strong_periods)
    first_original_recovery = _first_as_of(original_recovery)
    period_count = len(periods)
    summary = {
        "scenario_id": scenario_id,
        "display_name_zh": display_name_zh,
        "period_count": period_count,
        "recovery_watch_count": len(watch_periods),
        "strong_recovery_watch_count": len(strong_periods),
        "weak_count": len(weak_periods),
        "none_count": len(none_periods),
        "recovery_watch_density_ratio": _ratio(len(watch_periods) + len(strong_periods), period_count),
        "strong_recovery_watch_density_ratio": _ratio(len(strong_periods), period_count),
        "first_recovery_watch_as_of": first_watch,
        "first_strong_recovery_watch_as_of": _first_as_of(strong_periods),
        "first_original_recovery_phase_as_of": first_original_recovery,
        "first_original_confirmed_recession_as_of": _first_as_of(original_confirmed_recession),
        "watch_lead_or_lag_months_vs_original_recovery": _month_delta(first_watch, first_original_recovery)
        if first_watch and first_original_recovery
        else None,
        "longest_recovery_watch_streak_months": _longest_watch_streak(periods),
        "policy_only_blocked_count": sum(1 for period in periods if period["support_signal_cap_applied"]),
        "context_gate_blocked_count": sum(1 for period in periods if period["context_gate_applied"]),
        "exogenous_shock_caveat_count": sum(1 for period in periods if period["exogenous_shock_caveat"]),
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
        if not summary["first_recovery_watch_as_of"]:
            return "fail", ["recession trough / recovery initial 附近沒有 recovery watch。"]
        if float(summary["recovery_watch_density_ratio"]) > 0.65:
            notes.append("recovery watch density 偏高，future integration 需要 guardrails。")
            return "warning", notes
        return "pass", ["recession trough / recovery initial 附近已出現 recovery watch。"]
    if scenario_id == "covid_recession":
        notes.append("COVID 屬外生衝擊案例，recovery watch 需 caveat，不代表一般景氣循環復甦。")
        return "warning", notes
    if scenario_id in {"euro_debt_slowdown", "late_cycle_2018"} and excessive:
        return "warning", ["non-recession scenario 出現偏高 recovery watch density 或過長 streak。"]
    return "pass", notes


def _acceptance_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {summary["scenario_id"]: summary for summary in summaries}
    return {
        "pass_count": sum(1 for summary in summaries if summary["acceptance_status"] == "pass"),
        "warning_count": sum(1 for summary in summaries if summary["acceptance_status"] == "warning"),
        "fail_count": sum(1 for summary in summaries if summary["acceptance_status"] == "fail"),
        "gfc_has_trough_or_recovery_watch": _has_recovery_watch(by_id.get("global_financial_crisis", {})),
        "dotcom_has_recovery_watch": _has_recovery_watch(by_id.get("dotcom_bubble", {})),
        "covid_caveated_recovery_watch": _covid_caveated_watch(by_id.get("covid_recession", {})),
        "euro_debt_excessive_recovery_watch": _excessive_watch(by_id.get("euro_debt_slowdown", {})),
        "late_cycle_2018_excessive_recovery_watch": _excessive_watch(by_id.get("late_cycle_2018", {})),
    }


def _global_recovery_watch_density(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    total_period_count = sum(int(summary["period_count"]) for summary in summaries)
    total_watch_count = sum(int(summary["recovery_watch_count"]) for summary in summaries)
    total_strong_count = sum(int(summary["strong_recovery_watch_count"]) for summary in summaries)
    return {
        "total_period_count": total_period_count,
        "total_recovery_watch_count": total_watch_count,
        "total_strong_recovery_watch_count": total_strong_count,
        "recovery_watch_density_ratio": _ratio(total_watch_count + total_strong_count, total_period_count),
        "strong_recovery_watch_density_ratio": _ratio(total_strong_count, total_period_count),
    }


def _overlay_action(status: str) -> str:
    if status == "strong_recovery_watch":
        return "strong_recovery_watch"
    if status == "recovery_watch":
        return "watch_only"
    if status == "weak":
        return "weak_signal_only"
    if status == "missing":
        return "missing_candidate_data"
    return "no_action"


def _phase_score(period: dict[str, Any], phase_id: str) -> float:
    for score in period.get("phase_scores", []):
        if isinstance(score, dict) and score.get("phase_id") == phase_id:
            return float(score.get("score") or 0.0)
    return 0.0


def _scenario_has_exogenous_shock(scenario: Any) -> bool:
    text = " ".join(
        [
            str(getattr(scenario, "scenario_id", "")),
            str(getattr(scenario, "display_name_zh", "")),
            str(getattr(scenario, "display_name_en", "")),
            str(getattr(scenario, "benchmark_notes_zh", "")),
            " ".join(str(item) for item in getattr(scenario, "expected_focus_zh", [])),
        ]
    ).lower()
    return "外生衝擊" in text or "covid" in text


def _has_recovery_watch(summary: dict[str, Any]) -> bool:
    return bool(summary.get("first_recovery_watch_as_of"))


def _covid_caveated_watch(summary: dict[str, Any]) -> bool:
    return _has_recovery_watch(summary) and int(summary.get("exogenous_shock_caveat_count", 0) or 0) > 0


def _excessive_watch(summary: dict[str, Any]) -> bool:
    return float(summary.get("recovery_watch_density_ratio", 0.0) or 0.0) > 0.65 or int(
        summary.get("longest_recovery_watch_streak_months", 0) or 0
    ) > 18


def _longest_watch_streak(periods: list[dict[str, Any]]) -> int:
    longest = 0
    current = 0
    for period in periods:
        if period["recovery_watch_status"] in {"recovery_watch", "strong_recovery_watch"}:
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


def _groups_by_indicator(groups: dict[str, list[str]]) -> dict[str, str]:
    return {indicator_id: group_id for group_id, indicator_ids in groups.items() for indicator_id in indicator_ids}


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RecoveryWatchOverlayError(f"recovery watch overlay spec does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RecoveryWatchOverlayError(f"Invalid YAML in recovery watch overlay spec {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecoveryWatchOverlayError("recovery watch overlay YAML must be a mapping")
    return payload


def _str_mapping(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise RecoveryWatchOverlayError(f"{field} must be a mapping")
    return {str(key): str(raw) for key, raw in value.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise RecoveryWatchOverlayError(f"{field} must be a list")
    if not all(isinstance(item, dict) for item in value):
        raise RecoveryWatchOverlayError(f"{field} must contain mappings")
    return [dict(item) for item in value]


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RecoveryWatchOverlayError(f"{field} must be a non-empty list")
    return [str(item) for item in value]

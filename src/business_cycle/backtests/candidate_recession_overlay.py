"""Full-horizon experimental overlay for candidate recession confirmation."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.backtests.candidate_indicators import score_candidate_indicators
from business_cycle.backtests.candidate_recession_diagnostics import build_candidate_point_summary
from business_cycle.backtests.candidate_recession_rule import (
    CandidateRecessionConfirmationRule,
    classify_candidate_recession_status,
    load_candidate_recession_confirmation_rule,
)
from business_cycle.backtests.catalog import load_backtest_scenario_catalog
from business_cycle.backtests.runner import BacktestRunConfig, run_backtest

DEFAULT_SPEC_PATH = Path("specs/backtests/candidate_recession_overlay_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recession_confirmation_overlay/"
    "candidate_recession_overlay_report.json"
)
DEFAULT_EXISTING_TIMELINE_ROOTS = [
    Path("data/backtests/calibration/transition_controls_v2_breadth_full/experiment"),
    Path("data/backtests/calibration/transition_controls_v1_full/experiment"),
    Path("data/backtests"),
]

ScoreFunction = Callable[..., dict[str, Any]]


class CandidateRecessionOverlayError(ValueError):
    """Raised when candidate recession overlay cannot be built."""


@dataclass(frozen=True)
class CandidateRecessionOverlayExperiment:
    """Candidate recession overlay experiment spec."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    inputs: dict[str, str]
    overlay_policy: dict[str, Any]
    acceptance_targets: list[dict[str, Any]]


def load_candidate_recession_overlay_experiment(
    path: str | Path = DEFAULT_SPEC_PATH,
) -> CandidateRecessionOverlayExperiment:
    """Load and validate candidate recession overlay experiment spec."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("candidate_recession_overlay_experiment")
    if not isinstance(raw, dict):
        raise CandidateRecessionOverlayError("candidate_recession_overlay_experiment YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise CandidateRecessionOverlayError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise CandidateRecessionOverlayError("caveats_zh must include no-investment-advice caveat")
    experiment = CandidateRecessionOverlayExperiment(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        objective_zh=str(raw.get("objective_zh", "")),
        caveats_zh=caveats,
        inputs=_str_mapping(raw.get("inputs"), "inputs"),
        overlay_policy=dict(raw.get("overlay_policy") or {}),
        acceptance_targets=_list_of_mappings(raw.get("acceptance_targets"), "acceptance_targets"),
    )
    if experiment.version < 1:
        raise CandidateRecessionOverlayError("version must be positive")
    return experiment


def build_candidate_recession_overlay_report(
    *,
    experiment_id: str = "candidate_recession_overlay_v1",
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    output_root: str | Path = "data/backtests/candidate_indicators/recession_confirmation_overlay",
    cache_dir: str | Path = "data/raw/fred",
    reuse_existing: bool = False,
    force: bool = False,
    score_func: ScoreFunction | None = None,
    timeline_loader: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Build full-horizon candidate recession overlay report."""

    experiment = load_candidate_recession_overlay_experiment(spec_path)
    rule = load_candidate_recession_confirmation_rule(experiment.inputs["candidate_rule_spec"])
    catalog = load_backtest_scenario_catalog(experiment.inputs["scenario_spec"])
    scorer = score_func or score_candidate_indicators
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
        periods = []
        for period in timeline.get("periods", []):
            overlay_period = _overlay_period(
                period=dict(period),
                rule=rule,
                scorer=scorer,
                cache_dir=cache_dir,
                candidate_spec_path=experiment.inputs["candidate_indicator_spec"],
            )
            periods.append(overlay_period)
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
        "caveats_zh": experiment.caveats_zh,
    }


def write_candidate_recession_overlay_report(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write candidate recession overlay report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load_or_run_timeline(
    *,
    scenario_id: str,
    timeline_loader: Callable[[str], dict[str, Any] | None] | None,
    output_root: Path,
    scenario: Any,
    scenario_spec_path: Path,
    reuse_existing: bool,
    force: bool,
) -> dict[str, Any]:
    if timeline_loader is not None:
        loaded = timeline_loader(scenario_id)
        if loaded is None:
            raise CandidateRecessionOverlayError(f"timeline_loader returned no timeline for {scenario_id}")
        return loaded

    if not force:
        for root in DEFAULT_EXISTING_TIMELINE_ROOTS:
            path = root / scenario_id / "timeline.json"
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))

    generated_path = output_root / "timelines" / scenario_id / "timeline.json"
    if reuse_existing and not force and generated_path.exists():
        return json.loads(generated_path.read_text(encoding="utf-8"))

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
    rule: CandidateRecessionConfirmationRule,
    scorer: ScoreFunction,
    cache_dir: str | Path,
    candidate_spec_path: str | Path,
) -> dict[str, Any]:
    as_of = str(period.get("as_of"))
    try:
        score_payload = scorer(as_of=as_of, cache_dir=cache_dir, spec_path=candidate_spec_path)
        scores = list(score_payload.get("scores", []))
        failures = list(score_payload.get("failures", []))
    except Exception as exc:  # noqa: BLE001 - diagnostics must not crash a scenario.
        scores = []
        failures = [{"error_type": "CandidateScoringError", "message": str(exc)}]

    candidate_summary = build_candidate_point_summary(scores, failures, _groups_by_indicator())
    candidate_status = classify_candidate_recession_status(candidate_summary, rule) if not failures else "missing"
    original_current = period.get("current_phase_id")
    original_candidate = period.get("candidate_phase_id")
    original_status = period.get("decision_status")
    is_original_confirmed_recession = original_current == "recession" and original_status == "confirmed"
    is_recession_review = is_original_confirmed_recession or original_candidate == "recession"
    overlay_action = "no_action"
    overlay_current = original_current
    overlay_status = original_status
    reason = "candidate overlay 未介入此 period。"

    if failures:
        overlay_action = "missing_candidate_data"
        reason = "candidate indicator 資料不足，overlay 不修改原始判讀。"
    elif is_original_confirmed_recession and candidate_status == "confirmed":
        overlay_action = "confirm_supported"
        reason = "原始 confirmed recession 獲得 candidate rule 支持。"
    elif is_original_confirmed_recession and candidate_status != "confirmed":
        overlay_action = "downgrade_confirmed_to_watch"
        overlay_current = period.get("previous_phase_id") or original_current
        overlay_status = "transition_watch"
        reason = "原始 confirmed recession 未達 candidate confirmed 門檻，experimental overlay 降級為 transition_watch。"
    elif is_recession_review and candidate_status == "watch":
        overlay_action = "candidate_watch_only"
        reason = "candidate rule 顯示 recession watch，但不足以 confirmed。"

    return {
        "as_of": as_of,
        "original_current_phase_id": original_current,
        "original_decision_status": original_status,
        "original_candidate_phase_id": original_candidate,
        "candidate_recession_status": candidate_status,
        "candidate_weighted_confirmation_score": candidate_summary["weighted_confirmation_score"],
        "candidate_broad_group_count": candidate_summary["broad_group_count"],
        "candidate_high_signal_count": candidate_summary["high_signal_count"],
        "candidate_high_confidence_high_signal_count": candidate_summary["high_confidence_high_signal_count"],
        "overlay_action": overlay_action,
        "overlay_current_phase_id": overlay_current,
        "overlay_decision_status": overlay_status,
        "reason_zh": reason,
        "candidate_failures": failures,
    }


def _scenario_summary(scenario_id: str, display_name_zh: str, periods: list[dict[str, Any]]) -> dict[str, Any]:
    original_confirmed = [
        period
        for period in periods
        if period["original_current_phase_id"] == "recession"
        and period["original_decision_status"] == "confirmed"
    ]
    overlay_confirmed = [
        period
        for period in periods
        if period["overlay_current_phase_id"] == "recession"
        and period["overlay_decision_status"] == "confirmed"
    ]
    candidate_confirmed = [period for period in periods if period["candidate_recession_status"] == "confirmed"]
    summary = {
        "scenario_id": scenario_id,
        "display_name_zh": display_name_zh,
        "period_count": len(periods),
        "original_confirmed_recession_count": len(original_confirmed),
        "candidate_supported_confirmed_count": _count_action(periods, "confirm_supported"),
        "downgraded_confirmed_count": _count_action(periods, "downgrade_confirmed_to_watch"),
        "candidate_watch_count": sum(1 for period in periods if period["candidate_recession_status"] == "watch"),
        "missing_candidate_data_count": _count_action(periods, "missing_candidate_data"),
        "first_original_confirmed_recession_as_of": _first_as_of(original_confirmed),
        "first_overlay_confirmed_recession_as_of": _first_as_of(overlay_confirmed),
        "first_candidate_confirmed_as_of": _first_as_of(candidate_confirmed),
        "acceptance_status": "pass",
        "notes_zh": [],
    }
    summary["acceptance_status"], summary["notes_zh"] = _scenario_acceptance(summary)
    return summary


def _scenario_acceptance(summary: dict[str, Any]) -> tuple[str, list[str]]:
    scenario_id = summary["scenario_id"]
    notes: list[str] = []
    if summary["missing_candidate_data_count"] > 0:
        return "warning", ["部分 period 缺少 candidate 資料，overlay 結果需保守解讀。"]
    if scenario_id == "covid_recession":
        first_overlay = summary["first_overlay_confirmed_recession_as_of"]
        if first_overlay is not None and first_overlay < "2020-02-01":
            return "fail", ["COVID 2019 early false recession 仍維持 overlay confirmed。"]
        if summary["first_candidate_confirmed_as_of"] is None:
            return "warning", ["COVID 2020 期間沒有 candidate confirmed 訊號。"]
        return "pass", ["COVID early false confirmed 已被降低，且 2020 期間有 candidate confirmed。"]
    if scenario_id == "global_financial_crisis":
        return (
            ("pass", ["GFC 有 candidate confirmed 支持。"])
            if summary["candidate_supported_confirmed_count"] > 0 or summary["first_candidate_confirmed_as_of"]
            else ("fail", ["GFC 缺少 candidate confirmed 支持。"])
        )
    if scenario_id == "dotcom_bubble":
        return (
            ("pass", ["dotcom 至少有 watch 或 confirmed candidate 訊號。"])
            if summary["candidate_watch_count"] > 0 or summary["first_candidate_confirmed_as_of"]
            else ("warning", ["dotcom 缺少 candidate watch 訊號。"])
        )
    if scenario_id in {"euro_debt_slowdown", "late_cycle_2018"}:
        return (
            ("fail", ["out-of-sample scenario 出現 overlay confirmed recession。"])
            if summary["first_overlay_confirmed_recession_as_of"] is not None
            else ("pass", ["out-of-sample scenario 未新增 overlay confirmed recession。"])
        )
    return "pass", notes


def _acceptance_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {summary["scenario_id"]: summary for summary in summaries}
    statuses = [summary["acceptance_status"] for summary in summaries]
    out_of_sample_false = sum(
        1
        for scenario_id in ("euro_debt_slowdown", "late_cycle_2018")
        if by_id.get(scenario_id, {}).get("first_overlay_confirmed_recession_as_of") is not None
    )
    covid = by_id.get("covid_recession", {})
    gfc = by_id.get("global_financial_crisis", {})
    return {
        "pass_count": statuses.count("pass"),
        "warning_count": statuses.count("warning"),
        "fail_count": statuses.count("fail"),
        "blocked_covid_2019_false_confirmed": covid.get("first_overlay_confirmed_recession_as_of") is None
        or covid.get("first_overlay_confirmed_recession_as_of") >= "2020-02-01",
        "kept_gfc_confirmed": bool(gfc.get("candidate_supported_confirmed_count") or gfc.get("first_candidate_confirmed_as_of")),
        "kept_covid_2020_confirmed": bool(covid.get("first_candidate_confirmed_as_of")),
        "out_of_sample_false_confirmed_count": out_of_sample_false,
    }


def _groups_by_indicator() -> dict[str, str]:
    return {
        "continuing_jobless_claims": "employment",
        "insured_unemployment_rate": "employment",
        "unemployment_duration_15_weeks_over": "employment",
        "real_personal_consumption_expenditures": "consumption",
        "industrial_production": "production",
        "credit_spread_baa_aaa": "credit_financial_conditions",
        "financial_stress_index": "credit_financial_conditions",
    }


def _count_action(periods: list[dict[str, Any]], action: str) -> int:
    return sum(1 for period in periods if period["overlay_action"] == action)


def _first_as_of(periods: list[dict[str, Any]]) -> str | None:
    if not periods:
        return None
    return str(sorted(period["as_of"] for period in periods)[0])


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CandidateRecessionOverlayError(f"candidate recession overlay spec does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CandidateRecessionOverlayError(f"Invalid YAML in candidate recession overlay spec {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CandidateRecessionOverlayError("candidate recession overlay spec YAML must be a mapping")
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CandidateRecessionOverlayError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise CandidateRecessionOverlayError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CandidateRecessionOverlayError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CandidateRecessionOverlayError(f"{field} entries must be non-empty")
    return items


def _str_mapping(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise CandidateRecessionOverlayError(f"{field} must be a non-empty mapping")
    return {str(key): str(raw_value) for key, raw_value in value.items()}

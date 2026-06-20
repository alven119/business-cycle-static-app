"""Experimental comparison for recovery scoring refinements."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from business_cycle.backtests.recovery_candidates import (
    load_recovery_candidate_indicators,
    score_recovery_candidate_indicators,
)
from business_cycle.backtests.recovery_diagnostics import (
    build_recovery_group_summary,
    build_recovery_point_summary,
    load_experimental_indicator_groups,
    load_recovery_diagnostic_windows,
)
from business_cycle.indicators.experimental import (
    bottoming_momentum_score_refined,
    peak_reversal_score_refined,
    recovery_support_signal_score_cap,
    recession_context_gate_score,
    score_to_dict,
)

DEFAULT_EXPERIMENT_PATH = Path("specs/backtests/recovery_scoring_refinement_experiment.yaml")
DEFAULT_WINDOWS_PATH = Path("specs/backtests/recovery_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/recovery_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_refinement/recovery_refinement_experiment.json"
)

STATUS_ORDER = {"none": 0, "weak": 1, "watch": 2, "strong": 3}
RefinedScoreFunction = Callable[..., dict[str, Any]]


class RecoveryRefinementExperimentError(ValueError):
    """Raised when recovery refinement experiment cannot be built."""


def load_recovery_scoring_refinement_experiment(path: str | Path) -> dict[str, Any]:
    """Load and validate recovery scoring refinement experiment YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RecoveryRefinementExperimentError(
            f"Recovery scoring refinement experiment file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RecoveryRefinementExperimentError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecoveryRefinementExperimentError("experiment YAML must be a mapping")
    experiment = payload.get("recovery_scoring_refinement_experiment")
    if not isinstance(experiment, dict):
        raise RecoveryRefinementExperimentError(
            "YAML must contain recovery_scoring_refinement_experiment mapping"
        )
    if int(experiment.get("version", 0)) < 1:
        raise RecoveryRefinementExperimentError("version must exist")
    if not isinstance(experiment.get("refined_profile"), dict):
        raise RecoveryRefinementExperimentError("refined_profile must exist")
    if not isinstance(experiment.get("expected_refinement_outcomes"), list):
        raise RecoveryRefinementExperimentError("expected_refinement_outcomes must exist")
    caveats = [str(caveat) for caveat in experiment.get("caveats_zh", [])]
    for required in ["修訂後歷史資料", "recovery watch 不等於正式復甦確認", "policy easing 不得單獨確認 recovery", "不構成投資建議"]:
        if not any(required in caveat for caveat in caveats):
            raise RecoveryRefinementExperimentError(f"caveats_zh must include {required}")
    return experiment


def build_recovery_refinement_experiment(
    *,
    experiment_path: str | Path = DEFAULT_EXPERIMENT_PATH,
    windows_path: str | Path | None = None,
    candidate_spec_path: str | Path | None = None,
    groups_path: str | Path = DEFAULT_GROUPS_PATH,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    baseline_diagnostics: dict[str, Any] | None = None,
    refined_score_func: RefinedScoreFunction | None = None,
) -> dict[str, Any]:
    """Build baseline-vs-refined recovery scoring comparison."""

    experiment = load_recovery_scoring_refinement_experiment(experiment_path)
    inputs = dict(experiment.get("inputs", {}))
    candidate_spec = Path(candidate_spec_path or inputs.get("recovery_candidate_spec", DEFAULT_CANDIDATE_SPEC_PATH))
    windows = load_recovery_diagnostic_windows(windows_path or inputs.get("recovery_diagnostic_windows", DEFAULT_WINDOWS_PATH))
    baseline = baseline_diagnostics or _load_baseline_diagnostics(inputs)
    window_keys = {(point.scenario_id, point.as_of, point.label) for point in windows.points}
    baseline_lookup_warnings: list[dict[str, Any]] = []
    baseline_by_key = _baseline_by_key(baseline, window_keys, baseline_lookup_warnings)
    groups = load_experimental_indicator_groups(groups_path)
    groups_by_indicator = _groups_by_indicator(groups)
    profile = dict(experiment["refined_profile"])
    expected = _expected_by_key(experiment.get("expected_refinement_outcomes", []))
    scorer = refined_score_func or _score_refined_candidates
    points: list[dict[str, Any]] = []

    for point in windows.points:
        key = (point.scenario_id, point.as_of, point.label)
        point_lookup_warnings: list[dict[str, Any]] = []
        baseline_point = baseline_by_key.get(key)
        baseline_summary = _extract_baseline_summary(baseline_point, key, point_lookup_warnings)
        baseline_lookup_warnings.extend(point_lookup_warnings)
        refined_payload = scorer(
            as_of=point.as_of,
            cache_dir=Path(cache_dir),
            spec_path=candidate_spec,
            refined_profile=profile,
        )
        refined_scores = list(refined_payload.get("scores", []))
        failures = list(refined_payload.get("failures", []))
        refined_summary = build_recovery_point_summary(refined_scores, failures, groups_by_indicator)
        group_summary = build_recovery_group_summary(refined_scores, groups)
        support_cap = recovery_support_signal_score_cap(
            refined_scores,
            groups_by_indicator,
            profile.get("support_signal_cap", {}),
        )
        context_gate = recession_context_gate_score(
            point.context,
            refined_scores,
            {
                **dict(profile.get("recession_context_gate", {})),
                "exogenous_max_status": profile.get("exogenous_shock_profile", {}).get(
                    "max_status_without_labor_confirmation",
                    "watch",
                ),
            },
        )
        adjusted_status, status_adjustments = _apply_status_caps(
            str(refined_summary["recovery_status"]),
            support_cap,
            context_gate,
        )
        if _should_raise_caveated_watch(point.context, refined_summary, adjusted_status, profile):
            adjusted_status = "watch"
            status_adjustments.append(
                {
                    "kind": "exogenous_shock_caveated_watch_floor",
                    "reason_zh": "外生衝擊 trough 附近允許 caveated recovery watch，但不代表一般景氣循環復甦確認。",
                }
            )
        baseline_status = str(baseline_summary.get("recovery_status", "none"))
        baseline_score = float(baseline_summary.get("weighted_recovery_score", 0.0) or 0.0)
        refined_score = float(refined_summary.get("weighted_recovery_score", 0.0) or 0.0)
        expected_result = _expected_result(expected.get(key, {}), adjusted_status)
        points.append(
            {
                "scenario_id": point.scenario_id,
                "as_of": point.as_of,
                "label": point.label,
                "baseline_status": baseline_status,
                "refined_status": adjusted_status,
                "baseline_score": baseline_score,
                "refined_score": refined_score,
                "status_delta": _status_delta_for_point(point.expected_status, baseline_status, adjusted_status),
                "expected_result": expected_result,
                "context": point.context,
                "context_gate_applied": bool(context_gate.get("context_gate_applied")),
                "support_signal_cap_applied": bool(support_cap.get("support_only_cap_applied")),
                "support_cap_summary": support_cap,
                "context_gate_summary": context_gate,
                "status_adjustments": status_adjustments,
                "candidate_summary_before_caps": refined_summary,
                "refined_group_summary": group_summary,
                "top_refined_indicators": _top_scores(refined_scores),
                "diagnostic_notes_zh": _notes(point.context, support_cap, context_gate, expected_result),
                "failures": failures,
                "warnings": list(refined_payload.get("warnings", [])),
                "baseline_lookup_warnings": point_lookup_warnings,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": profile.get("profile_id", "recovery_refined"),
        "data_mode": experiment.get("data_mode", "revised"),
        "point_count": len(points),
        "baseline_lookup_warning_count": len(baseline_lookup_warnings),
        "baseline_lookup_warnings": baseline_lookup_warnings,
        "points": points,
        "summary": _summary(points),
        "refinement_candidates_still_open": _still_open(points),
        "caveats_zh": experiment.get("caveats_zh", []),
    }


def write_recovery_refinement_experiment(output_path: str | Path, experiment: dict[str, Any]) -> Path:
    """Write recovery refinement experiment JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(experiment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _score_refined_candidates(
    *,
    as_of: str,
    cache_dir: Path,
    spec_path: str | Path,
    refined_profile: dict[str, Any],
) -> dict[str, Any]:
    base_payload = score_recovery_candidate_indicators(as_of=as_of, cache_dir=cache_dir, spec_path=spec_path)
    spec = load_recovery_candidate_indicators(spec_path)
    score_by_id = {
        str(score["indicator_id"]): {**score, "refined_score_source": "baseline"}
        for score in base_payload.get("scores", [])
    }
    failures = list(base_payload.get("failures", []))
    warnings = list(base_payload.get("warnings", []))
    for indicator in spec.indicators:
        indicator_id = str(indicator["indicator_id"])
        try:
            refined = _refined_score_for_indicator(indicator_id, indicator, cache_dir, as_of, refined_profile)
        except FileNotFoundError as exc:
            warnings.append(f"refined scoring missing local cache for {indicator_id}: {exc}")
            continue
        if refined is None:
            continue
        score_dict = score_to_dict(refined)
        score_dict["display_name_zh"] = indicator.get("display_name_zh")
        score_dict["purpose_group"] = indicator.get("purpose_group")
        score_dict["selected_series_id"] = indicator.get("preferred_series")
        score_dict["selected_series_ids"] = []
        score_dict["derived_formula"] = indicator.get("derived_formula")
        score_dict["refined_score_source"] = "refined"
        score_dict["baseline_candidate_score"] = score_by_id.get(indicator_id)
        score_by_id[indicator_id] = score_dict
    return {
        **base_payload,
        "scores": list(score_by_id.values()),
        "failures": failures,
        "warnings": warnings,
        "scored_candidates": len(score_by_id),
        "failed_candidates": len(failures),
    }


def _refined_score_for_indicator(
    indicator_id: str,
    indicator: dict[str, Any],
    cache_dir: Path,
    as_of: str,
    refined_profile: dict[str, Any],
) -> Any:
    if indicator_id in {
        "initial_jobless_claims_peak_reversal",
        "continuing_jobless_claims_peak_reversal",
        "short_term_unemployment_peak_reversal",
    }:
        return peak_reversal_score_refined(
            _load_indicator_frame(indicator, cache_dir),
            indicator_id=indicator_id,
            as_of=as_of,
            config=refined_profile.get("labor_reversal", {}),
        )
    if indicator_id in {
        "real_retail_sales_bottoming",
        "real_pce_bottoming",
        "durable_goods_orders_bottoming",
        "industrial_production_bottoming",
    }:
        return bottoming_momentum_score_refined(
            _load_indicator_frame(indicator, cache_dir),
            indicator_id=indicator_id,
            as_of=as_of,
            config=refined_profile.get("real_activity_bottoming", {}),
        )
    return None


def _load_indicator_frame(indicator: dict[str, Any], cache_dir: Path) -> pd.DataFrame:
    formula = str(indicator.get("derived_formula") or "")
    if formula == "BAA - AAA":
        left = _read_series(cache_dir, "BAA")
        right = _read_series(cache_dir, "AAA")
        merged = left.rename(columns={"value": "left"}).merge(
            right.rename(columns={"value": "right"}),
            on="date",
            how="inner",
        )
        merged["value"] = merged["left"] - merged["right"]
        return merged[["date", "value"]]
    preferred = indicator.get("preferred_series")
    candidates = [str(item) for item in indicator.get("candidate_fred_series", [])]
    ordered = [str(preferred)] + [item for item in candidates if item != preferred] if preferred else candidates
    for series_id in ordered:
        path = cache_dir / f"{series_id.upper()}.csv"
        if path.exists():
            return _read_series(cache_dir, series_id)
    raise FileNotFoundError(f"missing local raw CSV for series candidates={ordered}")


def _read_series(cache_dir: Path, series_id: str) -> pd.DataFrame:
    path = cache_dir / f"{series_id.upper()}.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame[["date", "value"]]


def _load_baseline_diagnostics(inputs: dict[str, Any]) -> dict[str, Any]:
    path = Path(inputs.get("baseline_diagnostics", ""))
    if not path.exists():
        raise RecoveryRefinementExperimentError(
            f"baseline diagnostics file does not exist: {path}; run scripts/run_recovery_diagnostics.py first"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecoveryRefinementExperimentError(f"Invalid baseline diagnostics JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecoveryRefinementExperimentError("baseline diagnostics JSON must be an object")
    return payload


def _baseline_by_key(
    baseline: dict[str, Any],
    window_keys: set[tuple[str, str, str]],
    warnings: list[dict[str, Any]],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    baseline_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for point in baseline.get("points", []):
        key = _point_key(point)
        if key is None:
            warnings.append({"kind": "baseline_lookup", "missing_field": "scenario_id/as_of/label"})
            continue
        baseline_by_key[key] = point
    for key in sorted(set(baseline_by_key) - window_keys):
        warnings.append(
            {
                "kind": "baseline_lookup",
                "scenario_id": key[0],
                "as_of": key[1],
                "label": key[2],
                "unmatched_key": True,
            }
        )
    return baseline_by_key


def _point_key(point: dict[str, Any]) -> tuple[str, str, str] | None:
    if point.get("scenario_id") is None or point.get("as_of") is None or point.get("label") is None:
        return None
    return str(point["scenario_id"]), str(point["as_of"]), str(point["label"])


def _extract_baseline_summary(
    baseline_point: dict[str, Any] | None,
    key: tuple[str, str, str],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    if baseline_point is None:
        warnings.append(_baseline_warning(key, "unmatched_key"))
        return {}
    summary = baseline_point.get("candidate_summary")
    if not isinstance(summary, dict):
        warnings.append(_baseline_warning(key, "candidate_summary"))
        return {}
    for field in ["recovery_status", "weighted_recovery_score"]:
        if field not in summary and field not in baseline_point:
            warnings.append(_baseline_warning(key, f"candidate_summary.{field}"))
    return {
        **summary,
        "recovery_status": baseline_point.get("recovery_status", summary.get("recovery_status", "none")),
    }


def _baseline_warning(key: tuple[str, str, str], missing_field: str) -> dict[str, Any]:
    return {
        "kind": "baseline_lookup",
        "scenario_id": key[0],
        "as_of": key[1],
        "label": key[2],
        "missing_field": missing_field,
    }


def _apply_status_caps(
    status: str,
    support_cap: dict[str, Any],
    context_gate: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    adjusted = status
    adjustments: list[dict[str, Any]] = []
    support_max = str(support_cap.get("max_allowed_status_after_support_cap", "strong"))
    if STATUS_ORDER[adjusted] > STATUS_ORDER[support_max]:
        adjusted = support_max
        adjustments.append({"kind": "support_signal_cap", "max_status": support_max})
    context_max = str(context_gate.get("max_allowed_status_after_context", "strong"))
    if STATUS_ORDER[adjusted] > STATUS_ORDER[context_max]:
        adjusted = context_max
        adjustments.append({"kind": "recession_context_gate", "max_status": context_max})
    return adjusted, adjustments


def _should_raise_caveated_watch(
    context: dict[str, Any],
    summary: dict[str, Any],
    status: str,
    profile: dict[str, Any],
) -> bool:
    shock_profile = dict(profile.get("exogenous_shock_profile", {}))
    if not shock_profile.get("enabled", False) or not shock_profile.get("allow_fast_trough_watch_with_caveat", False):
        return False
    if not context.get("exogenous_shock_caveat"):
        return False
    if STATUS_ORDER[status] >= STATUS_ORDER["watch"]:
        return False
    if float(summary.get("weighted_recovery_score", 0.0) or 0.0) < 55.0:
        return False
    return bool(summary.get("credit_financial_confirmed") or summary.get("real_activity_confirmed"))


def _expected_by_key(items: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (str(item["scenario_id"]), str(item["as_of"]), str(item["label"])): item
        for item in items
    }


def _expected_result(expected: dict[str, Any], refined_status: str) -> str:
    if not expected:
        return "warning"
    if "expected_min_status" in expected:
        return "pass" if STATUS_ORDER[refined_status] >= STATUS_ORDER[str(expected["expected_min_status"])] else "fail"
    if "expected_max_status" in expected:
        return "pass" if STATUS_ORDER[refined_status] <= STATUS_ORDER[str(expected["expected_max_status"])] else "fail"
    return "warning"


def _status_delta_for_point(expected_status: str, baseline_status: str, refined_status: str) -> str:
    if _status_matches(refined_status, expected_status) and not _status_matches(baseline_status, expected_status):
        return "improved"
    if not _status_matches(refined_status, expected_status) and _status_matches(baseline_status, expected_status):
        return "regressed"
    if STATUS_ORDER[refined_status] == STATUS_ORDER[baseline_status]:
        return "unchanged"
    if expected_status == "weak_or_none":
        return "improved" if STATUS_ORDER[refined_status] < STATUS_ORDER[baseline_status] else "regressed"
    return "improved" if STATUS_ORDER[refined_status] > STATUS_ORDER[baseline_status] else "regressed"


def _status_matches(status: str, expected: str) -> bool:
    if expected == "watch_or_strong":
        return status in {"watch", "strong"}
    if expected == "weak_or_watch":
        return status in {"weak", "watch"}
    if expected == "weak_or_none":
        return status in {"weak", "none"}
    return status == expected


def _summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "improved_count": sum(1 for point in points if point["status_delta"] == "improved"),
        "unchanged_count": sum(1 for point in points if point["status_delta"] == "unchanged"),
        "regressed_count": sum(1 for point in points if point["status_delta"] == "regressed"),
        "expected_pass_count": sum(1 for point in points if point["expected_result"] == "pass"),
        "expected_warning_count": sum(1 for point in points if point["expected_result"] == "warning"),
        "expected_fail_count": sum(1 for point in points if point["expected_result"] == "fail"),
        "euro_debt_false_strong_fixed": _status_for(points, "euro_debt_non_recession") in {"weak", "none"},
        "late_cycle_2018_false_watch_fixed": _status_for(points, "late_cycle_2018_non_recession") in {"weak", "none"},
        "gfc_trough_watch_preserved": _status_for(points, "gfc_trough_area") in {"watch", "strong"},
        "gfc_recovery_watch_preserved": _status_for(points, "gfc_recovery_initial") in {"watch", "strong"},
        "dotcom_recovery_watch_improved": _status_for(points, "dotcom_recovery_initial") in {"watch", "strong"},
        "covid_trough_watch_improved": _status_for(points, "covid_trough_area") in {"watch", "strong"},
        "policy_only_strong_blocked": all(
            not (
                point["candidate_summary_before_caps"].get("policy_only_signal")
                and point["refined_status"] == "strong"
            )
            for point in points
        ),
    }


def _still_open(points: list[dict[str, Any]]) -> list[str]:
    open_items: list[str] = []
    if _status_for(points, "dotcom_recovery_initial") not in {"watch", "strong"}:
        open_items.append("labor_reversal_persistence_tuning")
    if _status_for(points, "covid_trough_area") not in {"watch", "strong"}:
        open_items.append("covid_exogenous_shock_profile")
    if _status_for(points, "euro_debt_non_recession") == "strong":
        open_items.append("recession_context_gate")
    if _status_for(points, "late_cycle_2018_non_recession") not in {"weak", "none"}:
        open_items.append("policy_and_financial_support_cap")
    return open_items


def _status_for(points: list[dict[str, Any]], label: str) -> str:
    for point in points:
        if point["label"] == label:
            return str(point["refined_status"])
    return "none"


def _top_scores(scores: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "indicator_id": score.get("indicator_id"),
                "score": score.get("score"),
                "confidence": score.get("confidence"),
                "reason_zh": score.get("reason_zh"),
                "refined_score_source": score.get("refined_score_source"),
            }
            for score in scores
        ],
        key=lambda item: (float(item.get("score") or 0.0), float(item.get("confidence") or 0.0)),
        reverse=True,
    )[:limit]


def _groups_by_indicator(groups: dict[str, list[str]]) -> dict[str, str]:
    return {
        str(indicator_id): str(group_id)
        for group_id, indicator_ids in groups.items()
        for indicator_id in indicator_ids
    }


def _notes(
    context: dict[str, Any],
    support_cap: dict[str, Any],
    context_gate: dict[str, Any],
    expected_result: str,
) -> list[str]:
    notes = ["此 comparison 只比較 experimental recovery scoring，不會修改正式模型判斷。"]
    if support_cap.get("support_only_cap_applied"):
        notes.append("policy / financial easing cap 已套用，support signal 不得單獨確認 recovery。")
    if context_gate.get("context_gate_applied"):
        notes.append("recession context gate 已套用，缺少 recession context 時不允許 recovery watch/strong。")
    if context.get("exogenous_shock_caveat"):
        notes.append("外生衝擊案例中，COVID 快速反彈不等同一般景氣循環復甦。")
    if expected_result == "fail":
        notes.append("此 point 未達 expected refinement outcome，需保留為 open refinement item。")
    return notes

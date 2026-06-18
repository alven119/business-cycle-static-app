"""Experimental comparison for boom-ending scoring refinements."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from business_cycle.backtests.boom_ending_candidates import (
    load_boom_ending_candidate_indicators,
    score_boom_ending_candidate_indicators,
)
from business_cycle.backtests.boom_ending_diagnostics import (
    build_boom_ending_group_summary,
    build_boom_ending_point_summary,
    load_boom_ending_diagnostic_windows,
    load_experimental_indicator_groups,
)
from business_cycle.indicators.experimental import (
    credit_spread_velocity_score,
    fed_policy_peak_pause_pressure_score,
    financial_conditions_delta_score,
    score_to_dict,
    yield_curve_lead_time_pressure_score,
)

DEFAULT_EXPERIMENT_PATH = Path("specs/backtests/boom_ending_scoring_refinement_experiment.yaml")
DEFAULT_WINDOWS_PATH = Path("specs/backtests/boom_ending_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/boom_ending_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_refinement/"
    "boom_ending_refinement_experiment.json"
)

STATUS_ORDER = {"none": 0, "weak": 1, "watch": 2, "strong": 3}
RefinedScoreFunction = Callable[..., dict[str, Any]]


class BoomEndingRefinementExperimentError(ValueError):
    """Raised when boom-ending refinement experiment cannot be built."""


def load_boom_ending_scoring_refinement_experiment(path: str | Path) -> dict[str, Any]:
    """Load and validate boom-ending scoring refinement experiment YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BoomEndingRefinementExperimentError(
            f"Boom ending scoring refinement experiment file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BoomEndingRefinementExperimentError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BoomEndingRefinementExperimentError("experiment YAML must be a mapping")
    experiment = payload.get("boom_ending_scoring_refinement_experiment")
    if not isinstance(experiment, dict):
        raise BoomEndingRefinementExperimentError(
            "YAML must contain boom_ending_scoring_refinement_experiment mapping"
        )
    if int(experiment.get("version", 0)) < 1:
        raise BoomEndingRefinementExperimentError("version must exist")
    if not experiment.get("refined_profile"):
        raise BoomEndingRefinementExperimentError("refined_profile must exist")
    if not experiment.get("expected_refinement_outcomes"):
        raise BoomEndingRefinementExperimentError("expected_refinement_outcomes must exist")
    caveats = list(experiment.get("caveats_zh", []))
    if not any("修訂後歷史資料" in str(caveat) for caveat in caveats):
        raise BoomEndingRefinementExperimentError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in str(caveat) for caveat in caveats):
        raise BoomEndingRefinementExperimentError("caveats_zh must include no-investment-advice caveat")
    return experiment


def build_boom_ending_refinement_experiment(
    *,
    experiment_path: str | Path = DEFAULT_EXPERIMENT_PATH,
    windows_path: str | Path = DEFAULT_WINDOWS_PATH,
    candidate_spec_path: str | Path = DEFAULT_CANDIDATE_SPEC_PATH,
    groups_path: str | Path = DEFAULT_GROUPS_PATH,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    baseline_diagnostics: dict[str, Any] | None = None,
    refined_score_func: RefinedScoreFunction | None = None,
) -> dict[str, Any]:
    """Build baseline-vs-refined boom-ending scoring comparison."""

    experiment = load_boom_ending_scoring_refinement_experiment(experiment_path)
    baseline = baseline_diagnostics or _load_baseline_diagnostics(experiment)
    windows = load_boom_ending_diagnostic_windows(windows_path)
    window_keys = {(point.scenario_id, point.as_of, point.label) for point in windows.points}
    baseline_lookup_warnings: list[dict[str, Any]] = []
    baseline_by_key = _baseline_by_key(baseline, window_keys, baseline_lookup_warnings)
    groups = load_experimental_indicator_groups(groups_path)
    groups_by_indicator = _groups_by_indicator(groups)
    refined_profile = dict(experiment["refined_profile"])
    expected = _expected_by_key(experiment.get("expected_refinement_outcomes", []))
    points: list[dict[str, Any]] = []

    for point in windows.points:
        baseline_key = (point.scenario_id, point.as_of, point.label)
        point_lookup_warnings: list[dict[str, Any]] = []
        baseline_point = baseline_by_key.get(baseline_key)
        baseline_summary = _extract_baseline_summary(
            baseline_point,
            baseline_key,
            point_lookup_warnings,
        )
        baseline_lookup_warnings.extend(point_lookup_warnings)
        scorer = refined_score_func or _score_refined_candidates
        refined_payload = scorer(
            as_of=point.as_of,
            cache_dir=Path(cache_dir),
            spec_path=candidate_spec_path,
            refined_profile=refined_profile,
        )
        refined_scores = list(refined_payload.get("scores", []))
        failures = list(refined_payload.get("failures", []))
        refined_summary = build_boom_ending_point_summary(refined_scores, failures, groups_by_indicator)
        baseline_status = str(baseline_summary.get("boom_ending_status", "none"))
        refined_status = str(refined_summary["boom_ending_status"])
        baseline_score = float(baseline_summary.get("weighted_boom_ending_score", 0.0))
        refined_score = float(refined_summary["weighted_boom_ending_score"])
        expected_result = _expected_result(
            expected.get((point.scenario_id, point.as_of), {}),
            refined_status,
        )
        points.append(
            {
                "scenario_id": point.scenario_id,
                "as_of": point.as_of,
                "label": point.label,
                "baseline_status": baseline_status,
                "refined_status": refined_status,
                "baseline_score": baseline_score,
                "refined_score": refined_score,
                "baseline_broad_group_count": baseline_summary.get("broad_group_count", 0),
                "baseline_high_signal_count": baseline_summary.get("high_signal_count", 0),
                "baseline_high_confidence_high_signal_count": baseline_summary.get(
                    "high_confidence_high_signal_count",
                    0,
                ),
                "refined_broad_group_count": refined_summary["broad_group_count"],
                "refined_high_signal_count": refined_summary["high_signal_count"],
                "refined_high_confidence_high_signal_count": refined_summary[
                    "high_confidence_high_signal_count"
                ],
                "status_delta": _status_delta(baseline_status, refined_status),
                "score_delta": round(refined_score - baseline_score, 4),
                "top_baseline_indicators": _top_scores(list(baseline_point.get("top_candidate_scores", [])))
                if baseline_point
                else [],
                "baseline_group_summary": baseline_point.get("group_summary", []) if baseline_point else [],
                "top_refined_indicators": _top_scores(refined_scores),
                "refined_group_summary": build_boom_ending_group_summary(refined_scores, groups),
                "expected_result": expected_result,
                "diagnostic_notes_zh": _notes(baseline_status, refined_status, expected_result),
                "failures": failures,
                "warnings": list(refined_payload.get("warnings", [])),
                "baseline_lookup_warnings": point_lookup_warnings,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": refined_profile.get("profile_id", "boom_ending_refined"),
        "data_mode": experiment.get("data_mode", "revised"),
        "point_count": len(points),
        "points": points,
        "summary": _summary(points),
        "refinement_candidates_still_open": _still_open(points),
        "baseline_lookup_warning_count": len(baseline_lookup_warnings),
        "baseline_lookup_warnings": baseline_lookup_warnings,
        "caveats_zh": experiment.get("caveats_zh", []),
    }


def write_boom_ending_refinement_experiment(
    output_path: str | Path,
    experiment: dict[str, Any],
) -> Path:
    """Write boom-ending refinement experiment JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(experiment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _baseline_by_key(
    baseline: dict[str, Any],
    window_keys: set[tuple[str, str, str]],
    warnings: list[dict[str, Any]],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    baseline_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for point in baseline.get("points", []):
        key = _point_key(point)
        if key is None:
            warnings.append(
                {
                    "kind": "baseline_lookup",
                    "missing_field": "scenario_id/as_of/label",
                    "message_zh": "baseline diagnostics point 缺少 scenario_id、as_of 或 label，無法比對。",
                }
            )
            continue
        if key in baseline_by_key:
            warnings.append(
                {
                    "kind": "baseline_lookup",
                    "scenario_id": key[0],
                    "as_of": key[1],
                    "label": key[2],
                    "missing_field": "unique_key",
                    "message_zh": "baseline diagnostics 出現重複 key，後一筆會覆蓋前一筆。",
                }
            )
        baseline_by_key[key] = point
    for key in sorted(set(baseline_by_key) - window_keys):
        warnings.append(
            {
                "kind": "baseline_lookup",
                "scenario_id": key[0],
                "as_of": key[1],
                "label": key[2],
                "unmatched_key": True,
                "message_zh": "baseline diagnostics point 不在 refinement diagnostic windows 中。",
            }
        )
    return baseline_by_key


def _point_key(point: dict[str, Any]) -> tuple[str, str, str] | None:
    scenario_id = point.get("scenario_id")
    as_of = point.get("as_of")
    label = point.get("label")
    if scenario_id is None or as_of is None or label is None:
        return None
    return str(scenario_id), str(as_of), str(label)


def _extract_baseline_summary(
    baseline_point: dict[str, Any] | None,
    key: tuple[str, str, str],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    if baseline_point is None:
        warnings.append(_baseline_warning(key, "unmatched_key", "找不到對應的 baseline diagnostics point。"))
        return {}
    summary = baseline_point.get("candidate_summary")
    if not isinstance(summary, dict):
        warnings.append(
            _baseline_warning(
                key,
                "candidate_summary",
                "baseline diagnostics point 缺少 candidate_summary。",
            )
        )
        return {}
    if "boom_ending_status" not in summary:
        warnings.append(
            _baseline_warning(
                key,
                "candidate_summary.boom_ending_status",
                "baseline diagnostics candidate_summary 缺少 boom_ending_status。",
            )
        )
    if "weighted_boom_ending_score" not in summary:
        warnings.append(
            _baseline_warning(
                key,
                "candidate_summary.weighted_boom_ending_score",
                "baseline diagnostics candidate_summary 缺少 weighted_boom_ending_score。",
            )
        )
    if "broad_group_count" not in summary:
        warnings.append(
            _baseline_warning(
                key,
                "candidate_summary.broad_group_count",
                "baseline diagnostics candidate_summary 缺少 broad_group_count。",
            )
        )
    return summary


def _baseline_warning(
    key: tuple[str, str, str],
    missing_field: str,
    message_zh: str,
) -> dict[str, Any]:
    return {
        "kind": "baseline_lookup",
        "scenario_id": key[0],
        "as_of": key[1],
        "label": key[2],
        "missing_field": missing_field,
        "message_zh": message_zh,
    }


def _score_refined_candidates(
    *,
    as_of: str,
    cache_dir: Path,
    spec_path: str | Path,
    refined_profile: dict[str, Any],
) -> dict[str, Any]:
    base_payload = score_boom_ending_candidate_indicators(
        as_of=as_of,
        cache_dir=cache_dir,
        spec_path=spec_path,
    )
    spec = load_boom_ending_candidate_indicators(spec_path)
    score_by_id = {str(score["indicator_id"]): score for score in base_payload.get("scores", [])}
    failures = list(base_payload.get("failures", []))
    warnings = list(base_payload.get("warnings", []))
    for indicator in spec.indicators:
        indicator_id = str(indicator["indicator_id"])
        try:
            refined = _refined_score_for_indicator(
                indicator_id=indicator_id,
                indicator=indicator,
                cache_dir=cache_dir,
                as_of=as_of,
                refined_profile=refined_profile,
            )
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
    *,
    indicator_id: str,
    indicator: dict[str, Any],
    cache_dir: Path,
    as_of: str,
    refined_profile: dict[str, Any],
) -> Any:
    if indicator_id in {"yield_curve_10y_3m", "yield_curve_10y_2y"}:
        return yield_curve_lead_time_pressure_score(
            _read_series(cache_dir, str(indicator["preferred_series"])),
            indicator_id=indicator_id,
            as_of=as_of,
            config=refined_profile.get("yield_curve", {}),
        )
    if indicator_id == "credit_spread_baa_10y":
        primary = _spread(cache_dir, "BAA", "DGS10")
        alternative = _spread(cache_dir, "BAA", "AAA") if (cache_dir / "AAA.csv").exists() else None
        return credit_spread_velocity_score(
            primary,
            alternative,
            indicator_id=indicator_id,
            as_of=as_of,
            config=refined_profile.get("credit_spread", {}),
        )
    if indicator_id == "financial_conditions_tightening":
        return financial_conditions_delta_score(
            _read_series(cache_dir, str(indicator["preferred_series"])),
            indicator_id=indicator_id,
            as_of=as_of,
            config=refined_profile.get("financial_conditions", {}),
        )
    if indicator_id == "fed_policy_restrictive_pressure":
        return fed_policy_peak_pause_pressure_score(
            _read_series(cache_dir, str(indicator["preferred_series"])),
            indicator_id=indicator_id,
            as_of=as_of,
            config=refined_profile.get("fed_policy", {}),
        )
    return None


def _spread(cache_dir: Path, left: str, right: str) -> pd.DataFrame:
    left_frame = _read_series(cache_dir, left)
    right_frame = _read_series(cache_dir, right)
    merged = left_frame.rename(columns={"value": "left"}).merge(
        right_frame.rename(columns={"value": "right"}),
        on="date",
        how="inner",
    )
    merged["value"] = merged["left"] - merged["right"]
    return merged[["date", "value"]]


def _read_series(cache_dir: Path, series_id: str) -> pd.DataFrame:
    path = cache_dir / f"{series_id.upper()}.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame[["date", "value"]]


def _load_baseline_diagnostics(experiment: dict[str, Any]) -> dict[str, Any]:
    path = Path(experiment.get("baseline", {}).get("diagnostics_path", ""))
    if not path.exists():
        raise BoomEndingRefinementExperimentError(
            f"baseline diagnostics file does not exist: {path}; run scripts/run_boom_ending_diagnostics.py first"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _expected_by_key(items: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(str(item["scenario_id"]), str(item["as_of"])): item for item in items}


def _groups_by_indicator(groups: dict[str, list[str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for group_id, indicator_ids in groups.items():
        for indicator_id in indicator_ids:
            mapping[str(indicator_id)] = str(group_id)
    return mapping


def _expected_result(expected: dict[str, Any], refined_status: str) -> str:
    if not expected:
        return "warning"
    if "expected_min_status" in expected:
        return "pass" if STATUS_ORDER[refined_status] >= STATUS_ORDER[str(expected["expected_min_status"])] else "fail"
    if "expected_max_status" in expected:
        return "pass" if STATUS_ORDER[refined_status] <= STATUS_ORDER[str(expected["expected_max_status"])] else "fail"
    return "warning"


def _status_delta(baseline_status: str, refined_status: str) -> str:
    delta = STATUS_ORDER[refined_status] - STATUS_ORDER[baseline_status]
    if delta > 0:
        return "improved"
    if delta < 0:
        return "regressed"
    return "unchanged"


def _summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "improved_count": sum(1 for point in points if point["status_delta"] == "improved"),
        "unchanged_count": sum(1 for point in points if point["status_delta"] == "unchanged"),
        "regressed_count": sum(1 for point in points if point["status_delta"] == "regressed"),
        "expected_pass_count": sum(1 for point in points if point["expected_result"] == "pass"),
        "expected_warning_count": sum(1 for point in points if point["expected_result"] == "warning"),
        "expected_fail_count": sum(1 for point in points if point["expected_result"] == "fail"),
        "gfc_2006_improved_to_watch": _status_for(points, "gfc_yield_curve_warning") in {"watch", "strong"},
        "gfc_2007_improved_to_watch": _status_for(points, "gfc_recession_window_start") in {"watch", "strong"},
        "dotcom_watch_preserved": _status_for(points, "dotcom_market_peak_area") in {"watch", "strong"},
        "late_cycle_2018_not_strong": _status_for(points, "late_cycle_2018_warning") != "strong",
        "euro_debt_not_strong": _status_for(points, "euro_debt_slowdown_warning") != "strong",
    }


def _still_open(points: list[dict[str, Any]]) -> list[str]:
    open_items: list[str] = []
    if _status_for(points, "gfc_yield_curve_warning") not in {"watch", "strong"}:
        open_items.append("yield_curve_lead_time_pressure")
    if _status_for(points, "gfc_recession_window_start") not in {"watch", "strong"}:
        open_items.append("financial_conditions_delta_score")
    if any(
        item["expected_result"] == "fail" and item["label"] in {"late_cycle_2018_warning", "euro_debt_slowdown_warning"}
        for item in points
    ):
        open_items.append("boom_ending_watch_rule_thresholds")
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
            }
            for score in scores
        ],
        key=lambda item: (float(item.get("score") or 0), float(item.get("confidence") or 0)),
        reverse=True,
    )[:limit]


def _notes(baseline_status: str, refined_status: str, expected_result: str) -> list[str]:
    notes = ["此 comparison 只比較 experimental boom ending scoring，不會修改正式模型判斷。"]
    if _status_delta(baseline_status, refined_status) == "improved":
        notes.append("refined scoring 提高了此 diagnostic point 的 early-warning status。")
    if expected_result == "fail":
        notes.append("此 point 未達 expected refinement outcome，後續仍需調整或保留為 open item。")
    return notes

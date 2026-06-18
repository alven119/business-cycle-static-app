"""Attribution builder for boom-ending candidate diagnostics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BoomEndingAttributionError(ValueError):
    """Raised when boom-ending attribution cannot be built."""


DEFAULT_DIAGNOSTICS_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_diagnostics/"
    "boom_ending_diagnostics.json"
)
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_diagnostics/"
    "boom_ending_attribution.json"
)

IMPORTANT_INDICATORS = {
    "yield_curve_10y_3m",
    "yield_curve_10y_2y",
    "fed_policy_restrictive_pressure",
    "financial_conditions_tightening",
    "credit_spread_baa_10y",
    "oil_price_pressure",
    "industrial_production_momentum_loss",
}


def build_boom_ending_attribution(diagnostics: dict[str, Any]) -> dict[str, Any]:
    """Build attribution from a boom-ending diagnostics payload."""

    points = list(diagnostics.get("points", []))
    if not points:
        raise BoomEndingAttributionError("boom-ending diagnostics must include points")
    attributed_points = [_attribute_point(point) for point in points]
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "data_mode": diagnostics.get("data_mode", "revised"),
        "point_count": len(attributed_points),
        "points": attributed_points,
        "comparisons": _build_comparisons(attributed_points),
        "refinement_candidates": _refinement_candidates(diagnostics, attributed_points),
        "caveats_zh": [
            "使用修訂後歷史資料，不等同當時投資人可見資料。",
            "此為 experimental diagnostics，不代表正式模型已更新。",
            "不構成投資建議。",
        ],
    }


def write_boom_ending_attribution(
    output_path: str | Path,
    attribution: dict[str, Any],
) -> Path:
    """Write boom-ending attribution JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(attribution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_boom_ending_attribution_from_file(
    diagnostics_path: str | Path = DEFAULT_DIAGNOSTICS_PATH,
) -> dict[str, Any]:
    """Load diagnostics JSON and build boom-ending attribution."""

    path = Path(diagnostics_path)
    if not path.exists():
        raise BoomEndingAttributionError(
            f"Boom ending diagnostics file does not exist: {path}. "
            "Run scripts/run_boom_ending_diagnostics.py first."
        )
    try:
        diagnostics = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BoomEndingAttributionError(f"Invalid diagnostics JSON: {path}: {exc}") from exc
    if not isinstance(diagnostics, dict):
        raise BoomEndingAttributionError("boom-ending diagnostics JSON must be an object")
    return build_boom_ending_attribution(diagnostics)


def _attribute_point(point: dict[str, Any]) -> dict[str, Any]:
    summary = dict(point.get("candidate_summary", {}))
    top_scores = list(point.get("top_candidate_scores", []))
    groups = list(point.get("group_summary", []))
    top_positive = [
        _indicator_summary(score)
        for score in top_scores
        if _num(score.get("score")) >= 65.0 and _num(score.get("confidence")) >= 0.5
    ]
    weak_important = [
        _indicator_summary(score)
        for score in top_scores
        if str(score.get("indicator_id")) in IMPORTANT_INDICATORS
        and _num(score.get("score")) < 65.0
    ]
    return {
        "scenario_id": point.get("scenario_id"),
        "as_of": point.get("as_of"),
        "label": point.get("label"),
        "boom_ending_status": summary.get("boom_ending_status"),
        "weighted_boom_ending_score": summary.get("weighted_boom_ending_score", 0.0),
        "top_positive_indicators": top_positive,
        "weak_but_important_indicators": weak_important,
        "group_contributions": _group_contributions(groups),
        "high_signal_indicators": [item["indicator_id"] for item in top_positive],
        "diagnostic_notes_zh": _notes(point, top_positive, weak_important),
    }


def _indicator_summary(score: dict[str, Any]) -> dict[str, Any]:
    return {
        "indicator_id": score.get("indicator_id"),
        "display_name_zh": score.get("display_name_zh"),
        "score": score.get("score"),
        "confidence": score.get("confidence"),
        "reason_zh": score.get("reason_zh"),
    }


def _group_contributions(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "group_id": group.get("group_id"),
                "scored_indicator_count": group.get("scored_indicator_count", 0),
                "high_signal_count": group.get("high_signal_count", 0),
                "avg_score": group.get("avg_score", 0.0),
                "avg_confidence": group.get("avg_confidence", 0.0),
                "status": group.get("status"),
            }
            for group in groups
        ],
        key=lambda item: (_num(item["avg_score"]), _num(item["high_signal_count"])),
        reverse=True,
    )


def _build_comparisons(points: list[dict[str, Any]]) -> dict[str, Any]:
    by_label = {str(point["label"]): point for point in points}
    comparisons: dict[str, Any] = {}
    comparisons["dotcom_progression"] = _progression(
        [by_label.get("dotcom_market_peak_area"), by_label.get("dotcom_recession_window")],
        "dotcom 從市場高點附近到 recession window 的 late-cycle pressure 變化。",
    )
    comparisons["gfc_progression"] = _progression(
        [
            by_label.get("gfc_yield_curve_warning"),
            by_label.get("gfc_recession_window_start"),
            by_label.get("gfc_confirmed_recession"),
        ],
        "GFC 2006/2007 偏弱但 2008 轉為 watch，需檢查 yield curve lead time 與 credit/financial stress scoring。",
    )
    comparisons["covid_2019_vs_2020"] = _progression(
        [by_label.get("covid_2019_false_recession_context"), by_label.get("covid_shock_recession")],
        "COVID 2019 watch 與 2020 shock 反映 boom ending 指標不是 confirmed recession rule。",
    )
    comparisons["late_cycle_2018_vs_euro_debt"] = _progression(
        [by_label.get("late_cycle_2018_warning"), by_label.get("euro_debt_slowdown_warning")],
        "比較非 confirmed recession 案例中的 late-cycle pressure，避免把 watch/weak 解讀為正式衰退。",
    )
    return comparisons


def _progression(points: list[dict[str, Any] | None], interpretation_zh: str) -> dict[str, Any]:
    valid = [point for point in points if point]
    return {
        "points": [str(point["as_of"]) for point in valid],
        "score_trend": [_num(point.get("weighted_boom_ending_score")) for point in valid],
        "status_trend": [str(point.get("boom_ending_status")) for point in valid],
        "top_positive_indicator_trend": [
            [str(item["indicator_id"]) for item in point.get("top_positive_indicators", [])]
            for point in valid
        ],
        "interpretation_zh": interpretation_zh,
    }


def _refinement_candidates(
    diagnostics: dict[str, Any],
    attributed_points: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    aggregate = diagnostics.get("aggregate", {})
    requiring_refinement = set(aggregate.get("candidate_indicators_requiring_refinement", []))
    if "credit_spread_baa_10y" in requiring_refinement or _credit_spread_is_weak(attributed_points):
        candidates.append(
            {
                "indicator_id": "credit_spread_baa_10y",
                "reason_zh": "BAA - DGS10 可能混入 Treasury yield level，需與 BAA - AAA、spread velocity 或 percentile proxy 比較。",
                "priority": "high",
            }
        )
    candidates.append(
        {
            "indicator_id": "yield_curve_10y_3m",
            "reason_zh": "GFC 2006/2007 主要由 yield curve 提供訊號，應加入 6~18 個月 lead-time pressure。",
            "priority": "high",
        }
    )
    candidates.append(
        {
            "indicator_id": "yield_curve_10y_2y",
            "reason_zh": "10Y-2Y 對 dotcom 與 GFC early warning 有貢獻，需檢查倒掛後持續期間與 lead-time scoring。",
            "priority": "high",
        }
    )
    return candidates


def _credit_spread_is_weak(points: list[dict[str, Any]]) -> bool:
    for point in points:
        ids = {item["indicator_id"] for item in point.get("top_positive_indicators", [])}
        if "credit_spread_baa_10y" in ids:
            return False
    return True


def _notes(
    point: dict[str, Any],
    top_positive: list[dict[str, Any]],
    weak_important: list[dict[str, Any]],
) -> list[str]:
    notes = ["此 attribution 只解釋 boom ending diagnostics，不會修改正式模型判斷。"]
    if point.get("label") in {"gfc_yield_curve_warning", "gfc_recession_window_start"}:
        notes.append("GFC 早期仍偏 weak，需檢查 yield curve lead time 與 credit/financial stress 計分。")
    if top_positive:
        notes.append("本期有高分候選指標，但仍需檢查是否具備多群組廣度。")
    if weak_important:
        notes.append("部分重要候選指標分數偏弱，可能需要 scoring refinement 或替代 proxy。")
    return notes


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

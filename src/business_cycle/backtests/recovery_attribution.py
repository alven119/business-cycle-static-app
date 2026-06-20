"""Attribution builder for recovery candidate diagnostics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RecoveryAttributionError(ValueError):
    """Raised when recovery attribution cannot be built."""


DEFAULT_DIAGNOSTICS_PATH = Path(
    "data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json"
)
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_diagnostics/recovery_attribution.json"
)

IMPORTANT_INDICATORS = {
    "initial_jobless_claims_peak_reversal",
    "continuing_jobless_claims_peak_reversal",
    "short_term_unemployment_peak_reversal",
    "real_retail_sales_bottoming",
    "real_pce_bottoming",
    "durable_goods_orders_bottoming",
    "industrial_production_bottoming",
    "credit_spread_easing",
    "financial_stress_easing",
    "fed_policy_easing_signal",
}


def build_recovery_attribution(diagnostics: dict[str, Any]) -> dict[str, Any]:
    """Build attribution from a recovery diagnostics payload."""

    points = list(diagnostics.get("points", []))
    if not points:
        raise RecoveryAttributionError("recovery diagnostics must include points")
    attributed_points = [_attribute_point(point) for point in points]
    summary = dict(diagnostics.get("summary", {}))
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "data_mode": diagnostics.get("data_mode", "revised"),
        "point_count": len(attributed_points),
        "mismatch_count": int(summary.get("mismatch_count", _mismatch_count(points))),
        "points": attributed_points,
        "comparisons": _build_comparisons(attributed_points),
        "refinement_candidates": _refinement_candidates(diagnostics, attributed_points),
        "caveats_zh": [
            "使用修訂後歷史資料，不等同當時投資人可見資料。",
            "此為 experimental diagnostics，不代表正式模型已更新。",
            "recovery watch 不等於正式復甦確認。",
            "policy easing 不得單獨確認 recovery。",
            "不構成投資建議。",
        ],
    }


def write_recovery_attribution(output_path: str | Path, attribution: dict[str, Any]) -> Path:
    """Write recovery attribution JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(attribution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_recovery_attribution_from_file(
    diagnostics_path: str | Path = DEFAULT_DIAGNOSTICS_PATH,
) -> dict[str, Any]:
    """Load diagnostics JSON and build recovery attribution."""

    path = Path(diagnostics_path)
    if not path.exists():
        raise RecoveryAttributionError(
            f"Recovery diagnostics file does not exist: {path}. "
            "Run scripts/run_recovery_diagnostics.py first."
        )
    try:
        diagnostics = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecoveryAttributionError(f"Invalid diagnostics JSON: {path}: {exc}") from exc
    if not isinstance(diagnostics, dict):
        raise RecoveryAttributionError("recovery diagnostics JSON must be an object")
    return build_recovery_attribution(diagnostics)


def _attribute_point(point: dict[str, Any]) -> dict[str, Any]:
    summary = dict(point.get("candidate_summary", {}))
    top_scores = list(point.get("top_positive_indicators", []))
    weak_scores = list(point.get("weak_but_important_indicators", []))
    groups = list(point.get("group_summary", []))
    top_positive = [
        _indicator_summary(score)
        for score in top_scores
        if _num(score.get("score")) >= 65.0 and _num(score.get("confidence")) >= 0.5
    ]
    weak_important = [
        _weak_indicator_summary(score)
        for score in weak_scores
        if str(score.get("indicator_id")) in IMPORTANT_INDICATORS
    ]
    return {
        "scenario_id": point.get("scenario_id"),
        "as_of": point.get("as_of"),
        "label": point.get("label"),
        "recovery_status": point.get("recovery_status"),
        "expected_status": point.get("expected_status"),
        "matches_expected": bool(point.get("matches_expected")),
        "weighted_recovery_score": summary.get("weighted_recovery_score", 0.0),
        "top_positive_indicators": top_positive,
        "weak_but_important_indicators": weak_important,
        "group_contributions": _group_contributions(groups),
        "policy_only_signal": bool(summary.get("policy_only_signal")),
        "labor_confirmed": bool(summary.get("labor_confirmed")),
        "real_activity_confirmed": bool(summary.get("real_activity_confirmed")),
        "credit_financial_confirmed": bool(summary.get("credit_financial_confirmed")),
        "policy_only_or_financial_only_warning": _policy_or_financial_only_warning(summary),
        "diagnostic_notes_zh": _notes(point, summary, top_positive, weak_important),
    }


def _indicator_summary(score: dict[str, Any]) -> dict[str, Any]:
    return {
        "indicator_id": score.get("indicator_id"),
        "display_name_zh": score.get("display_name_zh"),
        "score": score.get("score"),
        "confidence": score.get("confidence"),
        "reason_zh": score.get("reason_zh"),
    }


def _weak_indicator_summary(score: dict[str, Any]) -> dict[str, Any]:
    return {
        "indicator_id": score.get("indicator_id"),
        "group_id": score.get("group_id"),
        "score": score.get("score"),
        "confidence": score.get("confidence"),
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
    return {
        "dotcom_progression": _progression(
            [
                by_label.get("dotcom_recession_early"),
                by_label.get("dotcom_recession_trough_area"),
                by_label.get("dotcom_recovery_initial"),
            ],
            "dotcom 初期到復甦初期的 recovery evidence 偏慢，需檢查 labor reversal 與 real activity bottoming sensitivity。",
        ),
        "gfc_progression": _progression(
            [
                by_label.get("gfc_crisis_peak"),
                by_label.get("gfc_policy_stress_easing_but_labor_not_ready"),
                by_label.get("gfc_trough_area"),
                by_label.get("gfc_recovery_initial"),
            ],
            "GFC 從 crisis peak 到 recovery initial 呈現 weak/watch/watch/strong，表示 candidate layer 對 GFC trough/recovery 有辨識力。",
        ),
        "covid_progression": _progression(
            [
                by_label.get("covid_shock_crash"),
                by_label.get("covid_trough_area"),
                by_label.get("covid_recovery_initial"),
            ],
            "COVID 快速衝擊與反彈需要外生衝擊 caveat；一般 persistence window 可能太慢。",
        ),
        "false_positive_review": _progression(
            [
                by_label.get("euro_debt_non_recession"),
                by_label.get("late_cycle_2018_non_recession"),
            ],
            "euro debt 與 2018 顯示 non-recession 場景仍可能出現 recovery-like easing，需加入 recession-context gate。",
        ),
    }


def _progression(points: list[dict[str, Any] | None], interpretation_zh: str) -> dict[str, Any]:
    valid = [point for point in points if point]
    return {
        "points": [str(point["as_of"]) for point in valid],
        "labels": [str(point["label"]) for point in valid],
        "status_trend": [str(point.get("recovery_status")) for point in valid],
        "score_trend": [_num(point.get("weighted_recovery_score")) for point in valid],
        "top_positive_indicator_trend": [
            [str(item["indicator_id"]) for item in point.get("top_positive_indicators", [])]
            for point in valid
        ],
        "interpretation_zh": interpretation_zh,
    }


def _refinement_candidates(
    diagnostics: dict[str, Any],
    points: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    summary = dict(diagnostics.get("summary", {}))
    requiring_refinement = set(summary.get("indicators_requiring_refinement", []))
    candidate_ids = [
        "financial_stress_easing",
        "initial_jobless_claims_peak_reversal",
        "real_retail_sales_bottoming",
        "industrial_production_bottoming",
        "durable_goods_orders_bottoming",
    ]
    reasons = {
        "financial_stress_easing": "非衰退 slowdown 中金融壓力緩解可能造成 false strong，需搭配 recession context 與 labor/real activity gate。",
        "initial_jobless_claims_peak_reversal": "dotcom/COVID trough miss 顯示 labor peak reversal sensitivity 與 persistence 需重新校準。",
        "real_retail_sales_bottoming": "real activity bottoming 對復甦初期與 non-recession rebound 的辨識需更細緻。",
        "industrial_production_bottoming": "production rebound 應協助 dotcom/GFC 復甦辨識，但需避免一般波動 false positive。",
        "durable_goods_orders_bottoming": "orders bottoming 在復甦初期可能有用，但目前仍需 refinement。",
    }
    for indicator_id in candidate_ids:
        if indicator_id in requiring_refinement or _indicator_is_weak_in_missed_points(indicator_id, points):
            candidates.append(
                {
                    "indicator_id": indicator_id,
                    "reason_zh": reasons[indicator_id],
                    "priority": "high" if indicator_id in {"financial_stress_easing", "initial_jobless_claims_peak_reversal"} else "medium",
                }
            )
    candidates.append(
        {
            "indicator_id": "recession_context_gate",
            "reason_zh": "recovery watch/strong 應要求近期 recession context，避免 euro debt / 2018 類 non-recession false positive。",
            "priority": "high",
        }
    )
    return candidates


def _indicator_is_weak_in_missed_points(indicator_id: str, points: list[dict[str, Any]]) -> bool:
    for point in points:
        if point.get("matches_expected"):
            continue
        if point.get("expected_status") != "watch_or_strong":
            continue
        weak_ids = {str(item.get("indicator_id")) for item in point.get("weak_but_important_indicators", [])}
        if indicator_id in weak_ids:
            return True
    return False


def _policy_or_financial_only_warning(summary: dict[str, Any]) -> bool:
    if summary.get("policy_only_signal"):
        return True
    return bool(summary.get("credit_financial_confirmed")) and not (
        summary.get("labor_confirmed") or summary.get("real_activity_confirmed")
    )


def _notes(
    point: dict[str, Any],
    summary: dict[str, Any],
    top_positive: list[dict[str, Any]],
    weak_important: list[dict[str, Any]],
) -> list[str]:
    notes = ["此 attribution 只解釋 recovery diagnostics，不會修改正式模型判斷。"]
    if not point.get("matches_expected"):
        notes.append("此 point 與 expected status 不一致，應納入 refinement review。")
    if summary.get("policy_only_signal"):
        notes.append("policy easing 不得單獨確認 recovery。")
    if _policy_or_financial_only_warning(summary):
        notes.append("policy / financial easing 需搭配 labor 或 real activity confirmation。")
    if point.get("label") in {"euro_debt_non_recession", "late_cycle_2018_non_recession"}:
        notes.append("non-recession 場景需要 recession-context gate，避免把風險緩和誤判為 recovery。")
    if "covid" in str(point.get("label")):
        notes.append("COVID 屬外生衝擊，快速反彈不等同一般景氣循環復甦。")
    if top_positive:
        notes.append("本期有高分候選指標，需檢查是否來自多群組而非單一 support signal。")
    if weak_important:
        notes.append("部分重要候選指標偏弱，可能造成 missed recovery watch。")
    return notes


def _mismatch_count(points: list[dict[str, Any]]) -> int:
    return sum(1 for point in points if not point.get("matches_expected"))


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

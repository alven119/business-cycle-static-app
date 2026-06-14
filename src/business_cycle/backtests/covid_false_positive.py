"""Build diagnostics for COVID early false-positive recession detection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAVEATS_ZH = [
    "使用修訂後歷史資料，不等同當時投資人可見資料。",
    "此為模型校準診斷，不代表正式模型已更新。",
    "不構成投資建議。",
]

DIAGNOSTIC_HYPOTHESES_ZH = [
    "檢查是否由少數指標推動，避免單一短期訊號造成 confirmed recession。",
    "檢查是否需要 breadth_confirmation，要求多個指標群組同步支持衰退判讀。",
    "檢查是否需要更嚴格的 recession-specific confirmation period 或門檻。",
    "檢查是否需要針對 COVID 類外生衝擊建立獨立處理方式，而不是把 2019 訊號過早解讀為衰退。",
    "檢查是否需補齊書中衰退確認指標，以降低 MVP 指標集合造成的誤判。",
]


class CovidFalsePositiveError(ValueError):
    """Raised when COVID false-positive diagnostic inputs are invalid."""


def build_covid_false_positive_diagnostic(
    *,
    experiment_id: str,
    scenario_id: str,
    calibration_summary: dict[str, Any],
    acceptance_review: dict[str, Any],
    timeline: dict[str, Any],
    transition_attribution: dict[str, Any],
) -> dict[str, Any]:
    """Build a COVID early false-positive diagnostic from calibration outputs."""

    scenario_review = _scenario_by_id(acceptance_review.get("scenarios"), scenario_id)
    scenario_summary = _scenario_by_id(calibration_summary.get("scenarios"), scenario_id)
    experiment_summary = scenario_summary.get("experiment") if isinstance(scenario_summary.get("experiment"), dict) else {}
    first_recession = (
        scenario_review.get("first_recession_current_as_of")
        or experiment_summary.get("first_recession_current_as_of")
    )
    diagnostic = _diagnostic_for_as_of(transition_attribution, first_recession)
    period = _period_for_as_of(timeline, first_recession)
    top_indicator_changes = _list(diagnostic.get("top_indicator_score_changes"))[:5]
    return {
        "experiment_id": experiment_id,
        "scenario_id": scenario_id,
        "display_name_zh": timeline.get("display_name_zh") or scenario_review.get("display_name_zh"),
        "data_mode": timeline.get("data_mode") or calibration_summary.get("data_mode"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "first_recession_current_as_of": first_recession,
        "early_false_recession": bool(scenario_review.get("early_false_recession")),
        "recession_timing_status": scenario_review.get("recession_timing_status"),
        "acceptance_status": scenario_review.get("acceptance_status"),
        "phase_score_changes": _list(diagnostic.get("phase_score_changes")),
        "top_indicator_score_changes": top_indicator_changes,
        "top_candidate_phase_evidence": _list(diagnostic.get("top_candidate_phase_evidence")),
        "transition_controls_applied": _list_str(period.get("transition_controls_applied")),
        "transition_controls_blocked": _list_str(period.get("transition_controls_blocked")),
        "transition_controls_warnings": _list_str(period.get("transition_controls_warnings")),
        "diagnostic_hypotheses_zh": DIAGNOSTIC_HYPOTHESES_ZH,
        "attribution_quality": diagnostic.get("attribution_quality") or "limited",
        "caveats_zh": _caveats(calibration_summary, acceptance_review, timeline, transition_attribution),
        "warnings": _warnings(first_recession, diagnostic, period),
    }


def write_covid_false_positive_diagnostic(
    *,
    experiment_id: str,
    experiment_root: str | Path = Path("data/backtests/calibration"),
    scenario_id: str = "covid_recession",
    output_path: str | Path | None = None,
) -> Path:
    """Load full-horizon outputs and write COVID false-positive diagnostic JSON."""

    root = Path(experiment_root) / experiment_id
    summary_path = root / "calibration_summary.json"
    review_path = root / "calibration_acceptance_review.json"
    scenario_dir = root / "experiment" / scenario_id
    timeline_path = scenario_dir / "timeline.json"
    attribution_path = scenario_dir / "transition_attribution.json"
    missing = [path for path in (summary_path, review_path, timeline_path, attribution_path) if not path.exists()]
    if missing:
        missing_text = ", ".join(str(path) for path in missing)
        raise CovidFalsePositiveError(
            f"missing COVID false-positive diagnostic input(s): {missing_text}"
        )

    payload = build_covid_false_positive_diagnostic(
        experiment_id=experiment_id,
        scenario_id=scenario_id,
        calibration_summary=_load_json_mapping(summary_path),
        acceptance_review=_load_json_mapping(review_path),
        timeline=_load_json_mapping(timeline_path),
        transition_attribution=_load_json_mapping(attribution_path),
    )
    output = Path(output_path) if output_path is not None else root / "covid_false_positive_diagnostic.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def _scenario_by_id(value: Any, scenario_id: str) -> dict[str, Any]:
    for item in _list(value):
        if str(item.get("scenario_id")) == scenario_id:
            return item
    return {}


def _diagnostic_for_as_of(payload: dict[str, Any], as_of: Any) -> dict[str, Any]:
    if as_of is None:
        return {}
    for diagnostic in _list(payload.get("diagnostics")):
        if str(diagnostic.get("as_of")) == str(as_of):
            return diagnostic
    return {}


def _period_for_as_of(payload: dict[str, Any], as_of: Any) -> dict[str, Any]:
    if as_of is None:
        return {}
    for period in _list(payload.get("periods")):
        if str(period.get("as_of")) == str(as_of):
            return period
    return {}


def _caveats(*payloads: dict[str, Any]) -> list[str]:
    for payload in payloads:
        caveats = payload.get("caveats_zh")
        if isinstance(caveats, list) and caveats:
            values = [str(item) for item in caveats]
            if not any("不構成投資建議" in item for item in values):
                values.append("不構成投資建議。")
            return values
    return CAVEATS_ZH


def _warnings(first_recession: Any, diagnostic: dict[str, Any], period: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if first_recession is None:
        warnings.append("experiment output does not include first_recession_current_as_of")
    if not diagnostic:
        warnings.append("transition attribution does not include a diagnostic at first_recession_current_as_of")
    if not period:
        warnings.append("timeline does not include a period at first_recession_current_as_of")
    return warnings


def _load_json_mapping(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CovidFalsePositiveError(f"JSON input must be a mapping: {json_path}")
    return payload


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _list_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]

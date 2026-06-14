"""Build transition attribution diagnostics from backtest outputs."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAVEATS_ZH = [
    "使用修訂後歷史資料。",
    "不等同當時投資人可見資料。",
    "不構成投資建議。",
]


def build_transition_attribution(
    *,
    timeline_path: str | Path,
    report_path: str | Path,
    intermediate_dir: str | Path,
) -> dict[str, Any]:
    """Build attribution diagnostics for transitions and plausibility warnings."""

    timeline = _load_json_mapping(timeline_path)
    report = _load_json_mapping(report_path)
    periods = _list(timeline.get("periods"))
    periods_by_as_of = {str(period.get("as_of")): period for period in periods}
    period_order = [str(period.get("as_of")) for period in periods]
    warnings: list[str] = []
    transition_events = _list(report.get("transition_events"))
    plausibility_warnings = _list(report.get("plausibility_warnings"))
    warning_links_by_as_of = _warnings_by_as_of(plausibility_warnings)

    diagnostics: list[dict[str, Any]] = []
    transition_as_ofs: set[str] = set()
    for event in transition_events:
        as_of = str(event.get("as_of"))
        transition_as_ofs.add(as_of)
        diagnostics.append(
            _build_diagnostic(
                event_type="transition_event",
                as_of=as_of,
                previous_as_of=_previous_as_of(period_order, as_of),
                event=event,
                periods_by_as_of=periods_by_as_of,
                intermediate_dir=Path(intermediate_dir),
                linked_warnings=warning_links_by_as_of.get(as_of, []),
                warnings=warnings,
            )
        )

    for warning in plausibility_warnings:
        as_of = str(warning.get("as_of"))
        if as_of in transition_as_ofs:
            continue
        diagnostics.append(
            _build_diagnostic(
                event_type="plausibility_warning",
                as_of=as_of,
                previous_as_of=_previous_as_of(period_order, as_of),
                event=_event_from_warning(warning, periods_by_as_of.get(as_of)),
                periods_by_as_of=periods_by_as_of,
                intermediate_dir=Path(intermediate_dir),
                linked_warnings=[warning],
                warnings=warnings,
            )
        )

    return {
        "scenario_id": str(timeline.get("scenario_id") or report.get("scenario_id") or ""),
        "display_name_zh": str(timeline.get("display_name_zh") or report.get("display_name_zh") or ""),
        "data_mode": str(timeline.get("data_mode") or report.get("data_mode") or ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "transition_count": len(transition_events),
        "diagnostics": diagnostics,
        "plausibility_warnings_linked": _linked_warning_summaries(plausibility_warnings, transition_as_ofs),
        "caveats_zh": _caveats(timeline, report),
        "warnings": sorted(set(warnings)),
    }


def write_transition_attribution(
    *,
    timeline_path: str | Path,
    report_path: str | Path,
    intermediate_dir: str | Path,
    output_path: str | Path,
) -> Path:
    """Build and write transition attribution JSON."""

    output = Path(output_path)
    payload = build_transition_attribution(
        timeline_path=timeline_path,
        report_path=report_path,
        intermediate_dir=intermediate_dir,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def attribution_quality_counts(payload: dict[str, Any]) -> dict[str, int]:
    """Return counts by attribution quality for CLI summaries."""

    counts = Counter(
        str(diagnostic.get("attribution_quality") or "unknown")
        for diagnostic in _list(payload.get("diagnostics"))
    )
    return dict(sorted(counts.items()))


def _build_diagnostic(
    *,
    event_type: str,
    as_of: str,
    previous_as_of: str | None,
    event: dict[str, Any],
    periods_by_as_of: dict[str, dict[str, Any]],
    intermediate_dir: Path,
    linked_warnings: list[dict[str, Any]],
    warnings: list[str],
) -> dict[str, Any]:
    current_period = periods_by_as_of.get(as_of, {})
    previous_period = periods_by_as_of.get(previous_as_of or "", {})
    phase_score_changes = _phase_score_changes(previous_period, current_period)
    if previous_as_of is None:
        warnings.append(f"missing previous period for attribution at {as_of}")

    previous_indicator_scores = _load_indicator_scores(intermediate_dir, previous_as_of, warnings)
    current_indicator_scores = _load_indicator_scores(intermediate_dir, as_of, warnings)
    indicator_score_changes = _indicator_score_changes(previous_indicator_scores, current_indicator_scores)

    current_phase_scores = _load_phase_scores(intermediate_dir, as_of, warnings)
    candidate_phase_id = _optional_str(event.get("candidate_phase_id"))
    to_phase_id = _optional_str(event.get("to_phase_id"))
    current_phase_id = _optional_str(current_period.get("current_phase_id") or to_phase_id)
    candidate_evidence = _phase_evidence(current_phase_scores, candidate_phase_id, warnings)
    current_evidence = _phase_evidence(current_phase_scores, current_phase_id, warnings)

    diagnostic_warnings = [_warning_summary(warning) for warning in linked_warnings]
    return {
        "as_of": as_of,
        "previous_as_of": previous_as_of,
        "event_type": event_type,
        "from_phase_id": event.get("from_phase_id"),
        "to_phase_id": event.get("to_phase_id"),
        "decision_status": event.get("decision_status") or current_period.get("decision_status"),
        "candidate_phase_id": candidate_phase_id,
        "confidence": float(event.get("confidence") or current_period.get("confidence") or 0.0),
        "phase_score_changes": phase_score_changes,
        "top_candidate_phase_evidence": candidate_evidence,
        "top_current_phase_evidence": current_evidence,
        "top_indicator_score_changes": indicator_score_changes,
        "plausibility_warnings": diagnostic_warnings,
        "diagnostic_notes_zh": _diagnostic_notes(phase_score_changes, event_type),
        "attribution_quality": _attribution_quality(
            previous_as_of=previous_as_of,
            phase_score_changes=phase_score_changes,
            indicator_score_changes=indicator_score_changes,
            candidate_evidence=candidate_evidence,
            current_evidence=current_evidence,
        ),
    }


def _phase_score_changes(
    previous_period: dict[str, Any],
    current_period: dict[str, Any],
) -> list[dict[str, Any]]:
    previous_scores = _phase_scores_by_id(previous_period.get("phase_scores"))
    current_scores = _phase_scores_by_id(current_period.get("phase_scores"))
    changes: list[dict[str, Any]] = []
    for phase_id in sorted(previous_scores.keys() | current_scores.keys()):
        previous_score = previous_scores.get(phase_id)
        current_score = current_scores.get(phase_id)
        if previous_score is None or current_score is None:
            continue
        delta = current_score - previous_score
        changes.append(
            {
                "phase_id": phase_id,
                "previous_score": previous_score,
                "current_score": current_score,
                "delta": delta,
            }
        )
    return sorted(changes, key=lambda item: abs(float(item["delta"])), reverse=True)


def _indicator_score_changes(
    previous_scores: dict[str, dict[str, Any]],
    current_scores: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for indicator_id in sorted(previous_scores.keys() & current_scores.keys()):
        previous = previous_scores[indicator_id]
        current = current_scores[indicator_id]
        previous_score = _float_or_none(previous.get("score"))
        current_score = _float_or_none(current.get("score"))
        if previous_score is None or current_score is None:
            continue
        changes.append(
            {
                "indicator_id": indicator_id,
                "previous_score": previous_score,
                "current_score": current_score,
                "delta": current_score - previous_score,
                "confidence": _float_or_none(current.get("confidence")),
                "reason_zh": current.get("reason_zh") or current.get("reason"),
            }
        )
    return sorted(changes, key=lambda item: abs(float(item["delta"])), reverse=True)[:5]


def _phase_evidence(
    phase_scores: dict[str, dict[str, Any]],
    phase_id: str | None,
    warnings: list[str],
) -> list[dict[str, Any]]:
    if phase_id is None:
        return []
    phase = phase_scores.get(phase_id)
    if not phase:
        warnings.append(f"phase score intermediate output missing phase_id={phase_id}")
        return []
    contributions = phase.get("contributing_indicators")
    if not isinstance(contributions, list) or not contributions:
        warnings.append("phase score intermediate output does not include per-indicator contribution details")
        return []
    evidence = [
        {
            "indicator_id": str(item.get("indicator_id")),
            "phase_signal_score": _float_or_none(item.get("phase_signal_score")),
            "confidence": _float_or_none(item.get("confidence")),
            "weight": _float_or_none(item.get("weight")),
            "weighted_contribution": _float_or_none(item.get("weighted_contribution")),
            "role": item.get("role"),
            "signal_transform": item.get("signal_transform"),
        }
        for item in contributions
        if isinstance(item, dict) and item.get("indicator_id") is not None
    ]
    return sorted(
        evidence,
        key=lambda item: abs(float(item.get("weighted_contribution") or 0.0)),
        reverse=True,
    )[:5]


def _load_indicator_scores(
    intermediate_dir: Path,
    as_of: str | None,
    warnings: list[str],
) -> dict[str, dict[str, Any]]:
    if as_of is None:
        return {}
    path = intermediate_dir / as_of / "indicator_scores.json"
    payload = _try_load_json_mapping(path, warnings)
    return {
        str(item["indicator_id"]): item
        for item in _list(payload.get("results"))
        if item.get("indicator_id") is not None
    }


def _load_phase_scores(
    intermediate_dir: Path,
    as_of: str,
    warnings: list[str],
) -> dict[str, dict[str, Any]]:
    path = intermediate_dir / as_of / "phase_scores.json"
    payload = _try_load_json_mapping(path, warnings)
    return {
        str(item["phase_id"]): item
        for item in _list(payload.get("results"))
        if item.get("phase_id") is not None
    }


def _try_load_json_mapping(path: Path, warnings: list[str]) -> dict[str, Any]:
    if not path.exists():
        warnings.append(f"missing intermediate output: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"invalid intermediate JSON: {path}: {exc}")
        return {}
    if not isinstance(payload, dict):
        warnings.append(f"intermediate JSON is not a mapping: {path}")
        return {}
    return payload


def _event_from_warning(
    warning: dict[str, Any],
    period: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "from_phase_id": None,
        "to_phase_id": warning.get("phase_id"),
        "decision_status": period.get("decision_status") if isinstance(period, dict) else None,
        "candidate_phase_id": period.get("candidate_phase_id") if isinstance(period, dict) else warning.get("phase_id"),
        "confidence": period.get("confidence") if isinstance(period, dict) else 0.0,
    }


def _previous_as_of(period_order: list[str], as_of: str) -> str | None:
    try:
        index = period_order.index(as_of)
    except ValueError:
        return None
    if index == 0:
        return None
    return period_order[index - 1]


def _phase_scores_by_id(value: Any) -> dict[str, float]:
    scores: dict[str, float] = {}
    for item in _list(value):
        phase_id = item.get("phase_id")
        score = _float_or_none(item.get("score"))
        if phase_id is not None and score is not None:
            scores[str(phase_id)] = score
    return scores


def _diagnostic_notes(phase_score_changes: list[dict[str, Any]], event_type: str) -> list[str]:
    notes = ["此診斷只解釋回測結果，不會修改模型判斷。"]
    if phase_score_changes:
        largest = phase_score_changes[0]
        notes.insert(
            0,
            (
                f"{_phase_label_zh(str(largest['phase_id']))}分數在本期變化 "
                f"{float(largest['delta']):+.1f}，需檢查是否由單一指標或短期資料波動造成。"
            ),
        )
    if event_type == "plausibility_warning":
        notes.append("此筆為 plausibility warning attribution，可能沒有實際 current phase transition。")
    return notes


def _attribution_quality(
    *,
    previous_as_of: str | None,
    phase_score_changes: list[dict[str, Any]],
    indicator_score_changes: list[dict[str, Any]],
    candidate_evidence: list[dict[str, Any]],
    current_evidence: list[dict[str, Any]],
) -> str:
    if previous_as_of is None:
        return "limited"
    has_phase = bool(phase_score_changes)
    has_indicator = bool(indicator_score_changes)
    has_evidence = bool(candidate_evidence or current_evidence)
    if has_phase and has_indicator and has_evidence:
        return "full"
    if has_phase or has_indicator:
        return "partial"
    return "limited"


def _warnings_by_as_of(warnings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for warning in warnings:
        as_of = warning.get("as_of")
        if as_of is not None:
            grouped.setdefault(str(as_of), []).append(warning)
    return grouped


def _linked_warning_summaries(
    warnings: list[dict[str, Any]],
    transition_as_ofs: set[str],
) -> list[dict[str, Any]]:
    return [
        _warning_summary(warning)
        for warning in warnings
        if str(warning.get("as_of")) in transition_as_ofs
    ]


def _warning_summary(warning: dict[str, Any]) -> dict[str, Any]:
    return {
        "as_of": warning.get("as_of"),
        "kind": warning.get("kind"),
        "phase_id": warning.get("phase_id"),
    }


def _caveats(timeline: dict[str, Any], report: dict[str, Any]) -> list[str]:
    for payload in (timeline, report):
        caveats = payload.get("caveats_zh")
        if isinstance(caveats, list) and caveats:
            return [str(item) for item in caveats]
    return CAVEATS_ZH


def _load_json_mapping(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"Backtest attribution input does not exist: {json_path}")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Backtest attribution input must be a mapping: {json_path}")
    return payload


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _optional_str(value: Any) -> str | None:
    return None if value is None else str(value)


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _phase_label_zh(phase_id: str) -> str:
    labels = {
        "recovery": "復甦期",
        "growth": "成長期",
        "boom": "榮景期",
        "recession": "衰退期",
    }
    return labels.get(phase_id, phase_id)

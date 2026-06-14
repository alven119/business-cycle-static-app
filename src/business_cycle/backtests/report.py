"""Build diagnostics reports from backtest timeline JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CAVEATS_ZH = [
    "使用修訂後歷史資料。",
    "不等同當時投資人可見資料。",
    "不構成投資建議。",
]


@dataclass(frozen=True)
class PhaseSegment:
    """Continuous run of the same current phase."""

    phase_id: str | None
    start_as_of: str
    end_as_of: str
    period_count: int


@dataclass(frozen=True)
class TransitionEvent:
    """A current-phase change between adjacent periods."""

    as_of: str
    from_phase_id: str | None
    to_phase_id: str | None
    decision_status: str
    confidence: float
    candidate_phase_id: str | None
    reason_zh: str | None = None


@dataclass(frozen=True)
class PhaseScoreExtrema:
    """Score extrema for one phase over the timeline."""

    phase_id: str
    max_score: float
    max_score_as_of: str
    min_score: float
    min_score_as_of: str
    latest_score: float
    latest_confidence: float


@dataclass(frozen=True)
class BacktestPlausibilityConfig:
    """Thresholds for report-only plausibility diagnostics."""

    min_segment_periods: int = 3
    early_window_ratio: float = 0.2


@dataclass(frozen=True)
class PlausibilityWarning:
    """Report-only warning for suspicious backtest behavior."""

    kind: str
    as_of: str
    phase_id: str | None
    message_zh: str


@dataclass(frozen=True)
class BacktestDiagnosticsReport:
    """Diagnostics report derived from one backtest timeline."""

    scenario_id: str
    display_name_zh: str
    data_mode: str
    window_start: str
    window_end: str
    generated_at: str
    period_count: int
    phase_segments: list[PhaseSegment]
    transition_events: list[TransitionEvent]
    decision_status_counts: dict[str, int]
    phase_score_extrema: list[PhaseScoreExtrema]
    first_transition_watch_as_of: str | None
    first_confirmed_transition_as_of: str | None
    first_recession_watch_as_of: str | None
    first_recession_current_as_of: str | None
    failure_count: int
    warning_count: int
    periods_with_failures: list[dict[str, Any]]
    periods_with_warnings: list[dict[str, Any]]
    plausibility_warning_count: int
    plausibility_warnings: list[PlausibilityWarning]
    caveats_zh: list[str]
    warnings: list[str]


def build_backtest_report(
    timeline: dict[str, Any],
    plausibility_config: BacktestPlausibilityConfig | None = None,
) -> BacktestDiagnosticsReport:
    """Build a diagnostics report from a timeline mapping."""

    config = plausibility_config or BacktestPlausibilityConfig()
    periods = _periods(timeline)
    warnings: list[str] = []
    phase_segments = _phase_segments(periods)
    transition_events = _transition_events(periods)
    decision_status_counts = _decision_status_counts(periods)
    phase_score_extrema = _phase_score_extrema(periods, warnings)
    periods_with_failures = _periods_with_count(periods, "failures")
    periods_with_warnings = _periods_with_count(periods, "warnings")
    failure_count = sum(item["count"] for item in periods_with_failures)
    warning_count = sum(item["count"] for item in periods_with_warnings) + len(warnings)
    plausibility_warnings = _plausibility_warnings(
        periods=periods,
        phase_segments=phase_segments,
        transition_events=transition_events,
        first_recession_watch_as_of=_first_recession_watch(periods),
        first_recession_current_as_of=_first_current_phase(periods, "recession"),
        config=config,
    )

    return BacktestDiagnosticsReport(
        scenario_id=str(timeline.get("scenario_id") or ""),
        display_name_zh=str(timeline.get("display_name_zh") or ""),
        data_mode=str(timeline.get("data_mode") or ""),
        window_start=str(timeline.get("window_start") or ""),
        window_end=str(timeline.get("window_end") or ""),
        generated_at=datetime.now(timezone.utc).isoformat(),
        period_count=len(periods),
        phase_segments=phase_segments,
        transition_events=transition_events,
        decision_status_counts=decision_status_counts,
        phase_score_extrema=phase_score_extrema,
        first_transition_watch_as_of=_first_status(periods, "transition_watch"),
        first_confirmed_transition_as_of=_first_status(periods, "confirmed"),
        first_recession_watch_as_of=_first_recession_watch(periods),
        first_recession_current_as_of=_first_current_phase(periods, "recession"),
        failure_count=failure_count,
        warning_count=warning_count,
        periods_with_failures=periods_with_failures,
        periods_with_warnings=periods_with_warnings,
        plausibility_warning_count=len(plausibility_warnings),
        plausibility_warnings=plausibility_warnings,
        caveats_zh=_caveats(timeline),
        warnings=warnings,
    )


def write_backtest_report(timeline_path: str | Path, output_path: str | Path) -> Path:
    """Build and write a report JSON from a timeline JSON path."""

    path = Path(timeline_path)
    if not path.exists():
        raise FileNotFoundError(f"Backtest timeline JSON does not exist: {path}")
    timeline = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(timeline, dict):
        raise ValueError("Backtest timeline JSON must be a mapping")

    report = build_backtest_report(timeline)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(serialize_backtest_report(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output


def serialize_backtest_report(report: BacktestDiagnosticsReport) -> dict[str, Any]:
    """Convert a diagnostics report to a JSON-safe mapping."""

    return {
        "scenario_id": report.scenario_id,
        "display_name_zh": report.display_name_zh,
        "data_mode": report.data_mode,
        "window_start": report.window_start,
        "window_end": report.window_end,
        "generated_at": report.generated_at,
        "period_count": report.period_count,
        "phase_segments": [segment.__dict__ for segment in report.phase_segments],
        "transition_events": [event.__dict__ for event in report.transition_events],
        "decision_status_counts": report.decision_status_counts,
        "phase_score_extrema": [extrema.__dict__ for extrema in report.phase_score_extrema],
        "first_transition_watch_as_of": report.first_transition_watch_as_of,
        "first_confirmed_transition_as_of": report.first_confirmed_transition_as_of,
        "first_recession_watch_as_of": report.first_recession_watch_as_of,
        "first_recession_current_as_of": report.first_recession_current_as_of,
        "failure_count": report.failure_count,
        "warning_count": report.warning_count,
        "periods_with_failures": report.periods_with_failures,
        "periods_with_warnings": report.periods_with_warnings,
        "plausibility_warning_count": report.plausibility_warning_count,
        "plausibility_warnings": [warning.__dict__ for warning in report.plausibility_warnings],
        "caveats_zh": report.caveats_zh,
        "warnings": report.warnings,
    }


def _periods(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    periods = timeline.get("periods")
    if not isinstance(periods, list) or not periods:
        raise ValueError("Backtest timeline must contain non-empty periods")
    valid_periods = [period for period in periods if isinstance(period, dict)]
    if not valid_periods:
        raise ValueError("Backtest timeline must contain non-empty periods")
    return valid_periods


def _caveats(timeline: dict[str, Any]) -> list[str]:
    caveats = timeline.get("caveats_zh")
    if not isinstance(caveats, list) or not caveats:
        return DEFAULT_CAVEATS_ZH
    return [str(item) for item in caveats]


def _phase_segments(periods: list[dict[str, Any]]) -> list[PhaseSegment]:
    segments: list[PhaseSegment] = []
    current_phase = _optional_str(periods[0].get("current_phase_id"))
    start_as_of = str(periods[0].get("as_of"))
    end_as_of = start_as_of
    count = 0
    for period in periods:
        phase_id = _optional_str(period.get("current_phase_id"))
        as_of = str(period.get("as_of"))
        if phase_id != current_phase and count > 0:
            segments.append(
                PhaseSegment(
                    phase_id=current_phase,
                    start_as_of=start_as_of,
                    end_as_of=end_as_of,
                    period_count=count,
                )
            )
            current_phase = phase_id
            start_as_of = as_of
            count = 0
        end_as_of = as_of
        count += 1
    segments.append(
        PhaseSegment(
            phase_id=current_phase,
            start_as_of=start_as_of,
            end_as_of=end_as_of,
            period_count=count,
        )
    )
    return segments


def _transition_events(periods: list[dict[str, Any]]) -> list[TransitionEvent]:
    events: list[TransitionEvent] = []
    previous_phase = _optional_str(periods[0].get("current_phase_id"))
    for period in periods[1:]:
        current_phase = _optional_str(period.get("current_phase_id"))
        if current_phase != previous_phase:
            events.append(
                TransitionEvent(
                    as_of=str(period.get("as_of")),
                    from_phase_id=previous_phase,
                    to_phase_id=current_phase,
                    decision_status=str(period.get("decision_status") or "unknown"),
                    confidence=float(period.get("confidence") or 0.0),
                    candidate_phase_id=_optional_str(period.get("candidate_phase_id")),
                    reason_zh=_optional_str(period.get("reason_zh")),
                )
            )
        previous_phase = current_phase
    return events


def _decision_status_counts(periods: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for period in periods:
        status = str(period.get("decision_status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _phase_score_extrema(
    periods: list[dict[str, Any]],
    warnings: list[str],
) -> list[PhaseScoreExtrema]:
    by_phase: dict[str, list[dict[str, Any]]] = {}
    for period in periods:
        as_of = str(period.get("as_of"))
        phase_scores = period.get("phase_scores")
        if not isinstance(phase_scores, list) or not phase_scores:
            warnings.append(f"period {as_of} missing phase_scores")
            continue
        for score in phase_scores:
            if not isinstance(score, dict) or score.get("phase_id") is None:
                continue
            phase_id = str(score["phase_id"])
            by_phase.setdefault(phase_id, []).append({"as_of": as_of, **score})

    extrema: list[PhaseScoreExtrema] = []
    for phase_id in sorted(by_phase):
        entries = by_phase[phase_id]
        max_entry = max(entries, key=lambda item: float(item.get("score") or 0.0))
        min_entry = min(entries, key=lambda item: float(item.get("score") or 0.0))
        latest_entry = entries[-1]
        extrema.append(
            PhaseScoreExtrema(
                phase_id=phase_id,
                max_score=float(max_entry.get("score") or 0.0),
                max_score_as_of=str(max_entry["as_of"]),
                min_score=float(min_entry.get("score") or 0.0),
                min_score_as_of=str(min_entry["as_of"]),
                latest_score=float(latest_entry.get("score") or 0.0),
                latest_confidence=float(latest_entry.get("confidence") or 0.0),
            )
        )
    return extrema


def _first_status(periods: list[dict[str, Any]], status: str) -> str | None:
    for period in periods:
        if period.get("decision_status") == status:
            return str(period.get("as_of"))
    return None


def _first_recession_watch(periods: list[dict[str, Any]]) -> str | None:
    for period in periods:
        if period.get("candidate_phase_id") == "recession" and period.get("decision_status") in {
            "transition_watch",
            "confirmed",
        }:
            return str(period.get("as_of"))
    return None


def _first_current_phase(periods: list[dict[str, Any]], phase_id: str) -> str | None:
    for period in periods:
        if period.get("current_phase_id") == phase_id:
            return str(period.get("as_of"))
    return None


def _periods_with_count(periods: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for period in periods:
        values = period.get(field)
        count = len(values) if isinstance(values, list) else 0
        if count > 0:
            items.append({"as_of": str(period.get("as_of")), "count": count})
    return items


def _plausibility_warnings(
    *,
    periods: list[dict[str, Any]],
    phase_segments: list[PhaseSegment],
    transition_events: list[TransitionEvent],
    first_recession_watch_as_of: str | None,
    first_recession_current_as_of: str | None,
    config: BacktestPlausibilityConfig,
) -> list[PlausibilityWarning]:
    warnings: list[PlausibilityWarning] = []
    warnings.extend(_short_phase_segment_warnings(phase_segments, config))
    warnings.extend(_direct_confirmed_transition_warnings(periods, transition_events))
    warnings.extend(_rapid_round_trip_warnings(phase_segments, config))
    warning = _early_transition_warning(periods, transition_events, config)
    if warning is not None:
        warnings.append(warning)
    warning = _recession_without_watch_warning(
        first_recession_watch_as_of,
        first_recession_current_as_of,
    )
    if warning is not None:
        warnings.append(warning)
    return warnings


def _short_phase_segment_warnings(
    phase_segments: list[PhaseSegment],
    config: BacktestPlausibilityConfig,
) -> list[PlausibilityWarning]:
    warnings: list[PlausibilityWarning] = []
    for segment in phase_segments:
        if segment.period_count < config.min_segment_periods:
            warnings.append(
                PlausibilityWarning(
                    kind="short_phase_segment",
                    as_of=segment.start_as_of,
                    phase_id=segment.phase_id,
                    message_zh=(
                        f"{_phase_label_zh(segment.phase_id)}分段僅持續 {segment.period_count} 期，"
                        "可能代表模型對短期訊號過度敏感；此為診斷警示，不會修改回測結果。"
                    ),
                )
            )
    return warnings


def _direct_confirmed_transition_warnings(
    periods: list[dict[str, Any]],
    transition_events: list[TransitionEvent],
) -> list[PlausibilityWarning]:
    periods_by_as_of = {str(period.get("as_of")): index for index, period in enumerate(periods)}
    warnings: list[PlausibilityWarning] = []
    for event in transition_events:
        if event.decision_status != "confirmed":
            continue
        index = periods_by_as_of.get(event.as_of)
        previous_status = None if index is None or index == 0 else periods[index - 1].get("decision_status")
        if previous_status != "transition_watch":
            warnings.append(
                PlausibilityWarning(
                    kind="direct_confirmed_transition_without_watch",
                    as_of=event.as_of,
                    phase_id=event.to_phase_id,
                    message_zh=(
                        f"{event.as_of} 從{_phase_label_zh(event.from_phase_id)}直接確認轉換到"
                        f"{_phase_label_zh(event.to_phase_id)}，前一期未先進入轉換觀察；"
                        "此為診斷警示，需檢查轉換門檻或訊號敏感度。"
                    ),
                )
            )
    return warnings


def _rapid_round_trip_warnings(
    phase_segments: list[PhaseSegment],
    config: BacktestPlausibilityConfig,
) -> list[PlausibilityWarning]:
    warnings: list[PlausibilityWarning] = []
    for index in range(1, len(phase_segments) - 1):
        middle = phase_segments[index]
        if middle.period_count < config.min_segment_periods:
            previous = phase_segments[index - 1]
            next_segment = phase_segments[index + 1]
            warnings.append(
                PlausibilityWarning(
                    kind="rapid_round_trip",
                    as_of=middle.start_as_of,
                    phase_id=middle.phase_id,
                    message_zh=(
                        f"短時間內出現{_phase_label_zh(previous.phase_id)} -> "
                        f"{_phase_label_zh(middle.phase_id)} -> {_phase_label_zh(next_segment.phase_id)}，"
                        f"其中{_phase_label_zh(middle.phase_id)}僅持續 {middle.period_count} 期，"
                        "可能代表 whipsaw；此為診斷警示，不會修改結果。"
                    ),
                )
            )
    return warnings


def _early_transition_warning(
    periods: list[dict[str, Any]],
    transition_events: list[TransitionEvent],
    config: BacktestPlausibilityConfig,
) -> PlausibilityWarning | None:
    if not transition_events:
        return None
    first_event = transition_events[0]
    event_index = next(
        (index for index, period in enumerate(periods) if period.get("as_of") == first_event.as_of),
        None,
    )
    if event_index is None:
        return None
    early_periods = max(1, int(len(periods) * config.early_window_ratio))
    if event_index <= early_periods:
        return PlausibilityWarning(
            kind="early_scenario_transition",
            as_of=first_event.as_of,
            phase_id=first_event.to_phase_id,
            message_zh=(
                f"第一個階段轉換發生在 scenario 前 {config.early_window_ratio:.0%} 期間內，"
                "可能代表模型過早確認轉折；此為診斷警示。"
            ),
        )
    return None


def _recession_without_watch_warning(
    first_recession_watch_as_of: str | None,
    first_recession_current_as_of: str | None,
) -> PlausibilityWarning | None:
    if first_recession_current_as_of is None:
        return None
    if first_recession_watch_as_of == first_recession_current_as_of:
        return PlausibilityWarning(
            kind="recession_without_watch",
            as_of=first_recession_current_as_of,
            phase_id="recession",
            message_zh=(
                "衰退期在同一期直接被確認，缺少觀察期，需檢查 phase thresholds、"
                "scoring sensitivity 或 confirmation periods；此為診斷警示。"
            ),
        )
    return None


def _phase_label_zh(phase_id: str | None) -> str:
    labels = {
        "recovery": "復甦期",
        "growth": "成長期",
        "boom": "榮景期",
        "recession": "衰退期",
    }
    if phase_id is None:
        return "未判定"
    return labels.get(phase_id, phase_id)


def _optional_str(value: Any) -> str | None:
    return None if value is None else str(value)

"""As-of selection for official Census release events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol


class ReleaseEvent(Protocol):
    event_id: str
    series_id: str
    release_datetime: str
    availability_date: str
    reference_month: str
    estimate_stage: str
    value: float
    source_artifact_id: str
    source_checksum: str
    parser_version: str


@dataclass(frozen=True)
class CensusAsOfSelection:
    series_id: str
    as_of: str
    selected_event_id: str | None
    selected_estimate_stage: str | None
    selected_reference_month: str | None
    selected_release_datetime: str | None
    value: float | None
    superseded_event_ids: tuple[str, ...]
    benchmark_revision_applied: bool
    future_event_blocked_count: int
    source_artifact_id: str | None
    source_checksum: str | None
    parser_version: str | None
    point_in_time: bool
    missing_reason: str | None = None


def select_latest_census_event_as_of(
    events: Iterable[ReleaseEvent],
    *,
    series_id: str,
    as_of: str,
    reference_month: str | None = None,
) -> CensusAsOfSelection:
    """Select the latest legal Census estimate visible at end-of-day ``as_of``."""

    as_of_date = date.fromisoformat(as_of)
    normalized = [event for event in events if event.series_id == series_id]
    future_blocked = sum(date.fromisoformat(event.availability_date) > as_of_date for event in normalized)
    eligible = [
        event
        for event in normalized
        if date.fromisoformat(event.availability_date) <= as_of_date
        and (reference_month is None or event.reference_month == reference_month)
    ]
    if not eligible:
        return CensusAsOfSelection(
            series_id=series_id,
            as_of=as_of,
            selected_event_id=None,
            selected_estimate_stage=None,
            selected_reference_month=None,
            selected_release_datetime=None,
            value=None,
            superseded_event_ids=(),
            benchmark_revision_applied=False,
            future_event_blocked_count=future_blocked,
            source_artifact_id=None,
            source_checksum=None,
            parser_version=None,
            point_in_time=False,
            missing_reason="no_legal_census_release_event",
        )
    selected = max(
        eligible,
        key=lambda event: (
            event.reference_month,
            event.availability_date,
            _stage_rank(event.estimate_stage),
            event.event_id,
        ),
    )
    superseded = tuple(
        event.event_id
        for event in eligible
        if event.reference_month == selected.reference_month and event.event_id != selected.event_id
    )
    return CensusAsOfSelection(
        series_id=series_id,
        as_of=as_of,
        selected_event_id=selected.event_id,
        selected_estimate_stage=selected.estimate_stage,
        selected_reference_month=selected.reference_month,
        selected_release_datetime=selected.release_datetime,
        value=selected.value,
        superseded_event_ids=superseded,
        benchmark_revision_applied=selected.estimate_stage == "benchmark_revision",
        future_event_blocked_count=future_blocked,
        source_artifact_id=selected.source_artifact_id,
        source_checksum=selected.source_checksum,
        parser_version=selected.parser_version,
        point_in_time=True,
    )


def _stage_rank(stage: str) -> int:
    return {
        "advance": 1,
        "full": 2,
        "revised": 3,
        "benchmark_revision": 4,
    }.get(stage, 0)

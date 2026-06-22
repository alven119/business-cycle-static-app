"""Census retail sales official release archive reconstruction helpers."""

from __future__ import annotations

from dataclasses import dataclass

from business_cycle.data_sources.census_release_event_store import (
    CensusAsOfSelection,
    select_latest_census_event_as_of,
)
from business_cycle.data_sources.census_retail_sales_pdf_parser import (
    PARSER_VERSION,
    RetailReleaseEvent,
    parse_retail_sales_release_artifact,
    parse_retail_sales_release_text,
)


@dataclass(frozen=True)
class RetailSalesEstimate:
    release_date: str
    reference_month: str
    estimate_stage: str
    value: float
    seasonal_adjustment: str
    units: str
    source_artifact_id: str
    parser_version: str = PARSER_VERSION


def parser_status() -> str:
    """Return current parser implementation status."""

    return "implemented_partial_pdf_text_parser_full_horizon_blocked"


def select_retail_sales_estimate_as_of(
    estimates: list[RetailSalesEstimate] | tuple[RetailSalesEstimate, ...],
    *,
    as_of: str,
    reference_month: str | None = None,
) -> RetailSalesEstimate | None:
    """Select the latest published RSAFS estimate visible at ``as_of``."""

    eligible = [
        item
        for item in estimates
        if item.release_date <= as_of
        and (reference_month is None or item.reference_month == reference_month)
    ]
    return max(eligible, key=lambda item: (item.reference_month, item.release_date)) if eligible else None


def parse_retail_sales_artifact_events(
    content: bytes,
    *,
    artifact_id: str,
    artifact_filename: str | None = None,
) -> tuple[RetailReleaseEvent, ...]:
    """Parse retail release events from one official artifact."""

    return parse_retail_sales_release_artifact(
        content,
        artifact_id=artifact_id,
        artifact_filename=artifact_filename,
    ).events


def parse_retail_sales_text_events(
    text: str,
    *,
    artifact_id: str,
    source_checksum: str,
    artifact_filename: str | None = None,
) -> tuple[RetailReleaseEvent, ...]:
    """Parse retail release events from normalized fixture text."""

    return parse_retail_sales_release_text(
        text,
        artifact_id=artifact_id,
        source_checksum=source_checksum,
        artifact_filename=artifact_filename,
    ).events


def select_retail_release_event_as_of(
    events: list[RetailReleaseEvent] | tuple[RetailReleaseEvent, ...],
    *,
    as_of: str,
    reference_month: str | None = None,
) -> CensusAsOfSelection:
    """Select the latest official RSAFS event visible at ``as_of``."""

    return select_latest_census_event_as_of(
        events,
        series_id="RSAFS",
        as_of=as_of,
        reference_month=reference_month,
    )

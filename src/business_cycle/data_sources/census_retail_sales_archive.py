"""Census retail sales official release archive reconstruction contract."""

from __future__ import annotations

from dataclasses import dataclass

PARSER_ID = "census_retail_sales_archive"
PARSER_VERSION = "0-blocked"


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

    return "blocked_pending_retail_release_archive_parser"


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

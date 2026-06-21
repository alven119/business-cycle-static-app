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

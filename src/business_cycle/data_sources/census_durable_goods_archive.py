"""Census durable goods official release archive reconstruction contract."""

from __future__ import annotations

from dataclasses import dataclass

PARSER_ID = "census_durable_goods_archive"
PARSER_VERSION = "0-blocked"


@dataclass(frozen=True)
class DurableGoodsEstimate:
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

    return "blocked_pending_census_m3_release_parser"


def select_durable_goods_estimate_as_of(
    estimates: list[DurableGoodsEstimate] | tuple[DurableGoodsEstimate, ...],
    *,
    as_of: str,
    reference_month: str | None = None,
) -> DurableGoodsEstimate | None:
    """Select the latest published DGORDER estimate visible at ``as_of``."""

    eligible = [
        item
        for item in estimates
        if item.release_date <= as_of
        and (reference_month is None or item.reference_month == reference_month)
    ]
    return max(eligible, key=lambda item: (item.reference_month, item.release_date)) if eligible else None

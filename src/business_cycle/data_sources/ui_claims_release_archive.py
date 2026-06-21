"""DOL/OUI weekly initial claims release archive reconstruction contract."""

from __future__ import annotations

from dataclasses import dataclass

PARSER_ID = "ui_claims_release_archive"
PARSER_VERSION = "0-blocked"


@dataclass(frozen=True)
class UiClaimsReleaseRecord:
    release_date: str
    week_ending: str
    advance_seasonally_adjusted_initial_claims: int
    previous_week_revised_initial_claims: int | None
    revision_amount: int | None
    seasonal_adjustment_status: str
    source_artifact_id: str
    checksum: str
    parser_version: str = PARSER_VERSION


def parser_status() -> str:
    """Return current parser implementation status."""

    return "blocked_pending_weekly_claims_release_parser"

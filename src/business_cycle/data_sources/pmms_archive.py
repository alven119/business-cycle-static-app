"""Freddie Mac PMMS official archive reconstruction contract."""

from __future__ import annotations

from dataclasses import dataclass

PARSER_ID = "pmms_archive"
PARSER_VERSION = "0-blocked"


@dataclass(frozen=True)
class PmmsWeeklyRecord:
    release_date: str
    survey_window_start: str
    survey_window_end: str
    reference_week: str
    mortgage_rate_30y: float
    methodology_epoch: str
    source_artifact_id: str
    checksum: str
    parser_version: str = PARSER_VERSION


def parser_status() -> str:
    """Return current parser implementation status."""

    return "blocked_pending_pmms_methodology_and_archive_review"

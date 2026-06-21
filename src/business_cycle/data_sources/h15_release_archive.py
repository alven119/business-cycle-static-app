"""Federal Reserve H.15 release archive reconstruction contract."""

from __future__ import annotations

from dataclasses import dataclass

PARSER_ID = "h15_release_archive"
PARSER_VERSION = "0-blocked"


@dataclass(frozen=True)
class H15ReleaseObservation:
    release_date: str
    observation_date: str
    dgs10_value: float
    source_artifact_id: str
    source_checksum: str
    parser_version: str = PARSER_VERSION


def parser_status() -> str:
    """Return current parser implementation status."""

    return "blocked_pending_stable_h15_release_table_parser"

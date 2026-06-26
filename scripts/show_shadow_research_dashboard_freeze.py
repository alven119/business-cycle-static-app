#!/usr/bin/env python
"""Show Phase 38 alpha35 research dashboard freeze."""

from __future__ import annotations

from business_cycle.audits.shadow_research_dashboard_freeze import (
    summarize_shadow_research_dashboard_freeze,
)


def main() -> None:
    summary = summarize_shadow_research_dashboard_freeze()
    for key in (
        "phase",
        "research_validation_dashboard_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_manifest_hash",
        "alpha35_freeze_hash_valid",
        "alpha34_parent_preserved",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "economic_validation_status",
        "phase38_dashboard_status",
        "development_next_phase",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

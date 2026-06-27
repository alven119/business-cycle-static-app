#!/usr/bin/env python
"""Generate a Phase 39 current research snapshot artifact."""

from __future__ import annotations

import argparse

from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    summarize_current_research_snapshot,
    write_current_research_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--refresh-manifest")
    parser.add_argument("--data-cache-dir")
    parser.add_argument("--allow-fixture-fallback", action="store_true")
    parser.add_argument("--no-live-fetch", action="store_true")
    args = parser.parse_args()

    snapshot = build_current_research_snapshot(
        refresh_manifest_path=args.refresh_manifest,
        data_cache_dir=args.data_cache_dir,
        allow_fixture_fallback=args.allow_fixture_fallback,
        no_live_fetch=args.no_live_fetch,
    )
    write = write_current_research_snapshot(snapshot, output=args.output)
    summary = (
        summarize_current_research_snapshot()
        if args.refresh_manifest is None
        else {
            "phase": "40",
            "current_research_snapshot_runtime_ready": snapshot[
                "artifact_validation"
            ]["artifact_schema_valid"],
            "current_snapshot_artifact_count": 1,
            "snapshot_as_of": snapshot["snapshot_as_of"],
            "data_mode": snapshot["data_mode"],
            "refresh_mode": snapshot["refresh_metadata"]["refresh_mode"],
            "live_fetch_attempted": snapshot["refresh_metadata"][
                "live_fetch_attempted"
            ],
            "live_fetch_succeeded": snapshot["refresh_metadata"][
                "live_fetch_succeeded"
            ],
            "live_fetch_skipped_reason": snapshot["refresh_metadata"][
                "live_fetch_skipped_reason"
            ],
            "live_fetch_blocked_reason": snapshot["refresh_metadata"][
                "live_fetch_blocked_reason"
            ],
            "phase41_live_refresh_status": snapshot["refresh_metadata"][
                "phase41_live_refresh_status"
            ],
            "provider_error_class": snapshot["refresh_metadata"][
                "provider_error_class"
            ],
            "cache_used": snapshot["source_availability_summary"]["cache_used"],
            "fixture_used": snapshot["source_availability_summary"]["fixture_used"],
            "available_series_count": snapshot["source_availability_summary"][
                "available_series_count"
            ],
            "missing_series_count": snapshot["source_availability_summary"][
                "missing_series_count"
            ],
            "stale_series_count": snapshot["source_availability_summary"][
                "stale_series_count"
            ],
            "unavailable_series_count": snapshot["source_availability_summary"][
                "unavailable_series_count"
            ],
            "stale_series_count_before": snapshot["refresh_metadata"][
                "stale_series_count_before"
            ],
            "stale_series_count_after": snapshot["refresh_metadata"][
                "stale_series_count_after"
            ],
            "fresh_enough_series_count": snapshot["current_freshness_summary"][
                "fresh_enough_series_count"
            ],
            "phase_profile_count": snapshot["current_evidence_readiness"][
                "phase_profile_count"
            ],
            "why_not_formal_phase_present": snapshot["current_evidence_readiness"][
                "why_not_formal_phase_present"
            ],
            "blocker_summary_present": snapshot["current_evidence_readiness"][
                "blocker_summary_present"
            ],
            "refreshed_series_count": snapshot["refresh_metadata"][
                "refreshed_series_count"
            ],
            "fetched_series_count": snapshot["refresh_metadata"][
                "fetched_series_count"
            ],
            "failed_series_count": snapshot["refresh_metadata"][
                "failed_series_count"
            ],
            "candidate_phase_emitted": snapshot["candidate_phase_emitted"],
            "current_phase_emitted": snapshot["current_phase_emitted"],
        }
    )
    for key, value in summary.items():
        if key == "snapshot":
            continue
        print(f"{key}={_format_value(value)}")
    print(f"output={write['output']}")
    print(
        "result="
        f"{'passed' if summary['current_research_snapshot_runtime_ready'] else 'blocked'}"
    )
    return 0 if summary["current_research_snapshot_runtime_ready"] else 1


def _format_value(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

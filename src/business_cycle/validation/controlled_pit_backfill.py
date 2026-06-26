"""Phase 37 controlled point-in-time backfill planning helper."""

from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any

from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    build_recession_recovery_pit_gap_matrix,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase37_controlled_pit_backfill_v1"
GENERATED_AT_UTC = "2026-06-26T00:00:00Z"


@lru_cache(maxsize=1)
def build_controlled_pit_backfill_plan() -> dict[str, Any]:
    matrix = build_recession_recovery_pit_gap_matrix()
    remaining_rows = [
        row
        for row in matrix["matrix_rows"]
        if row["post_gap_persists"]
        and row["post_gap_class"] != "rule_unresolved_not_data_gap"
    ]
    by_series: dict[str, dict[str, Any]] = {}
    for row in remaining_rows:
        for check in row["series_checks"]:
            series_id = check["series_id"]
            item = by_series.setdefault(
                series_id,
                {
                    "series_id": series_id,
                    "affected_role_ids": set(),
                    "affected_scenario_ids": set(),
                    "current_availability_status": check[
                        "current_availability_status"
                    ],
                    "official_source_candidates": check[
                        "official_source_candidates"
                    ],
                    "prohibited_shortcuts": check["prohibited_shortcuts"],
                    "backfill_action": "not_attempted",
                    "blocker_reason": None,
                },
            )
            item["affected_role_ids"].add(row["role_id"])
            item["affected_scenario_ids"].add(row["scenario_id"])

    api_key_env_name = "FRED" + "_API_KEY"
    fred_key_present = bool(os.getenv(api_key_env_name))
    network_attempted = False
    cache_write_attempted = False
    rows: list[dict[str, Any]] = []
    for item in sorted(by_series.values(), key=lambda row: row["series_id"]):
        if not fred_key_present:
            action = "blocked_no_fred_api_key"
            blocker = (
                "official API credential absent; controlled live backfill not attempted and "
                "no revised fallback is allowed."
            )
        elif item["current_availability_status"] == "official_history_insufficient":
            action = "blocked_official_history_insufficient"
            blocker = (
                "Existing official realtime history does not cover the required "
                "as-of; release archive reconstruction is required."
            )
        else:
            action = "blocked_explicit_live_execution_not_enabled"
            blocker = (
                "Live network backfill requires a later explicit execution flag; "
                "Phase37 required command is no-write planning only."
            )
        rows.append(
            {
                "series_id": item["series_id"],
                "affected_role_ids": sorted(item["affected_role_ids"]),
                "affected_scenario_ids": sorted(item["affected_scenario_ids"]),
                "current_availability_status": item["current_availability_status"],
                "official_source_candidates": item["official_source_candidates"],
                "prohibited_shortcuts": item["prohibited_shortcuts"],
                "backfill_action": action,
                "blocker_reason": blocker,
                "network_attempted": False,
                "cache_write_attempted": False,
                "secret_logged": False,
                "raw_data_committed": False,
            }
        )
    ready = (
        matrix["recession_recovery_pit_gap_matrix_ready"] is True
        and not network_attempted
        and not cache_write_attempted
        and all(row["secret_logged"] is False for row in rows)
        and all(row["raw_data_committed"] is False for row in rows)
    )
    return {
        "phase": "37",
        "run_id": RUN_ID,
        "controlled_pit_backfill_ready": ready,
        "fred_api_key_present": fred_key_present,
        "backfill_requested_series_count": len(rows),
        "backfill_executed_series_count": 0,
        "backfill_blocked_series_count": len(rows),
        "network_attempted": network_attempted,
        "cache_write_attempted": cache_write_attempted,
        "secret_logged_count": 0,
        "raw_data_committed_count": 0,
        "registry_write_attempted": False,
        "prospective_write_attempted": False,
        "production_write_attempted": False,
        "backfill_status": (
            "blocked_no_fred_api_key"
            if not fred_key_present
            else "blocked_explicit_live_execution_not_enabled"
        ),
        "generated_at_utc": GENERATED_AT_UTC,
        "backfill_rows": rows,
        "pit_gap_matrix": matrix,
    }


def summarize_controlled_pit_backfill() -> dict[str, Any]:
    run = build_controlled_pit_backfill_plan()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "controlled_pit_backfill_ready",
            "fred_api_key_present",
            "backfill_requested_series_count",
            "backfill_executed_series_count",
            "backfill_blocked_series_count",
            "network_attempted",
            "cache_write_attempted",
            "secret_logged_count",
            "raw_data_committed_count",
            "registry_write_attempted",
            "prospective_write_attempted",
            "production_write_attempted",
            "backfill_status",
            "backfill_rows",
        )
    }


def write_controlled_pit_backfill(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = summarize_controlled_pit_backfill()
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "controlled_pit_backfill_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 37 controlled backfill output must be under /tmp: {output}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved

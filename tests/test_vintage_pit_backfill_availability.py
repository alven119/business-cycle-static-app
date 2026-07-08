from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.storage.vintage_pit_backfill_availability import (
    build_vintage_pit_backfill_availability_manifest,
    summarize_vintage_pit_backfill_availability,
    write_vintage_pit_backfill_availability_manifest,
)

pytestmark = pytest.mark.archive_regression


def test_vintage_pit_backfill_availability_summary_passes() -> None:
    summary = summarize_vintage_pit_backfill_availability()

    assert summary["result"] == "passed"
    assert summary["vintage_pit_backfill_availability_contract_ready"] is True
    assert summary["vintage_pit_backfill_accounting_ready"] is True
    assert summary["phase92_revised_import_dependency_ready"] is True
    assert summary["role_count"] == 39
    assert summary["revised_import_ready_role_count"] == 37
    assert summary["role_with_pit_backfill_plan_count"] == 34
    assert summary["role_blocked_from_pit_backfill_count"] == 5
    assert summary["unique_series_count"] == 28
    assert summary["series_registry_metadata_covered_count"] == 25
    assert summary["series_missing_release_lag_registry_count"] == 3
    assert summary["pit_eligible_series_count"] == 25
    assert summary["vintage_query_supported_series_count"] == 24
    assert summary["derived_pit_plan_series_count"] == 1
    assert summary["planned_vintage_request_row_count"] == 24
    assert summary["observation_vintage_row_count"] == 0
    assert summary["strict_pit_result_emitted_count"] == 0
    assert summary["live_fetch_attempt_count"] == 0


def test_vintage_pit_backfill_rows_preserve_revised_pit_separation() -> None:
    manifest = build_vintage_pit_backfill_availability_manifest()

    assert manifest["observation_vintage_rows"] == []
    assert manifest["point_in_time_claim_count"] == 0
    assert manifest["revised_mislabeled_as_pit_count"] == 0
    assert all(
        row["actual_observation_vintage_rows_written"] == 0
        for row in manifest["backfill_availability_rows"]
    )
    assert all(
        row["strict_point_in_time_result"] is False
        for row in manifest["backfill_availability_rows"]
    )
    blocked_roles = [
        row
        for row in manifest["role_backfill_rows"]
        if row["pit_backfill_status"] == "blocked"
    ]
    assert len(blocked_roles) == 5
    assert all(row["blocked_reason_codes"] for row in blocked_roles)


def test_derived_series_requires_registry_lineage() -> None:
    manifest = build_vintage_pit_backfill_availability_manifest()
    rows = {row["series_key"]: row for row in manifest["backfill_availability_rows"]}

    assert rows["credit_spread_baa_aaa"]["backfill_request_type"] == "derived_plan"
    assert rows["credit_spread_baa_aaa"]["input_series_ids"] == ["BAA", "AAA"]
    for series_key in [
        "initial_jobless_claims_peak_reversal",
        "short_term_unemployment_peak_reversal",
        "industrial_production_bottoming",
    ]:
        assert rows[series_key]["backfill_status"] == "blocked"
        assert rows[series_key]["blocked_reason_codes"] == [
            "missing_release_lag_registry_metadata",
        ]


def test_vintage_pit_backfill_output_must_be_under_tmp(tmp_path: Path) -> None:
    manifest = build_vintage_pit_backfill_availability_manifest()
    output = tmp_path / "phase93_vintage_pit_backfill_availability.json"

    result = write_vintage_pit_backfill_availability_manifest(
        manifest,
        output=output,
    )

    assert result["dry_run_output_under_tmp_only"] is True
    assert result["repo_output_written_count"] == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["vintage_pit_backfill_accounting_ready"] is True

    with pytest.raises(ValueError, match="under /tmp"):
        write_vintage_pit_backfill_availability_manifest(
            manifest,
            output="phase93_forbidden_repo_output.json",
        )


def test_show_vintage_pit_backfill_availability_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_vintage_pit_backfill_availability.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "vintage_pit_backfill_accounting_ready=true" in result.stdout
    assert "role_with_pit_backfill_plan_count=34" in result.stdout
    assert "planned_vintage_request_row_count=24" in result.stdout


def test_run_vintage_pit_backfill_availability_dry_run_script(
    tmp_path: Path,
) -> None:
    output = tmp_path / "phase93_vintage_pit_backfill_availability.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_vintage_pit_backfill_availability_dry_run.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "vintage_pit_backfill_accounting_ready=true" in result.stdout
    assert output.is_file()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["role_count"] == 39
    assert payload["observation_vintage_row_count"] == 0

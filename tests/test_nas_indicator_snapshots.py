from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
    summarize_nas_indicator_snapshot,
    write_nas_indicator_snapshot_manifest,
)

pytestmark = pytest.mark.archive_regression


def test_nas_indicator_snapshot_summary_passes() -> None:
    summary = summarize_nas_indicator_snapshot()

    assert summary["result"] == "passed"
    assert summary["nas_indicator_snapshot_contract_ready"] is True
    assert summary["nas_indicator_snapshot_materialization_ready"] is True
    assert summary["phase92_revised_import_dependency_ready"] is True
    assert summary["phase93_pit_availability_dependency_ready"] is True
    assert summary["role_snapshot_count"] == 39
    assert summary["role_with_revised_snapshot_count"] == 37
    assert summary["role_without_revised_snapshot_count"] == 2
    assert summary["role_with_pit_backfill_plan_count"] == 34
    assert summary["role_with_pit_backfill_blocker_count"] == 5
    assert summary["series_snapshot_count"] == 28
    assert summary["source_artifact_snapshot_count"] == 28
    assert summary["observation_revised_source_row_count"] == 112
    assert summary["latest_revised_observation_context_count"] == 40
    assert summary["service_view_model_ready"] is True
    assert summary["api_endpoint_contract_count"] == 0
    assert summary["strict_pit_result_emitted_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_nas_indicator_snapshot_view_model_is_server_side_research_only() -> None:
    manifest = build_nas_indicator_snapshot_manifest()
    view_model = manifest["service_view_model"]
    trust = view_model["trust_metadata"]

    assert view_model["service_target"] == "private_nas_dynamic_service"
    assert view_model["readiness_label"] == (
        "revised_diagnostic_snapshot_with_pit_availability_accounting"
    )
    assert trust["nas_migration_surface"] == "server_side_view_model_rehearsal"
    assert trust["frontend_database_access_allowed"] is False
    assert trust["frontend_api_key_allowed"] is False
    assert trust["revised_diagnostic_only"] is True
    assert trust["pit_availability_accounting_included"] is True
    assert trust["strict_point_in_time_result"] is False


def test_nas_indicator_snapshot_rows_preserve_data_mode_boundaries() -> None:
    manifest = build_nas_indicator_snapshot_manifest()

    assert manifest["observation_vintage_row_count"] == 0
    assert manifest["point_in_time_claim_count"] == 0
    assert manifest["revised_mislabeled_as_pit_count"] == 0
    assert all(
        row["strict_point_in_time_result"] is False
        for row in manifest["role_snapshots"]
    )
    blocked = [
        row for row in manifest["role_snapshots"] if row["snapshot_status"] == "blocked"
    ]
    assert len(blocked) == 2
    assert all(row["blocked_reason_codes"] for row in blocked)
    pit_blocked = [
        row
        for row in manifest["role_snapshots"]
        if row["pit_backfill_status"] == "blocked"
    ]
    assert len(pit_blocked) == 5
    assert all(row["blocked_reason_codes"] for row in pit_blocked)


def test_nas_indicator_snapshot_output_must_be_under_tmp(tmp_path: Path) -> None:
    manifest = build_nas_indicator_snapshot_manifest()
    output = tmp_path / "phase94_nas_indicator_snapshot.json"

    result = write_nas_indicator_snapshot_manifest(manifest, output=output)

    assert result["dry_run_output_under_tmp_only"] is True
    assert result["repo_output_written_count"] == 0
    assert result["public_output_count"] == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["nas_indicator_snapshot_materialization_ready"] is True

    with pytest.raises(ValueError, match="under /tmp"):
        write_nas_indicator_snapshot_manifest(
            manifest,
            output="phase94_forbidden_repo_output.json",
        )


def test_show_nas_indicator_snapshot_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_indicator_snapshot.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_indicator_snapshot_materialization_ready=true" in result.stdout
    assert "role_snapshot_count=39" in result.stdout
    assert "service_view_model_ready=true" in result.stdout


def test_run_nas_indicator_snapshot_dry_run_script(tmp_path: Path) -> None:
    output = tmp_path / "phase94_nas_indicator_snapshot.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_indicator_snapshot_dry_run.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_indicator_snapshot_materialization_ready=true" in result.stdout
    assert output.is_file()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["service_view_model"]["service_target"] == (
        "private_nas_dynamic_service"
    )

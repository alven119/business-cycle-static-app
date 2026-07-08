from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.storage.revised_macro_data_import import (
    build_revised_macro_data_import_manifest,
    summarize_revised_macro_data_import,
    write_revised_macro_data_import_manifest,
)

pytestmark = pytest.mark.archive_regression


def test_revised_macro_data_import_summary_passes() -> None:
    summary = summarize_revised_macro_data_import()

    assert summary["result"] == "passed"
    assert summary["revised_macro_data_import_contract_ready"] is True
    assert summary["revised_macro_data_import_dry_run_ready"] is True
    assert summary["postgres_macro_warehouse_dependency_ready"] is True
    assert summary["role_count"] == 39
    assert summary["revised_import_ready_role_count"] == 37
    assert summary["revised_import_blocked_role_count"] == 2
    assert summary["unique_series_count"] == 28
    assert summary["series_registry_row_count"] == 28
    assert summary["source_artifact_row_count"] == 28
    assert summary["observation_revised_row_count"] == 112
    assert summary["observation_vintage_row_count"] == 0
    assert summary["point_in_time_claim_count"] == 0
    assert summary["revised_mislabeled_as_pit_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_revised_macro_data_import_rows_match_phase91_shape() -> None:
    manifest = build_revised_macro_data_import_manifest()

    assert {row["data_mode"] for row in manifest["observation_revised_rows"]} == {
        "revised",
    }
    assert manifest["observation_vintage_rows"] == []
    assert all(row["content_hash"] for row in manifest["source_artifact_rows"])
    assert all(row["provenance_hash"] for row in manifest["observation_revised_rows"])
    assert all(row["no_secret"] is True for row in manifest["source_artifact_rows"])
    blocked = [
        row
        for row in manifest["role_import_rows"]
        if row["revised_import_status"] == "blocked"
    ]
    assert len(blocked) == 2
    assert all(row["blocked_reason_codes"] for row in blocked)
    assert all(row["point_in_time_result"] is False for row in manifest["role_import_rows"])


def test_revised_macro_data_import_output_must_be_under_tmp(tmp_path: Path) -> None:
    manifest = build_revised_macro_data_import_manifest()
    output = tmp_path / "phase92_revised_macro_data_import.json"

    result = write_revised_macro_data_import_manifest(manifest, output=output)

    assert result["dry_run_output_under_tmp_only"] is True
    assert result["repo_output_written_count"] == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["revised_macro_data_import_dry_run_ready"] is True

    with pytest.raises(ValueError, match="under /tmp"):
        write_revised_macro_data_import_manifest(
            manifest,
            output="phase92_forbidden_repo_output.json",
        )


def test_show_revised_macro_data_import_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_revised_macro_data_import.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "revised_macro_data_import_dry_run_ready=true" in result.stdout
    assert "role_count=39" in result.stdout
    assert "revised_import_ready_role_count=37" in result.stdout
    assert "observation_revised_row_count=112" in result.stdout


def test_run_revised_macro_data_import_dry_run_script(tmp_path: Path) -> None:
    output = tmp_path / "phase92_revised_macro_data_import.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_revised_macro_data_import_dry_run.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "revised_macro_data_import_dry_run_ready=true" in result.stdout
    assert output.is_file()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["role_count"] == 39
    assert payload["observation_revised_row_count"] == 112

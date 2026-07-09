from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

import pytest

from business_cycle.service.nas_container_manager_live_start import (
    build_nas_container_manager_live_start_package,
    load_nas_container_manager_live_start_contract,
    summarize_nas_container_manager_live_start,
    validate_nas_container_manager_live_start_report,
    write_nas_container_manager_live_start_package,
)

pytestmark = pytest.mark.archive_regression


def test_nas_container_manager_live_start_summary_passes() -> None:
    summary = summarize_nas_container_manager_live_start()

    assert summary["result"] == "passed"
    assert summary["nas_container_manager_live_start_package_ready"] is True
    assert summary["app_image_reference"] == "business-cycle-nas-app:phase107"
    assert summary["required_operator_action_count"] == 34
    assert summary["live_start_acceptance_status"] == "operator_report_required"
    assert summary["live_deployment_complete"] is False
    assert summary["codex_container_start_attempt_count"] == 0
    assert summary["current_phase_emitted"] is False


def test_nas_container_manager_live_start_sample_report_validates() -> None:
    package = build_nas_container_manager_live_start_package()
    contract = load_nas_container_manager_live_start_contract()

    validation = validate_nas_container_manager_live_start_report(
        package["sample_operator_report"],
        contract,
    )

    assert validation["operator_report_valid"] is True
    assert validation["live_start_acceptance_status"] == "accepted"
    assert validation["live_deployment_complete"] is True
    assert validation["operator_report_passed_action_count"] == 34


def test_nas_container_manager_live_start_bad_report_blocks() -> None:
    package = build_nas_container_manager_live_start_package()
    contract = load_nas_container_manager_live_start_contract()
    bad_report = dict(package["sample_operator_report"])
    bad_report["health_auth_summary"] = {
        **bad_report["health_auth_summary"],
        "unauthenticated_dashboard_request": "allowed",
    }

    validation = validate_nas_container_manager_live_start_report(
        bad_report,
        contract,
    )

    assert validation["operator_report_valid"] is False
    assert validation["live_start_acceptance_status"] == "blocked"


def test_nas_container_manager_live_start_writes_only_tmp(tmp_path: Path) -> None:
    result = write_nas_container_manager_live_start_package(tmp_path)

    assert result["result"] == "passed"
    assert result["live_start_package_output_path_count"] == 7
    assert result["live_start_package_output_under_tmp_only"] is True
    for path in result["written_paths"]:
        assert Path(path).is_file()

    report_path = tmp_path / "sample-accepted-live-start-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["app_image_reference"] == "business-cycle-nas-app:phase107"


def test_nas_container_manager_live_start_rejects_repo_output() -> None:
    with pytest.raises(ValueError, match="under /tmp"):
        write_nas_container_manager_live_start_package(
            Path("tmp-phase108-output"),
        )


def test_show_nas_container_manager_live_start_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_container_manager_live_start.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_container_manager_live_start_package_ready=true" in result.stdout
    assert "live_start_acceptance_status=operator_report_required" in result.stdout
    assert "codex_container_start_attempt_count=0" in result.stdout


def test_run_nas_container_manager_live_start_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_container_manager_live_start.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_container_manager_live_start_package_ready=true" in result.stdout
    assert "live_start_package_output_path_count=7" in result.stdout
    assert (tmp_path / "operator-live-start-report-template.json").is_file()

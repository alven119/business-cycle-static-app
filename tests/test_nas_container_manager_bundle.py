from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from business_cycle.service.nas_container_manager_bundle import (
    build_nas_container_manager_bundle,
    summarize_nas_container_manager_bundle,
    write_nas_container_manager_bundle_dry_run,
)

pytestmark = pytest.mark.archive_regression


def test_nas_container_manager_bundle_summary_passes() -> None:
    summary = summarize_nas_container_manager_bundle()

    assert summary["result"] == "passed"
    assert summary["nas_container_manager_bundle_contract_ready"] is True
    assert summary["nas_container_manager_bundle_ready"] is True
    assert summary["ds925_package_assessment_dependency_ready"] is True
    assert summary["phase99_readonly_smoke_dependency_ready"] is True
    assert summary["phase98_lifecycle_dependency_ready"] is True
    assert summary["compose_yaml_valid"] is True
    assert summary["compose_service_count"] == 3
    assert summary["healthcheck_service_count"] == 3
    assert summary["host_port_publish_count"] == 0
    assert summary["secret_value_literal_count"] == 0
    assert summary["container_manager_import_attempt_count"] == 0
    assert summary["docker_compose_execution_count"] == 0
    assert summary["container_start_attempt_count"] == 0


def test_nas_container_manager_bundle_compose_preserves_private_boundaries() -> None:
    bundle = build_nas_container_manager_bundle()
    compose = yaml.safe_load(bundle["compose_yaml"])

    assert set(compose["services"]) == {
        "macro_postgres",
        "business_cycle_app",
        "macro_refresh_worker",
    }
    assert "ports" not in compose["services"]["business_cycle_app"]
    assert compose["networks"]["business_cycle_private"]["internal"] is True
    assert compose["services"]["macro_refresh_worker"]["profiles"] == [
        "manual-refresh-disabled-until-phase-gate",
    ]
    assert bundle["frontend_database_access_allowed"] is False
    assert bundle["frontend_api_key_allowed"] is False
    assert bundle["candidate_phase_emitted"] is False
    assert bundle["current_phase_emitted"] is False


def test_nas_container_manager_bundle_dry_run_writes_only_tmp(tmp_path: Path) -> None:
    output = write_nas_container_manager_bundle_dry_run(tmp_path)

    assert output["result"] == "passed"
    assert output["dry_run_output_path_count"] == 4
    assert output["dry_run_output_under_tmp_only"] is True
    assert output["repo_output_written_count"] == 0
    assert output["public_output_count"] == 0
    for path in output["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_container_manager_bundle_rejects_repo_output_path() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_container_manager_bundle_dry_run(Path("tmp-phase100-output"))


def test_show_nas_container_manager_bundle_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_container_manager_bundle.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_container_manager_bundle_ready=true" in result.stdout
    assert "compose_yaml_valid=true" in result.stdout
    assert "compose_service_count=3" in result.stdout
    assert "host_port_publish_count=0" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_container_manager_bundle_dry_run_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_container_manager_bundle_dry_run.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_container_manager_bundle_ready=true" in result.stdout
    assert "compose_yaml_valid=true" in result.stdout
    assert "docker_compose_execution_count=0" in result.stdout
    assert "dry_run_output_path_count=4" in result.stdout
    assert "dry_run_output_under_tmp_only=true" in result.stdout

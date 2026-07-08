from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.service.nas_private_asgi_app import create_app
from business_cycle.service.nas_private_local_startup_smoke import (
    build_nas_private_local_startup_smoke,
    summarize_nas_private_local_startup_smoke,
    write_nas_private_local_startup_smoke_report,
)

pytestmark = pytest.mark.archive_regression


def test_nas_private_local_startup_smoke_summary_passes() -> None:
    summary = summarize_nas_private_local_startup_smoke()

    assert summary["result"] == "passed"
    assert summary["nas_private_local_startup_smoke_contract_ready"] is True
    assert summary["nas_private_local_startup_smoke_ready"] is True
    assert summary["phase100_bundle_dependency_ready"] is True
    assert summary["phase98_lifecycle_dependency_ready"] is True
    assert summary["phase97_asgi_dependency_ready"] is True
    assert summary["asgi_entrypoint_factory_ready"] is True
    assert summary["startup_command_preview_count"] == 1
    assert summary["startup_command_executed_count"] == 0
    assert summary["readiness_probe_pass_count"] == 5
    assert summary["uvicorn_run_attempt_count"] == 0
    assert summary["network_bind_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0


def test_nas_private_local_startup_smoke_preserves_private_boundaries() -> None:
    smoke = build_nas_private_local_startup_smoke()
    plan = smoke["startup_plan"]

    assert plan["host"] == "127.0.0.1"
    assert plan["command_preview_only"] is True
    assert "--factory" in plan["startup_command_preview"][0]
    assert "0.0.0.0" not in plan["startup_command_preview"][0]
    assert smoke["local_loopback_or_tailnet_only"] is True
    assert smoke["bind_host_public_count"] == 0
    assert smoke["frontend_database_access_allowed"] is False
    assert smoke["frontend_api_key_allowed"] is False
    assert smoke["candidate_phase_emitted"] is False
    assert smoke["current_phase_emitted"] is False


def test_nas_private_asgi_app_factory_is_callable() -> None:
    app = create_app()

    assert callable(app)


def test_nas_private_local_startup_smoke_writes_only_tmp(tmp_path: Path) -> None:
    output = write_nas_private_local_startup_smoke_report(tmp_path)

    assert output["result"] == "passed"
    assert output["startup_smoke_output_path_count"] == 3
    assert output["startup_smoke_output_under_tmp_only"] is True
    assert output["repo_output_written_count"] == 0
    assert output["public_output_count"] == 0
    for path in output["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_private_local_startup_smoke_rejects_repo_output_path() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_private_local_startup_smoke_report(Path("tmp-phase101-output"))


def test_show_nas_private_local_startup_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_private_local_startup_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_private_local_startup_smoke_ready=true" in result.stdout
    assert "startup_command_preview_ready=true" in result.stdout
    assert "readiness_probe_pass_count=5" in result.stdout
    assert "uvicorn_run_attempt_count=0" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_private_local_startup_smoke_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_private_local_startup_smoke.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_private_local_startup_smoke_ready=true" in result.stdout
    assert "startup_plan_ready=true" in result.stdout
    assert "startup_smoke_output_path_count=3" in result.stdout
    assert "startup_smoke_output_under_tmp_only=true" in result.stdout

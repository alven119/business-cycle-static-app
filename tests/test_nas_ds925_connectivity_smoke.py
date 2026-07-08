from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.service.nas_ds925_connectivity_smoke import (
    build_nas_ds925_connectivity_smoke,
    summarize_nas_ds925_connectivity_smoke,
    write_nas_ds925_connectivity_smoke_report,
)

pytestmark = pytest.mark.archive_regression


def test_nas_ds925_connectivity_smoke_summary_passes_without_network() -> None:
    summary = summarize_nas_ds925_connectivity_smoke()

    assert summary["result"] == "passed"
    assert summary["nas_ds925_connectivity_smoke_ready"] is True
    assert summary["nas_private_ip"] == "192.168.1.116"
    assert summary["nas_private_ip_private_lan"] is True
    assert summary["live_probe_requires_explicit_flag"] is True
    assert summary["default_probe_execution_count"] == 0
    assert summary["tests_network_dependency_count"] == 0
    assert summary["dsm_login_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0


def test_nas_ds925_connectivity_smoke_live_probe_can_be_stubbed() -> None:
    def fake_connector(ip: str, port: int, timeout: float) -> bool:
        assert ip == "192.168.1.116"
        assert timeout == 2.0
        return port == 5000

    smoke = build_nas_ds925_connectivity_smoke(
        execute_live=True,
        connector=fake_connector,
    )

    assert smoke["live_probe_executed"] is True
    assert smoke["live_probe_attempt_count"] == 4
    assert smoke["live_probe_reachable_count"] == 1
    assert smoke["live_probe_unreachable_count"] == 3
    assert smoke["nas_ds925_connectivity_smoke_ready"] is True
    assert smoke["http_request_attempt_count"] == 0
    assert smoke["dsm_login_attempt_count"] == 0
    assert smoke["postgres_write_attempt_count"] == 0


def test_nas_ds925_connectivity_smoke_writes_only_tmp(tmp_path: Path) -> None:
    output = write_nas_ds925_connectivity_smoke_report(tmp_path)

    assert output["result"] == "passed"
    assert output["connectivity_smoke_output_path_count"] == 3
    assert output["connectivity_smoke_output_under_tmp_only"] is True
    assert output["repo_output_written_count"] == 0
    assert output["public_output_count"] == 0
    for path in output["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_ds925_connectivity_smoke_rejects_repo_output_path() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_ds925_connectivity_smoke_report(Path("tmp-phase103-output"))


def test_show_nas_ds925_connectivity_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_ds925_connectivity_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_ds925_connectivity_smoke_ready=true" in result.stdout
    assert "nas_private_ip=192.168.1.116" in result.stdout
    assert "default_probe_execution_count=0" in result.stdout
    assert "dsm_login_attempt_count=0" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_ds925_connectivity_smoke_script_no_network(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_ds925_connectivity_smoke.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_ds925_connectivity_smoke_ready=true" in result.stdout
    assert "live_probe_executed=false" in result.stdout
    assert "live_probe_attempt_count=0" in result.stdout
    assert "connectivity_smoke_output_path_count=3" in result.stdout
    assert "connectivity_smoke_output_under_tmp_only=true" in result.stdout

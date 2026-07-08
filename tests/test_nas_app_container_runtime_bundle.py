from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from business_cycle.service.nas_app_container_runtime_bundle import (
    build_nas_app_container_runtime_bundle,
    summarize_nas_app_container_runtime_bundle,
    write_nas_app_container_runtime_bundle,
)

pytestmark = pytest.mark.archive_regression


def test_nas_app_container_runtime_bundle_summary_passes() -> None:
    summary = summarize_nas_app_container_runtime_bundle()

    assert summary["result"] == "passed"
    assert summary["nas_app_container_runtime_bundle_ready"] is True
    assert summary["dockerfile_present"] is True
    assert summary["dockerignore_present"] is True
    assert summary["runtime_server_module_ready"] is True
    assert summary["healthcheck_module_ready"] is True
    assert summary["refresh_worker_disabled_module_ready"] is True
    assert summary["app_image_reference"] == "business-cycle-nas-app:phase107"
    assert summary["dry_run_image_reference_count"] == 0
    assert summary["loopback_host_port_publish_count"] == 1
    assert summary["public_host_port_publish_count"] == 0
    assert summary["docker_build_attempt_count"] == 0
    assert summary["container_start_attempt_count"] == 0


def test_nas_app_container_runtime_compose_is_buildable_shape() -> None:
    bundle = build_nas_app_container_runtime_bundle()
    compose = yaml.safe_load(bundle["compose_yaml"])
    app = compose["services"]["business_cycle_app"]

    assert app["image"] == "business-cycle-nas-app:phase107"
    assert app["build"] == {"context": ".", "dockerfile": "Dockerfile.nas"}
    assert app["ports"] == ["127.0.0.1:18080:8000"]
    assert compose["networks"]["business_cycle_private"]["internal"] is True
    assert "dry-run" not in bundle["compose_yaml"]
    assert "docs/景氣循環投資.pdf" in bundle["dockerignore"]
    assert "data/raw" in bundle["dockerignore"]
    assert "BUSINESS_CYCLE_APP_SESSION_SECRET" in bundle["env_template"]


def test_nas_app_container_runtime_bundle_writes_only_tmp(tmp_path: Path) -> None:
    output = write_nas_app_container_runtime_bundle(tmp_path)

    assert output["result"] == "passed"
    assert output["runtime_bundle_output_path_count"] == 7
    assert output["runtime_bundle_output_under_tmp_only"] is True
    assert output["repo_output_written_count"] == 0
    assert output["public_output_count"] == 0
    for path in output["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_app_container_runtime_bundle_rejects_repo_output_path() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_app_container_runtime_bundle(Path("tmp-phase107-output"))


def test_show_nas_app_container_runtime_bundle_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_app_container_runtime_bundle.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_app_container_runtime_bundle_ready=true" in result.stdout
    assert "app_image_reference=business-cycle-nas-app:phase107" in result.stdout
    assert "public_host_port_publish_count=0" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_app_container_runtime_bundle_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_app_container_runtime_bundle.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_app_container_runtime_bundle_ready=true" in result.stdout
    assert "runtime_bundle_output_path_count=7" in result.stdout
    assert "runtime_bundle_output_under_tmp_only=true" in result.stdout

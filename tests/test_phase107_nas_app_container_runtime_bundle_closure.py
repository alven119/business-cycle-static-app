from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase107_nas_app_container_runtime_bundle_closure import (
    summarize_phase107_nas_app_container_runtime_bundle_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase107_nas_app_container_runtime_bundle_closure_passes() -> None:
    summary = summarize_phase107_nas_app_container_runtime_bundle_closure()

    assert summary["result"] == "passed"
    assert summary["phase107_closure_ready"] is True
    assert summary["nas_app_container_runtime_bundle_ready"] is True
    assert summary["phase106_operator_preflight_dependency_ready"] is True
    assert summary["app_image_reference"] == "business-cycle-nas-app:phase107"
    assert summary["dry_run_image_reference_count"] == 0
    assert summary["public_host_port_publish_count"] == 0
    assert summary["docker_build_attempt_count"] == 0
    assert summary["container_start_attempt_count"] == 0
    assert summary["development_next_phase"] == 108
    assert (
        summary["phase107_closure_status"]
        == "closed_nas_app_container_runtime_bundle_ready_no_live_start"
    )


def test_show_phase107_nas_app_container_runtime_bundle_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase107_nas_app_container_runtime_bundle_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase107_closure_ready=true" in result.stdout
    assert "nas_app_container_runtime_bundle_ready=true" in result.stdout
    assert "app_image_reference=business-cycle-nas-app:phase107" in result.stdout
    assert (
        "phase107_closure_status="
        "closed_nas_app_container_runtime_bundle_ready_no_live_start"
    ) in result.stdout

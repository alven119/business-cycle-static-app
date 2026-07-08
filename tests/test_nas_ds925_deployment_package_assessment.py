from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.nas_ds925_deployment_package_assessment import (
    summarize_nas_ds925_deployment_package_assessment,
)

pytestmark = pytest.mark.archive_regression


def test_nas_ds925_deployment_package_assessment_passes() -> None:
    summary = summarize_nas_ds925_deployment_package_assessment()

    assert summary["result"] == "passed"
    assert summary["nas_ds925_package_assessment_ready"] is True
    assert summary["assessed_package_count"] == 5
    assert summary["recommended_package_count"] == 4
    assert summary["primary_runtime_recommended"] == "synology_container_manager"
    assert summary["private_mobile_access_recommended"] == "tailscale"
    assert summary["database_runtime_recommended"] == "postgres_container_image"
    assert summary["public_internet_exposure_default"] is False
    assert summary["deployment_phase_estimate_ready"] is True
    assert summary["earliest_private_alpha_phase"] == 101
    assert summary["recommended_guided_ds925_deploy_phase"] == 102
    assert summary["full_private_nas_use_phase"] == 104


def test_show_nas_ds925_deployment_package_assessment_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_ds925_deployment_package_assessment.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_ds925_package_assessment_ready=true" in result.stdout
    assert "primary_runtime_recommended=synology_container_manager" in result.stdout
    assert "private_mobile_access_recommended=tailscale" in result.stdout
    assert "recommended_guided_ds925_deploy_phase=102" in result.stdout
    assert "result=passed" in result.stdout

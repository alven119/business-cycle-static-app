from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.genuine_validation_blocker_work_packages import (
    build_genuine_validation_blocker_work_packages,
    summarize_genuine_validation_blocker_work_packages,
)


def test_genuine_validation_blocker_work_packages_are_ready() -> None:
    summary = summarize_genuine_validation_blocker_work_packages()
    registry = build_genuine_validation_blocker_work_packages()

    assert summary["genuine_blocker_resolution_protocol_ready"] is True
    assert summary["genuine_blocker_work_package_registry_ready"] is True
    assert summary["reviewed_genuine_blocker_count"] == 5
    assert summary["work_package_count"] == 5
    assert summary["blocker_without_work_package_count"] == 0
    assert summary["work_package_without_source_blocker_count"] == 0
    assert summary["work_package_without_allowed_action_count"] == 0
    assert summary["work_package_without_prohibited_action_count"] == 0
    assert summary["work_package_without_completion_gate_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["blocker_resolution_executed"] is False
    assert summary["scenario_promoted_to_comparable_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert registry["validation"]["work_package_registry_valid"] is True

    for package in summary["work_packages"]:
        assert package["requires_preregistration"] is True
        assert package["current_status"] == "preregistered_unresolved"
        assert package["can_be_resolved_without_threshold"] is True
        assert package["allowed_resolution_actions"]
        assert "tune_rule_from_historical_result" in package[
            "prohibited_resolution_actions"
        ]
        assert package["completion_gate"]


def test_show_genuine_validation_blocker_work_packages_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_genuine_validation_blocker_work_packages.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase=32" in result.stdout
    assert "genuine_blocker_work_package_registry_ready=true" in result.stdout
    assert "reviewed_genuine_blocker_count=5" in result.stdout
    assert "work_package_count=5" in result.stdout
    assert "blocker_resolution_executed=false" in result.stdout

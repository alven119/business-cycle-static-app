from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase90_nas_dynamic_service_architecture_closure import (
    summarize_phase90_nas_dynamic_service_architecture_closure,
)


def test_phase90_nas_dynamic_service_architecture_closure_passes() -> None:
    summary = summarize_phase90_nas_dynamic_service_architecture_closure()

    assert summary["result"] == "passed"
    assert summary["phase90_closure_ready"] is True
    assert summary["nas_dynamic_service_contract_ready"] is True
    assert summary["github_pages_deployment_retired"] is True
    assert summary["pages_workflow_present"] is False
    assert summary["pages_action_reference_count"] == 0
    assert summary["dynamic_service_runtime_planned"] is True
    assert summary["planned_web_framework"] == "fastapi"
    assert summary["private_mobile_access_model"] == "tailscale_or_vpn_first"
    assert summary["postgres_pit_schema_planned"] is True
    assert summary["revised_first_backfill_policy_present"] is True
    assert summary["vintage_backfill_plan_present"] is True
    assert summary["development_next_phase"] == 91


def test_show_phase90_nas_dynamic_service_architecture_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase90_nas_dynamic_service_architecture_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase90_closure_ready=true" in result.stdout
    assert "github_pages_deployment_retired=true" in result.stdout
    assert "planned_web_framework=fastapi" in result.stdout
    assert "development_next_phase=91" in result.stdout
    assert "result=passed" in result.stdout

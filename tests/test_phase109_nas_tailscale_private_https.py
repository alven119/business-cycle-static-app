from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase109_nas_tailscale_private_https_closure import (
    summarize_phase109_nas_tailscale_private_https_closure,
)
from business_cycle.service.nas_tailscale_private_https import (
    build_nas_tailscale_private_https_acceptance,
    load_nas_tailscale_private_https_contract,
    summarize_nas_tailscale_private_https,
    validate_nas_tailscale_private_https_report,
)

pytestmark = pytest.mark.archive_regression


def test_phase109_private_https_acceptance_records_live_mobile_boundary() -> None:
    summary = summarize_nas_tailscale_private_https()

    assert summary["result"] == "passed"
    assert summary["nas_tailscale_private_https_package_ready"] is True
    assert summary["runtime_https_cookie_contract_ready"] is True
    assert summary["runtime_login_rate_limit_ready"] is True
    assert summary["runtime_security_headers_ready"] is True
    assert summary["tailscale_backend_online_observed"] is True
    assert summary["tailscale_serve_configured"] is True
    assert summary["tailscale_funnel_configured"] is False
    assert summary["mobile_cellular_smoke_passed"] is True
    assert summary["private_https_accepted"] is True
    assert summary["operator_action_required"] is False
    assert summary["postgres_business_table_count_observed"] == 11
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase109_acceptance_report_requires_every_private_boundary() -> None:
    package = build_nas_tailscale_private_https_acceptance()
    contract = load_nas_tailscale_private_https_contract()
    accepted = validate_nas_tailscale_private_https_report(
        package["sample_acceptance_report"],
        contract,
    )
    rejected_report = dict(package["sample_acceptance_report"])
    rejected_report["funnel_disabled"] = False
    rejected = validate_nas_tailscale_private_https_report(
        rejected_report,
        contract,
    )

    assert accepted["report_valid"] is True
    assert accepted["private_https_accepted"] is True
    assert rejected["report_valid"] is False
    assert rejected["private_https_accepted"] is False
    assert rejected["false_acceptance_field_count"] == 1


def test_phase109_private_https_closure_passes_as_accepted_boundary() -> None:
    summary = summarize_phase109_nas_tailscale_private_https_closure()

    assert summary["result"] == "passed"
    assert summary["phase109_checkpoint_ready"] is True
    assert summary["private_https_accepted"] is True
    assert summary["development_next_phase"] == 110
    assert summary["phase109_closure_status"] == (
        "closed_tailscale_private_https_and_mobile_acceptance"
    )


def test_phase109_show_scripts_report_accepted_private_https() -> None:
    private_https = subprocess.run(
        [sys.executable, "scripts/show_nas_tailscale_private_https.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    closure = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase109_nas_tailscale_private_https_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "private_https_accepted=true" in private_https.stdout
    assert "tailscale_funnel_configured=false" in private_https.stdout
    assert "result=passed" in closure.stdout
    assert (
        "phase109_closure_status="
        "closed_tailscale_private_https_and_mobile_acceptance"
        in closure.stdout
    )

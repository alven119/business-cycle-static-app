from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase95_nas_service_dashboard_closure import (
    summarize_phase95_nas_service_dashboard_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase95_nas_service_dashboard_closure_passes() -> None:
    summary = summarize_phase95_nas_service_dashboard_closure()

    assert summary["result"] == "passed"
    assert summary["phase95_closure_ready"] is True
    assert summary["nas_service_dashboard_contract_ready"] is True
    assert summary["nas_service_html_renderer_ready"] is True
    assert summary["traditional_chinese_role_label_count"] == 39
    assert summary["product_capability_rebaseline_recorded"] is True
    assert summary["progress_decrease_count"] == 0
    assert summary["progress_decrease_without_reason_count"] == 0
    assert summary["live_server_start_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["phase95_closure_status"] == (
        "closed_nas_service_dashboard_route_api_html_rehearsed_no_live_server_or_db"
    )


def test_show_phase95_nas_service_dashboard_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase95_nas_service_dashboard_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase95_closure_ready=true" in result.stdout
    assert "nas_service_html_renderer_ready=true" in result.stdout
    assert "progress_decrease_count=0" in result.stdout
    assert "result=passed" in result.stdout

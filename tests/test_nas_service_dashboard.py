from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
    summarize_nas_service_dashboard,
    write_nas_service_dashboard_dry_run,
)

pytestmark = pytest.mark.archive_regression


def test_nas_service_dashboard_summary_passes() -> None:
    summary = summarize_nas_service_dashboard()

    assert summary["result"] == "passed"
    assert summary["nas_service_dashboard_contract_ready"] is True
    assert summary["nas_service_route_manifest_ready"] is True
    assert summary["nas_service_api_payload_ready"] is True
    assert summary["nas_service_html_renderer_ready"] is True
    assert summary["private_nas_service_target_ready"] is True
    assert summary["phase94_snapshot_dependency_ready"] is True
    assert summary["product_capability_rebaseline_recorded"] is True
    assert summary["route_count"] == 4
    assert summary["api_payload_count"] == 3
    assert summary["html_page_count"] == 2
    assert summary["role_card_count"] == 39
    assert summary["indicator_snapshot_api_role_count"] == 39
    assert summary["html_role_card_count"] == 39
    assert summary["html_revised_snapshot_role_count"] == 37
    assert summary["html_blocked_role_count"] == 2
    assert summary["mobile_trust_caveat_count"] == 6


def test_nas_service_dashboard_preserves_private_no_live_boundaries() -> None:
    bundle = build_nas_service_dashboard_bundle()
    status = bundle["api_payloads"]["service_status"]

    assert bundle["service_target"] == "private_nas_dynamic_service"
    assert status["live_db_connection_attempted"] is False
    assert status["postgres_write_attempted"] is False
    assert status["live_fetch_attempted"] is False
    assert status["frontend_database_access_allowed"] is False
    assert status["frontend_api_key_allowed"] is False
    assert bundle["candidate_phase_emitted"] is False
    assert bundle["current_phase_emitted"] is False
    assert bundle["prohibited_output_field_count"] == 0


def test_nas_service_dashboard_html_is_chinese_research_surface() -> None:
    bundle = build_nas_service_dashboard_bundle()
    html = "\n".join(page["html"] for page in bundle["html_pages"])

    assert "NAS 私有研究儀表板" in html
    assert "總經指標快照" in html
    assert "研究用，不是正式景氣階段判斷" in html
    assert "不是投資建議" in html
    assert 'data-role-card="true"' in html
    assert 'data-snapshot-status="blocked"' in html


def test_nas_service_dashboard_output_must_be_under_tmp(tmp_path: Path) -> None:
    bundle = build_nas_service_dashboard_bundle()
    result = write_nas_service_dashboard_dry_run(bundle, output_dir=tmp_path)

    assert result["dry_run_output_under_tmp_only"] is True
    assert result["written_file_count"] == 5
    assert result["repo_output_written_count"] == 0
    assert result["public_output_count"] == 0
    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "indicators/index.html").is_file()
    payload = json.loads((tmp_path / "api/indicator-snapshot.json").read_text())
    assert payload["role_count"] == 39

    with pytest.raises(ValueError, match="under /tmp"):
        write_nas_service_dashboard_dry_run(
            bundle,
            output_dir="phase95_forbidden_repo_output",
        )


def test_show_nas_service_dashboard_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_service_dashboard.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_service_dashboard_ready=true" in result.stdout
    assert "route_count=4" in result.stdout
    assert "html_role_card_count=39" in result.stdout


def test_render_nas_service_dashboard_dry_run_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/render_nas_service_dashboard_dry_run.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_service_dashboard_ready=true" in result.stdout
    assert "written_file_count=5" in result.stdout
    assert (tmp_path / "api/service-status.json").is_file()

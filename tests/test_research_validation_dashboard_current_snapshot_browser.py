from __future__ import annotations

import json
import subprocess
import sys

from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


def test_current_snapshot_dashboard_view_renders_without_forbidden_outputs(tmp_path) -> None:
    snapshot = build_current_research_snapshot()
    bundle = build_research_dashboard_bundle(current_snapshot=snapshot)
    result = build_research_validation_dashboard(
        output_dir=tmp_path,
        bundle=bundle,
    )
    html = (tmp_path / "current-snapshot.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert result["prohibited_claim_count"] == 0
    assert result["prohibited_action_field_count"] == 0
    assert bundle["dashboard_view_count"] >= 8
    assert 'data-dashboard-view="current_research_snapshot"' in html
    assert "研究用途" in html
    assert "新鮮度足夠" in html
    assert "資料更新與來源新鮮度" in html
    assert "目前階段證據剖面" in html
    assert 'data-phase-profile-card="recovery"' in html
    assert 'data-phase-profile-card="growth"' in html
    assert 'data-phase-profile-card="boom"' in html
    assert 'data-phase-profile-card="recession"' in html
    assert "為什麼尚非正式判讀" in html
    assert "watch 不等於 confirmation" in html
    assert "判讀 readiness blockers" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_build_dashboard_script_accepts_current_snapshot(tmp_path) -> None:
    snapshot_path = tmp_path / "phase39_current_snapshot.json"
    snapshot_path.write_text(
        json.dumps(build_current_research_snapshot(), indent=2),
        encoding="utf-8",
    )
    output_dir = tmp_path / "dashboard"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_research_validation_dashboard.py",
            "--output-dir",
            str(output_dir),
            "--include-current-snapshot",
            str(snapshot_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (output_dir / "current-snapshot.html").is_file()
    assert "dashboard_view_count=8" in result.stdout
    assert "browser_verification_ready=true" in result.stdout


def test_current_snapshot_dashboard_view_shows_phase40_refresh_metadata(tmp_path) -> None:
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    snapshot = build_current_research_snapshot(refresh_manifest=manifest)
    bundle = build_research_dashboard_bundle(current_snapshot=snapshot)
    result = build_research_validation_dashboard(
        output_dir=tmp_path,
        bundle=bundle,
    )
    html = (tmp_path / "current-snapshot.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert "data-refresh-panel" in html
    assert "data-current-phase-evidence-profile" in html
    assert "data-refresh-mode" in html
    assert "live_fetch_disabled_by_cli" in html
    assert manifest["manifest_hash"] in html
    assert "來源模式" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html

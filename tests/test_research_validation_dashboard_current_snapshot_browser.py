from __future__ import annotations

import json
import subprocess
import sys

from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
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
    assert "RESEARCH ONLY" in html
    assert "Available series" in html
    assert "Decision readiness blockers" in html
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

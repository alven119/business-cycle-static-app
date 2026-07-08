from __future__ import annotations

import subprocess
import sys

from business_cycle.render.boom_transition_dashboard_surface import (
    build_boom_transition_dashboard_surface,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


def test_research_dashboard_renders_declared_boom_transition_surface(tmp_path) -> None:
    surface = build_boom_transition_dashboard_surface()
    bundle = build_research_dashboard_bundle(boom_transition_surface=surface)
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "boom-transition.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert result["prohibited_claim_count"] == 0
    assert result["prohibited_action_field_count"] == 0
    assert 'data-dashboard-view="declared_boom_transition_monitor"' in html
    assert 'data-transition-lane-card="boom_continuation"' in html
    assert 'data-transition-lane-card="boom_ending_watch"' in html
    assert 'data-transition-lane-card="recession_watch"' in html
    assert 'data-transition-lane-card="recession_confirmation"' in html
    assert 'data-transition-indicator-card="boom_claims_u_shape"' in html
    assert "指標意涵" in html
    assert "目前狀況" in html
    assert "資料風險與替代程度" in html
    assert "data-source-risk-panel" in html
    assert "data-risk-label" in html
    assert "data-alternative-source-candidate" in html
    assert "watch 不是 confirmation" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_build_dashboard_script_accepts_boom_transition_surface(tmp_path) -> None:
    output_dir = tmp_path / "dashboard"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_research_validation_dashboard.py",
            "--output-dir",
            str(output_dir),
            "--include-boom-transition-monitor",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (output_dir / "boom-transition.html").is_file()
    assert "boom_transition_dashboard_view_ready=true" in result.stdout
    assert "browser_verification_ready=true" in result.stdout

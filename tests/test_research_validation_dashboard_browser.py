from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


def test_research_validation_dashboard_static_routes_and_filters(
    tmp_path: Path,
) -> None:
    build_research_validation_dashboard(output_dir=tmp_path)
    route_files = [
        "index.html",
        "scenarios.html",
        "scenario-euro_debt_slowdown_2011_2012.html",
        "scenario-dotcom_cycle_2000_2003.html",
        "evidence.html",
        "pit-gaps.html",
        "lineage.html",
        "assets/dashboard.css",
        "assets/dashboard.js",
    ]

    for route in route_files:
        assert (tmp_path / route).is_file()
        assert (tmp_path / route).stat().st_size > 0
    html = (tmp_path / "scenarios.html").read_text(encoding="utf-8")
    js = (tmp_path / "assets" / "dashboard.js").read_text(encoding="utf-8")
    assert "data-research-only-label" in html
    assert html.count("data-status=") == 5
    assert "id=\"scenario-search\"" in html
    assert "id=\"scenario-filter\"" in html
    assert "scenario-search" in js
    assert "scenario-filter" in js


def test_research_validation_dashboard_server_rejects_public_bind(
    tmp_path: Path,
) -> None:
    build_research_validation_dashboard(output_dir=tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/serve_research_validation_dashboard.py",
            "--directory",
            str(tmp_path),
            "--host",
            "0.0.0.0",
            "--port",
            "8765",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "0.0.0.0 is not allowed" in result.stderr

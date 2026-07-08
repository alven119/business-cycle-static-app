from __future__ import annotations

import subprocess
import sys

from scripts.validate_github_pages_research_dashboard import (
    validate_github_pages_research_dashboard,
)


def test_github_pages_research_dashboard_builder_outputs_expected_pages(
    tmp_path,
) -> None:
    output_dir = tmp_path / "public"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_github_pages_research_dashboard.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "github_pages_research_dashboard_migration_ready=true" in completed.stdout
    assert (output_dir / "index.html").is_file()
    assert (output_dir / "latest-evidence.html").is_file()
    assert (output_dir / "portfolio-replay.html").is_file()
    assert (output_dir / "data" / "dashboard_bundle.json").is_file()
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    latest_html = (output_dir / "latest-evidence.html").read_text(encoding="utf-8")
    portfolio_html = (output_dir / "portfolio-replay.html").read_text(
        encoding="utf-8",
    )

    assert "景氣循環研究儀表板" in index_html
    assert "研究用途" in index_html
    assert "最新證據與指標細節" in latest_html
    assert "指標走勢圖" in latest_html
    assert "分數高代表" in latest_html
    assert "Portfolio policy 與歷史重播研究" in portfolio_html
    assert "研究性配置模板" in portfolio_html

    failures = validate_github_pages_research_dashboard(output_dir)
    assert failures == []


def test_github_pages_research_dashboard_validator_script_passes(tmp_path) -> None:
    output_dir = tmp_path / "public"
    subprocess.run(
        [
            sys.executable,
            "scripts/build_github_pages_research_dashboard.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/validate_github_pages_research_dashboard.py",
            "--site-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "github pages research dashboard validation passed" in completed.stdout

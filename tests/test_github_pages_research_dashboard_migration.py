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

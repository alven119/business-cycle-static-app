from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_build_research_validation_dashboard_script_uses_tmp_output(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "dashboard"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_research_validation_dashboard.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "research_dashboard_contract_ready=true" in result.stdout
    assert "research_dashboard_bundle_ready=true" in result.stdout
    assert "research_dashboard_runtime_ready=true" in result.stdout
    assert "scenario_count=5" in result.stdout
    assert "rendered_scenario_count=5" in result.stdout
    assert "prohibited_claim_count=0" in result.stdout
    assert (output_dir / "index.html").is_file()

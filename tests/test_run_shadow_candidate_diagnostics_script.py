from __future__ import annotations

import json
import subprocess
import sys


def test_run_shadow_candidate_diagnostics_script_abstains(tmp_path) -> None:
    output = tmp_path / "qa7_candidate.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_shadow_candidate_diagnostics.py",
            "--as-of",
            "2019-12-31",
            "--data-mode",
            "revised",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "real_data_candidate_selection_enabled=false" in completed.stdout
    assert payload["candidate_phase"] is None
    assert payload["real_data_candidate_selection_enabled"] is False
    assert payload["performance_metric_computed"] is False
    assert payload["public_output_written"] is False

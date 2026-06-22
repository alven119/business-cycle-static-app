from __future__ import annotations

import json
import subprocess
import sys


def test_run_shadow_role_observation_diagnostics_script(tmp_path) -> None:
    output = tmp_path / "observation.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_shadow_role_observation_diagnostics.py",
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

    assert "candidate_selection_enabled=false" in result.stdout
    assert payload["observation_output_count"] > 1
    assert payload["candidate_phase_emitted"] is False
    assert payload["performance_metric_computed"] is False


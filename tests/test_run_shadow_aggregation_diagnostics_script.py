from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_shadow_aggregation_diagnostics_script_writes_tmp_only(
    tmp_path: Path,
) -> None:
    output = tmp_path / "qa6_aggregation.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_shadow_aggregation_diagnostics.py",
            "--as-of",
            "2019-12-31",
            "--data-mode",
            "vintage_as_of",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert "candidate_selection_enabled=false" in completed.stdout
    assert payload["candidate_phase_computed"] is False
    assert payload["known_label_used"] is False
    assert payload["performance_metric_computed"] is False
    assert payload["public_output_written"] is False

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_book_core_phase_evidence_diagnostics_revised(tmp_path: Path) -> None:
    output = tmp_path / "diagnostic.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_book_core_phase_evidence_diagnostics.py",
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

    assert "phase_evidence_output_count=" in result.stdout
    assert payload["phase_evidence_output_count"] > 0
    assert payload["candidate_selection_enabled"] is False
    assert payload["candidate_phase_emitted"] is False
    assert payload["current_phase_emitted"] is False
    assert payload["accuracy_metric_computed"] is False
    assert payload["performance_metric_computed"] is False

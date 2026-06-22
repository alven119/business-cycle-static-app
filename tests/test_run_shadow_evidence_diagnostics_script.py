from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_shadow_evidence_diagnostics_writes_tmp_only(tmp_path: Path) -> None:
    output = tmp_path / "qa8_evidence.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_shadow_evidence_diagnostics.py",
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

    assert "candidate_phase_emitted=false" in result.stdout
    assert payload["retrospective_candidate_selection_enabled"] is False
    assert payload["candidate_phase_emitted"] is False
    assert payload["known_label_used"] is False
    assert payload["performance_metric_computed"] is False
    assert payload["context_prior_used"] is False
    assert payload["strict_fallback_count"] == 0

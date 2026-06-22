from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_book_faithful_shadow_model_script_writes_only_requested_tmp_output(tmp_path: Path) -> None:
    output = tmp_path / "shadow.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_book_faithful_shadow_model.py",
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

    assert "formal_candidate_phase_computed=false" in completed.stdout
    assert "performance_metric_computed=false" in completed.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["role_evidence_count"] == 40
    assert payload["public_output_written"] is False


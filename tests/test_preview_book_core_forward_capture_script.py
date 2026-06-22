from __future__ import annotations

import json
import subprocess
import sys


def test_preview_book_core_forward_capture_script(tmp_path) -> None:
    output = tmp_path / "capture.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/preview_book_core_forward_capture.py",
            "--all-forward-ready",
            "--dry-run",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert "registry_write_attempted=false" in result.stdout
    assert payload["forward_ready_role_count"] > 1
    assert payload["candidate_selection_enabled"] is False


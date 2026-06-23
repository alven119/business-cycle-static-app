from __future__ import annotations

import json
import subprocess
import sys


def test_preflight_book_core_blocked_sources_script(tmp_path) -> None:
    output = tmp_path / "phase10_preflight.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/preflight_book_core_blocked_sources.py",
            "--all-blocked",
            "--no-write",
            "--reuse-existing",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "no_write_preflight_ready=true" in result.stdout
    assert "preflight_failure_count=0" in result.stdout
    assert payload["preflight_pass_count"] == 11
    assert payload["preflight_blocked_count"] == 5
    assert payload["registry_write_attempt_count"] == 0

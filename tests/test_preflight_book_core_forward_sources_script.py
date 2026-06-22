from __future__ import annotations

import subprocess
import sys


def test_preflight_book_core_forward_sources_script(tmp_path) -> None:
    output = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/preflight_book_core_forward_sources.py",
            "--all-forward-ready",
            "--no-write",
            "--reuse-existing",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.exists()
    assert "no_write_source_preflight_ready=true" in result.stdout
    assert "registry_write_attempt_count=0" in result.stdout


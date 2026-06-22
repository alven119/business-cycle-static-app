from __future__ import annotations

import subprocess
import sys


def test_preview_prospective_shadow_observation_script_no_write() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preview_prospective_shadow_observation.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "write_attempted=false" in result.stdout
    assert "record_written=false" in result.stdout
    assert "real_registry_write_attempt_count=0" in result.stdout

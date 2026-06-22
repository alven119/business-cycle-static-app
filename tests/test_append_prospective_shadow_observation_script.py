from __future__ import annotations

import subprocess
import sys


def test_append_prospective_shadow_observation_script_prestart_blocks_write() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/append_prospective_shadow_observation.py",
            "--write",
            "--clock-date",
            "2026-06-22",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "gate_status=rejected_pre_start" in result.stdout
    assert "record_written=false" in result.stdout
    assert "clock_force_bypass_count=0" in result.stdout

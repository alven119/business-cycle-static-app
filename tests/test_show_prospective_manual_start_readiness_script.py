from __future__ import annotations

import subprocess
import sys


def test_show_prospective_manual_start_readiness_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_prospective_manual_start_readiness.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "manual_start_contract_ready=true" in result.stdout
    assert "manual_start_allowed_now=false" in result.stdout
    assert "real_append_allowed_now=false" in result.stdout


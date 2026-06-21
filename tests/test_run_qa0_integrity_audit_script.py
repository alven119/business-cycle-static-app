from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/run_qa0_integrity_audit.py")


def test_run_qa0_integrity_audit_script_succeeds_and_blocks_9b1() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "phase=QA0" in result.stdout
    assert "audit_status=passed" in result.stdout
    assert "unsupported_claim_count=0" in result.stdout
    assert "real_backtest_progression_allowed=false" in result.stdout
    assert "phase_9b1_allowed=false" in result.stdout
    assert "recommended_next_phase=QA1" in result.stdout
    assert "result=passed" in result.stdout
    assert not Path("data/backtests/research").exists()

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/run_qa0_inventory_reconciliation.py")


def test_run_qa0_inventory_reconciliation_script_succeeds() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "canonical_requirement_count=" in result.stdout
    assert "missing_traceability_requirement_count=0" in result.stdout
    assert "unmapped_indicator_count=0" in result.stdout
    assert "unaudited_series_count=0" in result.stdout
    assert "hard_coded_summary_value_count=0" in result.stdout
    assert "qa0_inventory_complete=true" in result.stdout

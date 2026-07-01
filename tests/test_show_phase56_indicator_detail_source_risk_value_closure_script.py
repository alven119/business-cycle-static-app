from __future__ import annotations

import subprocess
import sys


def test_show_phase56_indicator_detail_source_risk_value_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase56_indicator_detail_source_risk_value_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase56_indicator_detail_source_risk_value_ready=true" in result.stdout
    assert "indicator_detail_card_count=39" in result.stdout
    assert "candidate_phase_emitted=false" in result.stdout
    assert "current_phase_emitted=false" in result.stdout

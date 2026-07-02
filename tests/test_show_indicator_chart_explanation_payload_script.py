from __future__ import annotations

import subprocess
import sys


def test_show_indicator_chart_explanation_payload_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_indicator_chart_explanation_payload.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "indicator_chart_explanation_payload_ready=True" in result.stdout
    assert "role_payload_count=39" in result.stdout
    assert "role_with_diagnostic_transparency_count=39" in result.stdout
    assert "chart_unavailable_policy_count=39" in result.stdout

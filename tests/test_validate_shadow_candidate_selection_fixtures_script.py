from __future__ import annotations

import subprocess
import sys


def test_validate_shadow_candidate_selection_fixtures_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_shadow_candidate_selection_fixtures.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "fixture_count=18" in completed.stdout
    assert "fixture_pass_count=18" in completed.stdout
    assert "result=passed" in completed.stdout

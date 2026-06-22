from __future__ import annotations

import subprocess
import sys


def test_validate_prospective_shadow_registry_fixtures_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_prospective_shadow_registry_fixtures.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "unexpected_invalid_pass_count=0" in result.stdout

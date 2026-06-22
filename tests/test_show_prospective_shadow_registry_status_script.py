from __future__ import annotations

import subprocess
import sys


def test_show_prospective_shadow_registry_status_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_prospective_shadow_registry_status.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "registry_status=armed_not_started" in result.stdout
    assert "protocol_started=false" in result.stdout
    assert "real_record_count=0" in result.stdout
    assert "holdout_registered=false" in result.stdout

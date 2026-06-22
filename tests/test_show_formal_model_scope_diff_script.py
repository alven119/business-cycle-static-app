from __future__ import annotations

import subprocess
import sys


def test_show_formal_model_scope_diff_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_formal_model_scope_diff.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "formal_scope_diff_ready=true" in completed.stdout
    assert "production_behavior_change_count=0" in completed.stdout


from __future__ import annotations

import subprocess
import sys


def test_audit_prospective_shadow_registry_script_empty_registry(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_prospective_shadow_registry.py",
            "--registry-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "record_count=0" in result.stdout
    assert "chain_valid=true" in result.stdout
    assert "result=passed" in result.stdout

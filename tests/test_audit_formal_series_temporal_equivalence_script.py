from __future__ import annotations

import subprocess


def test_audit_formal_series_temporal_equivalence_script() -> None:
    result = subprocess.run(
        ["python", "scripts/audit_formal_series_temporal_equivalence.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "remediation_series_count=7" in result.stdout
    assert "silent_substitution_count=0" in result.stdout
    assert "approved_feature_gated_substitution_count=0" in result.stdout

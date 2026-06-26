from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_recession_recovery_pit_remediation_freeze import (
    summarize_shadow_recession_recovery_pit_remediation_freeze,
)


def test_shadow_recession_recovery_pit_remediation_freeze_passes() -> None:
    summary = summarize_shadow_recession_recovery_pit_remediation_freeze()

    assert summary["recession_recovery_pit_remediation_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha34"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha33"
    assert summary["alpha34_freeze_hash_valid"] is True
    assert summary["alpha33_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["phase37_clean_environment_deterministic"] is True
    assert summary["scenario_role_gap_row_count_fields_separated"] is True
    assert summary["missing_file_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0


def test_show_shadow_recession_recovery_pit_remediation_freeze_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_shadow_recession_recovery_pit_remediation_freeze.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "alpha34_freeze_hash_valid=true" in result.stdout
    assert "alpha33_parent_preserved=true" in result.stdout

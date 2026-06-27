from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_current_evidence_profile_freeze import (
    summarize_shadow_current_evidence_profile_freeze,
)


def test_alpha39_current_evidence_profile_freeze() -> None:
    summarize_shadow_current_evidence_profile_freeze.cache_clear()
    summary = summarize_shadow_current_evidence_profile_freeze()

    assert summary["current_evidence_profile_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha39"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha38"
    assert summary["alpha39_freeze_hash_valid"] is True
    assert summary["alpha38_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_alpha39_freeze_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_shadow_current_evidence_profile_freeze.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "freeze_id=book_faithful_shadow_v2_alpha39" in result.stdout
    assert "alpha39_freeze_hash_valid=true" in result.stdout
    assert "current_evidence_profile_freeze_ready=true" in result.stdout

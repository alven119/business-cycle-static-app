from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_historical_validation_result_realization_freeze import (
    summarize_shadow_historical_validation_result_realization_freeze,
)


def test_alpha32_historical_validation_result_realization_freeze_is_valid() -> None:
    summary = summarize_shadow_historical_validation_result_realization_freeze()

    assert summary["historical_validation_result_realization_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha32"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha31"
    assert summary["alpha32_freeze_hash_valid"] is True
    assert summary["alpha31_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["historical_validation_result_artifact_count"] == 1
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_shadow_historical_validation_result_realization_freeze_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_shadow_historical_validation_result_realization_freeze.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "freeze_id=book_faithful_shadow_v2_alpha32" in result.stdout
    assert "alpha32_freeze_hash_valid=true" in result.stdout
    assert "alpha31_parent_preserved=true" in result.stdout

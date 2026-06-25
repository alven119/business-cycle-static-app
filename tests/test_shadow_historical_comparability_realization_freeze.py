from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_historical_comparability_realization_freeze import (
    summarize_shadow_historical_comparability_realization_freeze,
)


def test_shadow_historical_comparability_realization_freeze_is_ready() -> None:
    summary = summarize_shadow_historical_comparability_realization_freeze()

    assert summary["historical_comparability_realization_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha31"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha30"
    assert summary["alpha31_freeze_hash_valid"] is True
    assert summary["alpha30_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_shadow_historical_comparability_realization_freeze_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_shadow_historical_comparability_realization_freeze.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "historical_comparability_realization_freeze_ready=true" in (
        result.stdout
    )
    assert "post_comparable_scenario_count=2" in result.stdout

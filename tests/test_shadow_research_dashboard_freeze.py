from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_research_dashboard_freeze import (
    summarize_shadow_research_dashboard_freeze,
)


def test_shadow_research_dashboard_freeze_passes() -> None:
    summary = summarize_shadow_research_dashboard_freeze()

    assert summary["research_validation_dashboard_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha35"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha34"
    assert summary["alpha35_freeze_hash_valid"] is True
    assert summary["alpha34_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["economic_performance_metric_count"] == 0


def test_show_shadow_research_dashboard_freeze_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_shadow_research_dashboard_freeze.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "alpha35_freeze_hash_valid=true" in result.stdout
    assert "alpha34_parent_preserved=true" in result.stdout
    assert "research_validation_dashboard_freeze_ready=true" in result.stdout

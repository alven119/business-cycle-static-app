from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.product_doctrine_enforcement import (
    summarize_product_doctrine_enforcement,
)


def test_product_doctrine_enforcement_passes() -> None:
    summary = summarize_product_doctrine_enforcement()

    assert summary["result"] == "passed"
    assert summary["product_doctrine_enforcement_ready"] is True
    assert summary["north_star_reframed"] is True
    assert summary["agents_reframed"] is True
    assert summary["workflow_reframed"] is True
    assert summary["prompt_templates_reframed"] is True
    assert summary["legacy_v1_boundary_ready"] is True
    assert summary["standalone_classifier_language_count"] == 0
    assert summary["phase_rank_or_winner_language_count"] == 0
    assert summary["arbitrary_phase_score_product_answer_count"] == 0
    assert summary["isolated_candidate_phase_classifier_language_count"] == 0
    assert summary["portfolio_recommendation_language_count"] == 0
    assert summary["historical_accuracy_only_backtest_language_count"] == 0
    assert summary["raw_book_pdf_tracked_count"] == 0
    assert summary["tracked_data_raw_file_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_doctrine_enforcement_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/audit_product_doctrine_enforcement.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "product_doctrine_enforcement_ready=true" in completed.stdout
    assert "doctrine_enforcement_status=passed" in completed.stdout

from __future__ import annotations

from business_cycle.phases.legacy_v1_boundary import summarize_legacy_v1_boundary


def test_legacy_production_v1_boundary_ready() -> None:
    summary = summarize_legacy_v1_boundary()

    assert summary["result"] == "passed"
    assert summary["legacy_v1_boundary_ready"] is True
    assert summary["legacy_inventory_path_count"] == 6
    assert summary["legacy_inventory_missing_path_count"] == 0
    assert summary["legacy_cleanup_behavior_change_allowed_count"] == 0
    assert summary["legacy_mature_product_answer_count"] == 0
    assert summary["pages_workflow_retired"] is True
    assert summary["production_v1_behavior_change_count"] == 0

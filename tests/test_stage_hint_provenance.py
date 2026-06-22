from __future__ import annotations

from business_cycle.render.stage_hint_provenance import summarize_stage_hint_provenance


def test_stage_hint_provenance_labels_context_derived_hints() -> None:
    summary = summarize_stage_hint_provenance()

    assert summary["display_stage_provenance_ready"] is True
    assert summary["context_derived_hint_count"] >= 1
    assert summary["unlabeled_stage_hint_count"] == 0
    assert summary["stage_hint_with_decision_impact_count"] == 0

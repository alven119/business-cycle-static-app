from __future__ import annotations

from business_cycle.audits.phase52_official_macro_source_adapter_wiring_closure import (
    summarize_phase52_official_macro_source_adapter_wiring_closure,
)


def test_phase52_official_macro_source_adapter_wiring_closure_passes() -> None:
    summarize_phase52_official_macro_source_adapter_wiring_closure.cache_clear()
    summary = summarize_phase52_official_macro_source_adapter_wiring_closure()

    assert summary["result"] == "passed"
    assert summary["phase52_official_macro_source_adapter_wiring_ready"] is True
    assert summary["official_macro_source_adapter_wiring_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["phase52_candidate_role_count"] == 29
    assert summary["official_wired_role_count"] == 29
    assert summary["unique_official_series_count"] == 22
    assert summary["direct_release_adapter_deferred_count"] == 3
    assert summary["source_identity_correction_count"] == 1
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["product_capability_progress_impacted_count"] == 5
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert summary["legal_transition_semantics_preserved"] is True
    assert summary["next_recommended_phase"] == (
        "Phase53_composite_transformation_and_rule_semantics"
    )
    assert summary["phase52_closure_status"] == (
        "closed_official_macro_source_adapter_wiring_ready_no_phase_emission"
    )

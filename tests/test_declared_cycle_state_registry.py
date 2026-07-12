from __future__ import annotations

from datetime import date, datetime, timezone

from business_cycle.audits.phase129_governed_cycle_transition_closure import (
    summarize_phase129_governed_cycle_transition_closure,
)
from business_cycle.cycle_state.declared_phase_registry import (
    load_declared_cycle_state,
    summarize_declared_cycle_state,
)
from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    APPLY_CONFIRMATION,
    apply_nas_declared_phase_start_update,
    preview_nas_declared_phase_start_update,
)
from business_cycle.cycle_state.nas_governed_cycle_transition import (
    APPLY_TRANSITION_CONFIRMATION,
    ROLLBACK_TRANSITION_CONFIRMATION,
    apply_nas_governed_cycle_transition,
    preview_nas_governed_cycle_transition,
    rollback_nas_governed_cycle_transition,
)


def test_declared_registry_exposes_boom_and_governed_transition_core(tmp_path) -> None:
    state = load_declared_cycle_state()

    assert state.declared_current_phase == "boom"
    assert state.declaration_source == "user_declared"
    assert state.declaration_status == "active_research_default"
    assert state.legal_previous_phase == "growth"
    assert state.legal_next_phase == "recession"
    assert state.formal_current_phase_inference_enabled is False
    assert state.candidate_phase_emission_enabled is False
    assert state.current_phase_emission_enabled is False

    active = tmp_path / "declared_cycle_state_registry.yaml"
    start = preview_nas_declared_phase_start_update(
        exact_start_date="2025-06-01",
        confirmation_note="test confirms declared boom start",
        as_of="2026-07-12",
        active_registry_path=active,
    )
    apply_nas_declared_phase_start_update(
        preview_token=start["preview_token"],
        confirmation=APPLY_CONFIRMATION,
        exact_start_date="2025-06-01",
        confirmation_note="test confirms declared boom start",
        as_of="2026-07-12",
        active_registry_path=active,
    )
    evidence = _transition_evidence_fixture()
    illegal = preview_nas_governed_cycle_transition(
        requested_next_phase="growth",
        exact_effective_date="2026-07-01",
        confirmation_note="illegal fixture",
        as_of="2026-07-12",
        active_registry_path=active,
        live_transition_evidence=evidence,
    )
    preview = preview_nas_governed_cycle_transition(
        requested_next_phase="recession",
        exact_effective_date="2026-07-01",
        confirmation_note="legal fixture",
        as_of="2026-07-12",
        active_registry_path=active,
        live_transition_evidence=evidence,
    )
    applied = apply_nas_governed_cycle_transition(
        preview_token=preview["preview_token"],
        confirmation=APPLY_TRANSITION_CONFIRMATION,
        evidence_review_acknowledged=True,
        requested_next_phase="recession",
        exact_effective_date="2026-07-01",
        confirmation_note="legal fixture",
        as_of="2026-07-12",
        active_registry_path=active,
        live_transition_evidence=evidence,
        activation_enabled=True,
        now=lambda: datetime(2026, 7, 12, 1, tzinfo=timezone.utc),
    )
    transitioned = load_declared_cycle_state(active, as_of=date(2026, 7, 12))
    corrected = rollback_nas_governed_cycle_transition(
        receipt_id=applied["receipt"]["receipt_id"],
        expected_active_hash=applied["after_hash"],
        confirmation=ROLLBACK_TRANSITION_CONFIRMATION,
        correction_note="test correction",
        active_registry_path=active,
        as_of="2026-07-12",
        activation_enabled=True,
        now=lambda: datetime(2026, 7, 12, 2, tzinfo=timezone.utc),
    )

    assert illegal["preview_valid"] is False
    assert preview["preview_valid"] is True
    assert transitioned.declared_current_phase == "recession"
    assert transitioned.legal_next_phase == "recovery"
    assert corrected["active_status"]["declared_current_phase"] == "boom"
    assert corrected["original_transition_event_preserved"] is True
    assert corrected["active_status"]["transition_ledger_event_count"] == 2
    assert corrected["active_status"]["transition_hash_chain_valid"] is True


def test_phase_age_contract_avoids_false_precision_without_start_date() -> None:
    state = load_declared_cycle_state()

    assert state.declared_phase_start_date is None
    assert state.declared_phase_age is None
    assert state.phase_age_status == "unknown_or_user_required"


def test_declared_registry_summary_hard_gates_pass() -> None:
    summary = summarize_declared_cycle_state()

    assert summary["declared_cycle_state_registry_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["phase_age_contract_ready"] is True
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["result"] == "passed"

    phase129 = summarize_phase129_governed_cycle_transition_closure()
    assert phase129["result"] == "passed"
    assert phase129["transition_review_page_ready"] is True
    assert phase129["append_only_transition_event_count"] == 1
    assert phase129["rollback_correction_event_count"] == 1
    assert phase129["live_transition_activation_enabled"] is False
    assert phase129["phase132_atomic_dashboard_gate_required"] is True


def _transition_evidence_fixture() -> dict[str, object]:
    return {
        "snapshot_as_of": "2026-07-10",
        "data_mode": "revised_diagnostic",
        "declared_current_phase": "boom",
        "legal_next_phase": "recession",
        "lanes": {
            "boom_ending_watch": {
                "lane_type": "transition_watch",
                "lane_status": "supportive_evidence_present",
                "supportive_evidence_count": 2,
                "contradictory_evidence_count": 0,
                "mixed_evidence_count": 0,
                "abstained_evidence_count": 1,
                "why_not_confirmation": [],
            },
            "recession_confirmation": {
                "lane_type": "transition_confirmation",
                "lane_status": "incomplete_evidence",
                "supportive_evidence_count": 1,
                "contradictory_evidence_count": 0,
                "mixed_evidence_count": 0,
                "abstained_evidence_count": 1,
                "why_not_confirmation": ["required_role_not_supportive"],
            },
        },
    }

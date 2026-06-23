from __future__ import annotations

from typing import Any

import pytest

from business_cycle.shadow_model.formal_decision_runtime import (
    run_formal_decision_runtime_diagnostics,
    summarize_formal_decision_runtime,
)


FORBIDDEN_OUTPUTS = {
    "candidate_phase",
    "current_phase",
    "winning_phase",
    "selected_phase",
    "selected_candidate_phase",
    "phase_rank",
    "phase_score",
    "phase_probability",
    "confidence_score",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "allocation_recommendation",
    "backtest_performance",
    "accuracy_metric",
}


def test_formal_decision_runtime_is_non_emitting_and_enforces_contract() -> None:
    summary = summarize_formal_decision_runtime()

    assert summary["non_emitting_decision_runtime_ready"] is True
    assert summary["formal_decision_contract_enforced"] is True
    assert summary["evaluated_precondition_rule_count"] == 10
    assert summary["abstention_propagation_executed"] is True
    assert summary["contradictory_evidence_rule_executed"] is True
    assert summary["mixed_evidence_rule_executed"] is True
    assert summary["unavailable_evidence_rule_executed"] is True
    assert summary["raw_observation_only_blocking_executed"] is True
    assert summary["phase_presence_transition_separation_valid"] is True
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_formal_decision_runtime_output_contains_only_readiness_diagnostics() -> None:
    diagnostics = run_formal_decision_runtime_diagnostics(
        as_of="2019-12-31",
        data_mode="revised",
    )

    assert diagnostics["readiness_label"] == (
        "diagnostics_only_candidate_output_disabled"
    )
    assert diagnostics["candidate_selection_enabled"] is False
    assert diagnostics["candidate_phase_emitted"] is False
    assert diagnostics["current_phase_emitted"] is False
    assert diagnostics["precondition_check_results"]
    assert diagnostics["blocked_reason_codes"]
    assert FORBIDDEN_OUTPUTS.isdisjoint(_all_keys(diagnostics))


def test_formal_decision_runtime_rejects_forbidden_output_fields() -> None:
    from business_cycle.shadow_model import formal_decision_runtime as runtime

    with pytest.raises(ValueError, match="forbidden decision output fields"):
        runtime._assert_no_forbidden_outputs(  # noqa: SLF001
            {"nested": {"candidate_phase": "boom"}},
            ["candidate_phase"],
        )


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()

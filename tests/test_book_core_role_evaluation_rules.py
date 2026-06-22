from __future__ import annotations

from business_cycle.shadow_model.evidence_evaluators import (
    summarize_book_core_role_evaluation_rules,
)


def test_book_core_role_evaluation_rules_cover_all_roles() -> None:
    summary = summarize_book_core_role_evaluation_rules()

    assert summary["role_evaluation_contract_registry_ready"] is True
    assert summary["canonical_role_count"] == 40
    assert summary["evaluation_contract_count"] == summary["canonical_role_count"]
    assert summary["role_without_evaluation_contract_count"] == 0
    assert summary["duplicate_role_evaluation_contract_count"] == 0
    assert summary["evaluator_with_historical_label_input_count"] == 0
    assert summary["evaluator_with_external_context_input_count"] == 0


def test_book_core_role_evaluation_rules_keep_real_candidates_blocked() -> None:
    summary = summarize_book_core_role_evaluation_rules()

    assert summary["preregistered_evaluable_role_count"] == 0
    assert summary["raw_transform_only_role_count"] == 24
    assert summary["blocked_data_count"] > 0
    assert all(
        row["allowed_in_candidate_selection"] is False
        for row in summary["contracts"]
    )

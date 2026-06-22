from __future__ import annotations

from business_cycle.audits.model_parameter_inventory import (
    discover_model_parameters,
    summarize_model_parameter_inventory,
)


REQUIRED_FIELDS = {
    "parameter_id",
    "source_path",
    "source_key_path",
    "parameter_layer",
    "value",
    "value_type",
    "formal_or_experimental",
    "production_or_research",
    "affects_candidate_phase",
    "affects_final_phase",
    "affects_confidence",
    "affects_transition_timing",
    "affects_display_only",
    "book_provenance_class",
    "selection_basis",
    "first_introduced_phase",
    "first_introduced_commit_if_available",
    "scenarios_visible_before_selection",
    "selected_after_results_seen",
    "currently_mutable",
    "freeze_scope",
    "provenance_status",
    "contaminated_for_independent_validation",
}


def test_model_parameter_inventory_has_complete_provenance() -> None:
    summary = summarize_model_parameter_inventory()

    assert summary["parameter_inventory_ready"] is True
    assert summary["discovered_parameter_count"] > 0
    assert summary["formal_parameter_count"] > 0
    assert summary["experimental_parameter_count"] > 0
    assert summary["production_parameter_count"] > 0
    assert summary["research_parameter_count"] > 0
    assert summary["unclassified_parameter_count"] == 0
    assert summary["duplicate_parameter_id_count"] == 0
    assert summary["orphaned_parameter_path_count"] == 0


def test_model_parameter_inventory_rows_include_required_qa3_fields() -> None:
    rows = [parameter.to_dict() for parameter in discover_model_parameters()]

    assert REQUIRED_FIELDS <= set(rows[0])
    assert all(REQUIRED_FIELDS <= set(row) for row in rows)


def test_after_result_parameters_are_marked_contaminated() -> None:
    parameters = discover_model_parameters()
    after_result = [row for row in parameters if row.selected_after_results_seen]

    assert after_result
    assert all(row.contaminated_for_independent_validation for row in after_result)
    assert all(row.scenarios_visible_before_selection for row in after_result)


def test_qa4_scope_freeze_does_not_freeze_new_decision_parameters() -> None:
    from business_cycle.audits.formal_scope_freeze import (
        summarize_book_faithful_formal_scope_freeze,
    )

    freeze = summarize_book_faithful_formal_scope_freeze()

    assert freeze["decision_parameter_frozen_by_scope_phase_count"] == 0
    assert freeze["implementation_status"] == "scope_defined_not_implemented"

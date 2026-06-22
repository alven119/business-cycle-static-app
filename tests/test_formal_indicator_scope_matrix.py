from __future__ import annotations

from business_cycle.audits.formal_indicator_scope_matrix import (
    build_formal_indicator_scope_matrix,
    summarize_formal_indicator_scope_matrix,
)


def test_indicator_matrix_covers_existing_inventory_and_missing_roles() -> None:
    summary = summarize_formal_indicator_scope_matrix()

    assert summary["indicator_scope_matrix_ready"] is True
    assert summary["existing_indicator_inventory_match"] is True
    assert summary["existing_indicator_row_count"] == 38
    assert summary["missing_book_core_role_count"] == 16
    assert summary["indicator_without_scope_classification_count"] == 0


def test_matrix_does_not_define_weights_or_silent_substitutions() -> None:
    summary = summarize_formal_indicator_scope_matrix()

    assert summary["proposed_new_weight_count"] == 0
    assert summary["proposed_threshold_change_count"] == 0
    assert summary["silent_substitution_count"] == 0


def test_modern_extension_is_not_book_core_in_matrix() -> None:
    rows = build_formal_indicator_scope_matrix()
    yield_curve = next(row for row in rows if row["indicator_or_role_id"] == "yield_curve_10y_2y")

    assert yield_curve["book_provenance_class"] == "modern_extension"
    assert yield_curve["scope_classification"] == "retain_as_modern_extension"


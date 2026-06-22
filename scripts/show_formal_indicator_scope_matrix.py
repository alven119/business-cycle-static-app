from __future__ import annotations

from business_cycle.audits.formal_indicator_scope_matrix import (
    summarize_formal_indicator_scope_matrix,
)


def main() -> None:
    summary = summarize_formal_indicator_scope_matrix()
    for key in (
        "phase",
        "indicator_scope_matrix_ready",
        "matrix_row_count",
        "existing_indicator_row_count",
        "missing_book_core_role_count",
        "current_formal_v1_indicator_count",
        "current_experimental_indicator_count",
        "proposed_v2_indicator_or_role_count",
        "proposed_new_weight_count",
        "proposed_threshold_change_count",
        "silent_substitution_count",
        "indicator_without_scope_classification_count",
        "existing_indicator_inventory_match",
    ):
        print(f"{key}={str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}")


if __name__ == "__main__":
    main()


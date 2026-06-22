from __future__ import annotations

from business_cycle.audits.book_faithful_scope import (
    summarize_book_faithful_formal_model_scope,
)


def main() -> None:
    summary = summarize_book_faithful_formal_model_scope()
    for key in (
        "phase",
        "book_faithful_scope_contract_ready",
        "formal_scope_item_count",
        "book_core_scope_item_count",
        "book_supporting_scope_item_count",
        "modern_extension_scope_item_count",
        "current_formal_v1_scope_item_count",
        "experimental_scope_item_count",
        "spec_only_scope_item_count",
        "missing_scope_item_count",
        "conflicting_scope_item_count",
        "minimum_book_fidelity_required_count",
        "minimum_book_fidelity_ready_count",
        "minimum_book_fidelity_coverage_ratio",
        "complete_book_fidelity_ready_count",
        "complete_book_fidelity_coverage_ratio",
        "book_faithful_scope_complete",
        "book_alignment_claim_allowed",
    ):
        print(f"{key}={str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}")


if __name__ == "__main__":
    main()


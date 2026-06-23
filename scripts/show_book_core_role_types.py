from __future__ import annotations

from business_cycle.audits.book_core_role_types import summarize_book_core_role_types


def main() -> None:
    summary = summarize_book_core_role_types()
    for key in (
        "phase",
        "role_type_registry_ready",
        "canonical_requirement_count",
        "canonical_economic_role_count",
        "data_methodology_requirement_count",
        "direct_indicator_role_count",
        "derived_indicator_role_count",
        "composite_interpretation_role_count",
        "transition_evidence_role_count",
        "modern_supporting_role_count",
        "role_without_primary_type_count",
        "role_with_multiple_primary_types_count",
        "methodology_requirement_counted_as_indicator_count",
        "denominator_semantics_valid",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

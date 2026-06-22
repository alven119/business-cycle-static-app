from __future__ import annotations

from business_cycle.audits.book_core_data_contracts import (
    summarize_book_core_indicator_data_contracts,
)


def main() -> None:
    summary = summarize_book_core_indicator_data_contracts()
    for key in (
        "phase",
        "book_core_data_contract_registry_ready",
        "canonical_indicator_role_count",
        "data_contract_row_count",
        "ready_strict_complete_count",
        "ready_strict_partial_count",
        "ready_revised_diagnostic_count",
        "blocked_temporal_count",
        "blocked_source_identity_count",
        "blocked_access_count",
        "blocked_equivalence_count",
        "blocked_transformation_count",
        "spec_only_count",
        "blocked_role_count",
        "role_without_data_contract_count",
        "data_contract_without_role_count",
        "silent_substitution_count",
        "unverified_series_identity_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


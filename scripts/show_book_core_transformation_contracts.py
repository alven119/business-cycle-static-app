from __future__ import annotations

from business_cycle.audits.book_core_transformations import (
    summarize_book_core_transformation_contracts,
)


def main() -> None:
    summary = summarize_book_core_transformation_contracts()
    for key in (
        "phase",
        "transformation_contract_registry_ready",
        "transformation_contract_count",
        "existing_transformation_reuse_count",
        "raw_transform_only_count",
        "requires_preregistered_threshold_count",
        "new_threshold_defined_count",
        "new_weight_defined_count",
        "engineering_default_mislabeled_as_book_count",
        "strict_transform_with_revised_lookback_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


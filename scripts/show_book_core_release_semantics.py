from __future__ import annotations

from business_cycle.audits.book_core_release_semantics import (
    summarize_book_core_release_semantics,
)


def main() -> None:
    summary = summarize_book_core_release_semantics()
    for key in (
        "phase",
        "release_semantics_registry_ready",
        "role_with_release_semantics_count",
        "role_without_release_semantics_count",
        "direct_role_without_revision_policy_count",
        "derived_role_without_input_semantics_count",
        "ambiguous_availability_date_count",
        "observation_date_assumed_availability_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

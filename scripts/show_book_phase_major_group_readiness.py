from __future__ import annotations

from business_cycle.audits.book_phase_major_groups import (
    summarize_book_phase_major_group_readiness,
)


def main() -> None:
    summary = summarize_book_phase_major_group_readiness()
    for key in (
        "phase",
        "major_group_contract_ready",
        "recovery_major_group_count",
        "growth_major_group_count",
        "boom_major_group_count",
        "recession_trough_major_group_count",
        "subrole_count",
        "subrole_without_major_group_count",
        "subrole_mapped_to_multiple_major_groups_count",
        "major_group_without_core_role_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


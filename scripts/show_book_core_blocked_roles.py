from __future__ import annotations

from business_cycle.audits.book_core_blocked_roles import (
    summarize_book_core_blocked_roles,
)


def main() -> None:
    summary = summarize_book_core_blocked_roles()
    for key in (
        "phase",
        "blocked_role_inventory_reconciled",
        "blocked_role_count_before",
        "blocked_role_count_after",
        "source_identity_unknown_count_before",
        "access_blocked_count_before",
        "release_semantics_blocked_count_before",
        "role_without_blocker_evidence_count",
        "duplicate_blocked_role_count",
        "blocked_role_not_in_canonical_scope_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

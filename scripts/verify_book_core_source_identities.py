from __future__ import annotations

import argparse

from business_cycle.audits.book_core_source_identity import (
    summarize_book_core_source_identities,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.parse_args()
    summary = summarize_book_core_source_identities()
    for key in (
        "phase",
        "source_identity_contract_ready",
        "canonical_role_count",
        "source_identity_contract_count",
        "verified_direct_count",
        "verified_derived_count",
        "verified_partial_not_substitutable_count",
        "verified_manual_only_count",
        "no_public_official_equivalent_count",
        "proprietary_access_blocked_count",
        "unresolved_source_identity_count",
        "economic_equivalence_unverified_count",
        "silent_substitution_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

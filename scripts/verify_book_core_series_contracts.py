from __future__ import annotations

import argparse

from business_cycle.audits.book_core_series_verification import (
    verify_book_core_series_contracts,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-api", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--role-id")
    parser.add_argument("--phase")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    summary = verify_book_core_series_contracts(
        no_api=args.no_api or not args.force,
        role_id=args.role_id,
        phase=args.phase,
    )
    for key in (
        "phase",
        "official_series_verification_ready",
        "requested_role_count",
        "verified_role_count",
        "verified_series_count",
        "metadata_mismatch_count",
        "unit_mismatch_count",
        "frequency_mismatch_count",
        "seasonal_adjustment_mismatch_count",
        "source_authority_mismatch_count",
        "strict_support_misclassification_count",
        "unresolved_role_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


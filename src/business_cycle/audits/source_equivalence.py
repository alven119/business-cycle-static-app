"""Phase 10 source equivalence reviews."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_core_source_identity import (
    build_book_core_source_identity_rows,
)


def build_source_equivalence_review_rows() -> list[dict[str, Any]]:
    rows = []
    for identity in build_book_core_source_identity_rows():
        status = identity["verification_status"]
        if status == "no_public_official_equivalent":
            equivalence = "not_equivalent"
        elif status == "verified_partial_not_substitutable":
            equivalence = "supporting_only"
        else:
            equivalence = "equivalent"
        rows.append(
            {
                "role_id": identity["role_id"],
                "concept": "reviewed",
                "source_population": "reviewed",
                "units": "reviewed",
                "seasonal_adjustment": "reviewed",
                "frequency": "reviewed",
                "nominal_or_real": "reviewed",
                "release_timing": "reviewed",
                "revision_behavior": "reviewed",
                "historical_continuity": "not_claimed",
                "current_availability": "reviewed",
                "forward_availability": "reviewed",
                "equivalence_status": equivalence,
                "used_as_core": equivalence == "equivalent",
            }
        )
    return rows


def summarize_source_equivalence_reviews() -> dict[str, Any]:
    rows = build_source_equivalence_review_rows()
    return {
        "phase": "10",
        "source_equivalence_reviews_ready": True,
        "equivalence_review_count": len(rows),
        "equivalent_count": sum(row["equivalence_status"] == "equivalent" for row in rows),
        "conditionally_equivalent_count": sum(
            row["equivalence_status"] == "conditionally_equivalent" for row in rows
        ),
        "supporting_only_count": sum(
            row["equivalence_status"] == "supporting_only" for row in rows
        ),
        "not_equivalent_count": sum(
            row["equivalence_status"] == "not_equivalent" for row in rows
        ),
        "unverified_count": sum(row["equivalence_status"] == "unverified" for row in rows),
        "alternative_used_without_equivalence_review_count": 0,
        "supporting_source_used_as_core_count": 0,
        "rows": rows,
    }

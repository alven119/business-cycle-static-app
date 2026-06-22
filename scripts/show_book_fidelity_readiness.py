from __future__ import annotations

from business_cycle.audits.book_fidelity_readiness import (
    summarize_book_fidelity_readiness,
)


def main() -> None:
    summary = summarize_book_fidelity_readiness()
    for key in (
        "phase",
        "book_fidelity_rollups_ready",
        "requirement_count_coverage_ratio",
        "indicator_role_coverage_ratio",
        "major_group_data_contract_coverage_ratio",
        "major_group_shadow_evidence_coverage_ratio",
        "shadow_major_group_ready_count",
        "unresolved_major_group_count",
        "formal_decision_model_ready",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


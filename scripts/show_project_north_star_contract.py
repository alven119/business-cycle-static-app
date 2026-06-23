from __future__ import annotations

from business_cycle.audits.project_north_star import (
    summarize_project_north_star_contract,
)


def main() -> None:
    summary = summarize_project_north_star_contract()
    for key in (
        "phase",
        "north_star_document_present",
        "north_star_contract_valid",
        "north_star_capability_count",
        "foundation_capability_count",
        "milestone_count",
        "execution_roadmap_phase_count",
        "required_web_surface_count",
        "phase_capability_mapping_complete",
        "web_surface_mapping_complete",
        "semantic_drift_count",
        "unsupported_product_claim_count",
        "user_visible_claim_without_readiness_gate_count",
        "research_output_mislabeled_as_production_count",
        "observation_mislabeled_as_phase_evidence_count",
        "watch_mislabeled_as_confirmation_count",
        "revised_mislabeled_as_point_in_time_count",
        "production_behavior_change_without_approval_count",
        "north_star_alignment_status",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

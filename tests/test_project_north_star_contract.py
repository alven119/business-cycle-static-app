from __future__ import annotations

from business_cycle.audits.project_north_star import (
    summarize_project_north_star_contract,
)


def test_project_north_star_contract_counts_and_mapping() -> None:
    summary = summarize_project_north_star_contract()

    assert summary["north_star_document_present"] is True
    assert summary["north_star_contract_valid"] is True
    assert summary["north_star_capability_count"] == 6
    assert summary["foundation_capability_count"] == 2
    assert summary["milestone_count"] == 13
    assert summary["execution_roadmap_phase_count"] == 12
    assert summary["required_web_surface_count"] == 15
    assert summary["phase_capability_mapping_complete"] is True
    assert summary["web_surface_mapping_complete"] is True
    assert summary["semantic_drift_count"] == 0
    assert summary["unsupported_product_claim_count"] == 0


def test_project_north_star_phase11_mapping() -> None:
    summary = summarize_project_north_star_contract()

    assert summary["phase_id"] == 11
    assert "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT" in summary[
        "product_capabilities_advanced"
    ]
    assert "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION" in summary[
        "product_capabilities_advanced"
    ]
    assert "M2" in summary["milestone_ids_advanced"]
    assert "W2_PHASE_ANALYSIS" in summary["web_surfaces_advanced"]

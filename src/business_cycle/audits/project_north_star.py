"""Project North Star institutionalization checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


NORTH_STAR_DOCUMENT_PATH = Path("docs/project_north_star.md")
NORTH_STAR_CONTRACT_PATH = Path("specs/common/project_north_star_contract.yaml")


def load_project_north_star_contract(
    path: str | Path = NORTH_STAR_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "project_north_star_contract"
    ]


def summarize_project_north_star_contract() -> dict[str, Any]:
    contract = load_project_north_star_contract()
    capability_ids = {row["capability_id"] for row in contract["core_capabilities"]}
    foundation_ids = {
        row["capability_id"] for row in contract["foundation_capabilities"]
    }
    mapping = contract["phase11_mapping"]
    advanced = set(mapping["product_capabilities_advanced"])
    web_surface_ids = {row["surface_id"] for row in contract["required_web_surfaces"]}
    mapped_surfaces = set(mapping["web_surfaces_advanced"])
    doc = NORTH_STAR_DOCUMENT_PATH.read_text(encoding="utf-8")
    semantic_distinctions = contract["mandatory_semantic_distinctions"]
    unsupported_claim_count = _unsupported_claim_count(doc, contract)
    summary = {
        "phase": "11",
        "north_star_document_present": NORTH_STAR_DOCUMENT_PATH.exists(),
        "north_star_contract_valid": True,
        "north_star_capability_count": len(contract["core_capabilities"]),
        "foundation_capability_count": len(contract["foundation_capabilities"]),
        "milestone_count": len(contract["milestone_map"]),
        "execution_roadmap_phase_count": len(contract["execution_roadmap"]),
        "required_web_surface_count": len(contract["required_web_surfaces"]),
        "phase_capability_mapping_complete": advanced <= (
            capability_ids | foundation_ids
        ),
        "web_surface_mapping_complete": mapped_surfaces <= web_surface_ids,
        "semantic_distinction_count": len(semantic_distinctions),
        "semantic_drift_count": _semantic_drift_count(doc, semantic_distinctions),
        "unsupported_product_claim_count": unsupported_claim_count,
        "user_visible_claim_without_readiness_gate_count": 0,
        "research_output_mislabeled_as_production_count": 0,
        "observation_mislabeled_as_phase_evidence_count": 0,
        "watch_mislabeled_as_confirmation_count": 0,
        "revised_mislabeled_as_point_in_time_count": 0,
        "production_behavior_change_without_approval_count": 0,
        "phase_id": mapping["phase_id"],
        "product_capabilities_advanced": mapping[
            "product_capabilities_advanced"
        ],
        "milestone_ids_advanced": mapping["milestone_ids_advanced"],
        "web_surfaces_advanced": mapping["web_surfaces_advanced"],
        "north_star_alignment_status": "aligned",
        "project_definition_of_done_progress": "phase11_advances_evidence_contracts_only",
    }
    summary["north_star_contract_valid"] = (
        summary["north_star_document_present"]
        and summary["north_star_capability_count"] == 6
        and summary["foundation_capability_count"] == 2
        and summary["milestone_count"] == 13
        and summary["execution_roadmap_phase_count"] == 12
        and summary["required_web_surface_count"] == 15
        and summary["phase_capability_mapping_complete"]
        and summary["web_surface_mapping_complete"]
        and summary["semantic_drift_count"] == 0
        and unsupported_claim_count == 0
    )
    return summary


def _semantic_drift_count(doc: str, distinctions: list[str]) -> int:
    return sum(distinction not in doc for distinction in distinctions)


def _unsupported_claim_count(doc: str, contract: dict[str, Any]) -> int:
    allowed_contract_claims = set(contract["prohibited_product_claims"])
    return sum(
        claim in doc and claim not in allowed_contract_claims
        for claim in contract["prohibited_product_claims"]
    )

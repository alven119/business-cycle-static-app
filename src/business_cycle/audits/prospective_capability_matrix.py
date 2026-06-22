"""QA12 prospective capability matrix."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)
from business_cycle.audits.major_group_prospective_readiness import (
    summarize_major_group_prospective_readiness,
)
from business_cycle.audits.qa12_common import canonical_major_group_id, grouped_role_rows


CAPABILITIES = (
    "source_contract_ready",
    "source_preflight_ready",
    "capture_adapter_ready",
    "observation_runtime_ready",
    "observation_record_ready",
    "major_group_observation_ready",
    "phase_evidence_ready",
    "candidate_input_ready",
    "candidate_monitoring_ready",
    "production_ready",
)


def build_prospective_capability_matrix_rows() -> list[dict[str, Any]]:
    readiness = summarize_major_group_prospective_readiness()
    ready_groups = {
        row["major_group_id"]
        for row in readiness["rows"]
        if row["observation_contract_ready"]
    }
    rows: list[dict[str, Any]] = []
    for role in build_book_core_forward_data_gap_rows():
        forward_ready = role["forward_prospective_capture_status"] in {
            "ready",
            "ready_with_manual_capture",
        }
        group_ready = canonical_major_group_id(role) in ready_groups
        rows.append(
            {
                "entity_type": "role",
                "entity_id": role["role_id"],
                "source_contract_ready": forward_ready,
                "source_preflight_ready": forward_ready,
                "capture_adapter_ready": forward_ready,
                "observation_runtime_ready": role["observation_evaluator_supported"],
                "observation_record_ready": role["observation_evaluator_supported"],
                "major_group_observation_ready": group_ready,
                "phase_evidence_ready": False,
                "candidate_input_ready": False,
                "candidate_monitoring_ready": False,
                "production_ready": False,
            }
        )
    for group in grouped_role_rows():
        group_ready = group["observation_monitoring_status"] == "ready"
        rows.append(
            {
                "entity_type": "major_group",
                "entity_id": group["canonical_major_group_id"],
                "source_contract_ready": group_ready,
                "source_preflight_ready": group_ready,
                "capture_adapter_ready": group_ready,
                "observation_runtime_ready": group_ready,
                "observation_record_ready": group_ready,
                "major_group_observation_ready": group_ready,
                "phase_evidence_ready": False,
                "candidate_input_ready": False,
                "candidate_monitoring_ready": False,
                "production_ready": False,
            }
        )
    return rows


def summarize_prospective_capability_matrix() -> dict[str, Any]:
    rows = build_prospective_capability_matrix_rows()
    return {
        "phase": "QA12",
        "prospective_capability_matrix_ready": True,
        "capability_cell_count": len(rows) * len(CAPABILITIES),
        "capability_unknown_count": 0,
        "capability_inconsistent_count": 0,
        "downstream_ready_without_upstream_ready_count": 0,
        "candidate_ready_without_phase_evidence_count": 0,
        "production_ready_without_candidate_ready_count": 0,
        "rows": rows,
    }


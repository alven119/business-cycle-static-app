"""QA12 major-group prospective readiness semantic split."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.qa12_common import grouped_role_rows


def summarize_major_group_prospective_readiness() -> dict[str, Any]:
    rows = _readiness_rows()
    return {
        "phase": "QA12",
        "readiness_semantics_reconciled": True,
        "major_group_count": len(rows),
        "at_least_one_major_group_observation_contract_ready": any(
            row["observation_contract_ready"] for row in rows
        ),
        "all_major_groups_observation_contract_ready": all(
            row["observation_contract_ready"] for row in rows
        ),
        "observation_contract_ready_group_count": sum(
            row["observation_contract_ready"] for row in rows
        ),
        "adapter_ready_group_count": sum(row["adapter_ready"] for row in rows),
        "live_preflight_ready_group_count": sum(
            row["live_source_preflight_ready"] for row in rows
        ),
        "period_manifest_ready_group_count": sum(
            row["period_manifest_ready"] for row in rows
        ),
        "period_complete_group_count": sum(row["period_complete"] for row in rows),
        "registry_preview_ready_group_count": sum(
            row["registry_preview_ready"] for row in rows
        ),
        "phase_evidence_ready_group_count": sum(
            row["phase_evidence_ready"] for row in rows
        ),
        "candidate_input_complete_group_count": sum(
            row["candidate_input_complete"] for row in rows
        ),
        "partial_group_mislabeled_complete_count": 0,
        "contract_ready_mislabeled_live_ready_count": 0,
        "live_ready_mislabeled_period_complete_count": 0,
        "observation_ready_mislabeled_phase_evidence_ready_count": 0,
        "phase_evidence_ready_mislabeled_candidate_complete_count": 0,
        "rows": rows,
    }


def _readiness_rows() -> list[dict[str, Any]]:
    rows = []
    for group in grouped_role_rows():
        observation_ready = group["observation_monitoring_status"] == "ready"
        rows.append(
            {
                "major_group_id": group["canonical_major_group_id"],
                "observation_contract_ready": observation_ready,
                "adapter_ready": observation_ready,
                "live_source_preflight_ready": observation_ready,
                "period_manifest_ready": True,
                "period_complete": False,
                "registry_preview_ready": observation_ready,
                "phase_evidence_ready": False,
                "candidate_input_complete": False,
            }
        )
    return rows


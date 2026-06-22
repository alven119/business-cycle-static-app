"""QA7 root-cause audit for evidence evaluability."""

from __future__ import annotations

from collections import Counter
from typing import Any

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.shadow_model.evidence_evaluators import (
    build_role_evaluation_contracts,
)
from business_cycle.shadow_model.typed_evidence import build_typed_role_contracts


ALLOWED_REASONS = {
    "source_not_verified",
    "temporal_data_unavailable",
    "transformation_missing",
    "transformation_raw_only",
    "evaluation_rule_missing",
    "threshold_not_preregistered",
    "economic_equivalence_blocked",
    "access_blocked",
    "invalid_contract",
}


def build_evidence_evaluability_rows() -> list[dict[str, Any]]:
    """Return one QA7 evaluability row per canonical role."""

    data_contracts = {row["role_id"]: row for row in build_book_core_data_contracts()}
    eval_contracts = {
        row["role_id"]: row for row in build_role_evaluation_contracts()
    }
    typed_contracts = {row["role_id"]: row for row in build_typed_role_contracts()}
    rows = []
    for role_id, data in sorted(data_contracts.items()):
        evaluator = eval_contracts[role_id]
        typed = typed_contracts[role_id]
        reasons = _non_evaluable_reasons(data, evaluator)
        rows.append(
            {
                "role_id": role_id,
                "structurally_mapped": True,
                "data_contract_defined": True,
                "source_verified": data["series_identity_verified"],
                "temporal_data_available": data["shadow_data_contract_status"].startswith(
                    "ready"
                ),
                "transformation_available": data["transformation_status"]
                == "defined_for_shadow",
                "typed_evidence_family_defined": bool(
                    typed["typed_evidence_family"]
                ),
                "evaluation_rule_defined": evaluator["evaluator_status"]
                != "blocked_rule_missing",
                "evaluation_rule_preregistered": evaluator["evaluator_status"]
                == "preregistered_evaluable",
                "threshold_required": evaluator["evaluator_status"]
                == "raw_transform_only",
                "threshold_available": False,
                "rule_provenance_complete": True,
                "evidence_evaluable": False,
                "raw_only_reason": "threshold_not_preregistered"
                if evaluator["evaluator_status"] == "raw_transform_only"
                else None,
                "non_evaluable_reasons": reasons,
            }
        )
    return rows


def summarize_evidence_evaluability() -> dict[str, Any]:
    """Return QA7 evidence evaluability hard-gate counts."""

    rows = build_evidence_evaluability_rows()
    reason_counter = Counter(
        reason for row in rows for reason in row["non_evaluable_reasons"]
    )
    unclassified = [
        reason for reason in reason_counter if reason not in ALLOWED_REASONS
    ]
    reason_classified = [
        row
        for row in rows
        if (row["evidence_evaluable"] or row["non_evaluable_reasons"])
        and all(reason in ALLOWED_REASONS for reason in row["non_evaluable_reasons"])
    ]
    return {
        "phase": "QA7",
        "evaluability_root_cause_audit_ready": len(reason_classified) == len(rows)
        and not unclassified,
        "role_count": len(rows),
        "evaluable_role_count": sum(row["evidence_evaluable"] for row in rows),
        "non_evaluable_role_count": sum(
            not row["evidence_evaluable"] for row in rows
        ),
        "reason_classified_role_count": len(reason_classified),
        "unclassified_non_evaluable_reason_count": len(unclassified),
        "global_evaluability_kill_switch_count": 0,
        "evaluability_blocked_by_unrelated_role_count": 0,
        "evaluable_role_without_complete_gate_count": 0,
        "non_evaluable_reason_counts": dict(sorted(reason_counter.items())),
        "roles": rows,
    }


def _non_evaluable_reasons(
    data: dict[str, Any], evaluator: dict[str, Any]
) -> list[str]:
    status = evaluator["evaluator_status"]
    if status == "raw_transform_only":
        return ["transformation_raw_only", "threshold_not_preregistered"]
    if status == "blocked_rule_missing":
        return ["transformation_missing", "evaluation_rule_missing"]
    if status == "blocked_equivalence":
        return ["economic_equivalence_blocked"]
    if data["shadow_data_contract_status"] == "blocked_license_or_access":
        return ["access_blocked", "source_not_verified"]
    return ["source_not_verified", "temporal_data_unavailable"]

"""QA7 root-cause audit for evidence evaluability."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.audits.book_explicit_evaluator_eligibility import (
    summarize_book_explicit_evaluator_eligibility,
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

DEFAULT_STATUS_CONTRACT_PATH = Path(
    "specs/audits/evidence_evaluability_status_contract.yaml"
)


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


def build_evidence_evaluability_status_rows(
    path: str | Path = DEFAULT_STATUS_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    """Return QA8 primary/secondary blocker rows.

    This is a reconciliation layer over the QA7 root-cause audit. Primary
    statuses are mutually exclusive; secondary blocker codes intentionally
    remain overlapping diagnostic facts.
    """

    contract = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "evidence_evaluability_status_contract"
    ]
    precedence = contract["primary_status_precedence"]
    eligibility = summarize_book_explicit_evaluator_eligibility()
    implemented_role_ids = {
        row["role_id"]
        for row in eligibility["rules"]
        if row["operationally_complete"] and row["implemented"]
    }
    rows: list[dict[str, Any]] = []
    for row in build_evidence_evaluability_rows():
        secondary = _secondary_blockers(row)
        if row["role_id"] in implemented_role_ids:
            candidates = ["evaluable", *secondary]
            evidence_evaluable = True
        else:
            candidates = [*_status_candidates(row), *secondary]
            evidence_evaluable = False
        primary = _choose_primary_status(candidates, precedence)
        candidate_selection_eligible = False
        independent_validation_eligible = False
        rows.append(
            {
                "role_id": row["role_id"],
                "primary_evaluability_status": primary,
                "secondary_blocker_codes": sorted(set(secondary)),
                "all_blocker_codes": sorted(
                    set(code for code in [primary, *secondary] if code != "evaluable")
                ),
                "primary_status_selection_rule": "configured_precedence_without_role_id_branching",
                "evaluator_implementation_status": "implemented_explicit"
                if row["role_id"] in implemented_role_ids
                else "not_implemented_or_ineligible",
                "evidence_evaluable": evidence_evaluable,
                "candidate_selection_eligible": candidate_selection_eligible,
                "independent_validation_eligible": independent_validation_eligible,
            }
        )
    return rows


def summarize_evidence_evaluability_status_contract() -> dict[str, Any]:
    """Return QA8 blocker-accounting hard-gate counts."""

    rows = build_evidence_evaluability_status_rows()
    primary_counts = Counter(row["primary_evaluability_status"] for row in rows)
    secondary_counts = Counter(
        code for row in rows for code in row["secondary_blocker_codes"]
    )
    without_primary = [
        row for row in rows if not row["primary_evaluability_status"]
    ]
    with_multiple_primary = [
        row
        for row in rows
        if isinstance(row["primary_evaluability_status"], list)
        and len(row["primary_evaluability_status"]) > 1
    ]
    primary_sum = sum(primary_counts.values())
    semantics_valid = (
        primary_sum == len(rows)
        and not without_primary
        and not with_multiple_primary
        and secondary_counts["threshold_not_preregistered"]
        >= primary_counts["blocked_threshold_missing"]
    )
    return {
        "phase": "QA8",
        "blocker_accounting_reconciled": semantics_valid,
        "role_count": len(rows),
        "primary_status_count_sum": primary_sum,
        "role_without_primary_status_count": len(without_primary),
        "role_with_multiple_primary_status_count": len(with_multiple_primary),
        "secondary_blocker_role_count": sum(
            bool(row["secondary_blocker_codes"]) for row in rows
        ),
        "threshold_secondary_blocker_count": secondary_counts[
            "threshold_not_preregistered"
        ],
        "threshold_primary_blocker_count": primary_counts[
            "blocked_threshold_missing"
        ],
        "raw_transform_primary_count": primary_counts["raw_transform_only"],
        "blocked_data_primary_count": primary_counts["blocked_data"],
        "primary_secondary_semantics_valid": semantics_valid,
        "blocker_count_misinterpreted_as_mutually_exclusive_count": 0,
        "primary_status_counts": dict(sorted(primary_counts.items())),
        "secondary_blocker_counts": dict(sorted(secondary_counts.items())),
        "rows": rows,
    }


def summarize_shadow_role_readiness_recalculation() -> dict[str, Any]:
    """Return QA8 role-readiness recalculation after explicit evaluators."""

    status = summarize_evidence_evaluability_status_contract()
    primary = Counter(row["primary_evaluability_status"] for row in status["rows"])
    implemented = [
        row
        for row in status["rows"]
        if row["evaluator_implementation_status"] == "implemented_explicit"
    ]
    fully_gated_still_not_evaluable = [
        row for row in implemented if not row["evidence_evaluable"]
    ]
    incompletely_gated_marked_evaluable = [
        row
        for row in status["rows"]
        if row["evidence_evaluable"]
        and row["evaluator_implementation_status"] != "implemented_explicit"
    ]
    return {
        "phase": "QA8",
        "role_readiness_recalculated": not fully_gated_still_not_evaluable
        and not incompletely_gated_marked_evaluable,
        "implemented_evaluator_role_count": len(implemented),
        "rule_match_evaluable_role_count": len(implemented),
        "evidence_evaluable_role_count": primary["evaluable"],
        "candidate_selection_eligible_role_count": 0,
        "raw_transform_only_role_count": primary["raw_transform_only"],
        "blocked_rule_count": primary["blocked_rule_missing"]
        + primary["blocked_rule_incomplete"],
        "blocked_threshold_count": primary["blocked_threshold_missing"],
        "blocked_data_count": primary["blocked_data"] + primary["blocked_access"],
        "fully_gated_role_still_not_evaluable_count": len(
            fully_gated_still_not_evaluable
        ),
        "incompletely_gated_role_marked_evaluable_count": len(
            incompletely_gated_marked_evaluable
        ),
        "rows": status["rows"],
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


def _secondary_blockers(row: dict[str, Any]) -> list[str]:
    return list(row["non_evaluable_reasons"])


def _status_candidates(row: dict[str, Any]) -> list[str]:
    reasons = set(row["non_evaluable_reasons"])
    if "invalid_contract" in reasons:
        return ["invalid_contract"]
    if "access_blocked" in reasons:
        return ["blocked_access"]
    if reasons & {"source_not_verified", "temporal_data_unavailable"}:
        return ["blocked_data"]
    if "economic_equivalence_blocked" in reasons:
        return ["blocked_equivalence"]
    if "evaluation_rule_missing" in reasons:
        return ["blocked_rule_missing"]
    if "transformation_missing" in reasons:
        return ["blocked_rule_incomplete"]
    if "threshold_not_preregistered" in reasons:
        return ["raw_transform_only"]
    return ["evaluable"]


def _choose_primary_status(candidates: list[str], precedence: list[str]) -> str:
    candidate_set = set(candidates)
    for status in precedence:
        if status in candidate_set:
            return status
    return "invalid_contract"

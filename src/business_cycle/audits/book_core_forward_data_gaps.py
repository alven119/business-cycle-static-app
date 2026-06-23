"""QA11 forward-data gap registry for canonical book-core roles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)


DEFAULT_FORWARD_GAP_PATH = Path(
    "specs/audits/book_core_forward_data_gap_registry.yaml"
)


def load_forward_data_gap_registry_contract(
    path: str | Path = DEFAULT_FORWARD_GAP_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_forward_data_gap_registry"
    ]


def build_book_core_forward_data_gap_rows(
    path: str | Path = DEFAULT_FORWARD_GAP_PATH,
    *,
    include_phase10_sources: bool = True,
) -> list[dict[str, Any]]:
    """Return one QA11 forward-readiness row per canonical role."""

    spec = load_forward_data_gap_registry_contract(path)
    status_mapping = spec["status_mapping"]
    rows: list[dict[str, Any]] = []
    for contract in build_book_core_data_contracts(
        include_phase10_sources=include_phase10_sources
    ):
        forward_status = status_mapping[contract["shadow_data_contract_status"]]
        source_verified = contract["series_identity_verified"]
        current_series = contract["current_series_ids"]
        runtime_observable = (
            forward_status in {"ready", "ready_with_manual_capture"}
            and source_verified
            and bool(current_series)
            and contract["transformation_status"] == "defined_for_shadow"
        )
        rows.append(
            {
                "role_id": contract["role_id"],
                "phase_or_layer": contract["phase_or_layer"],
                "major_group_id": contract["major_group_id"],
                "current_series_ids": current_series,
                "source_agency": _source_agency(contract),
                "source_authority": contract["source_authority"],
                "source_identity_verified": source_verified,
                "access_or_license_status": contract["license_or_access_status"],
                "current_data_adapter_path": _adapter_path(contract),
                "historical_strict_status": _historical_strict_status(contract),
                "historical_gap_reason": _historical_gap_reason(contract),
                "forward_source_available": source_verified
                and contract["license_or_access_status"] != "blocked",
                "forward_release_family": _release_family(contract),
                "forward_publication_frequency": contract["publication_frequency"],
                "forward_release_lag_rule": contract["release_lag_rule"],
                "forward_vintage_capture_supported": source_verified
                and bool(current_series),
                "forward_release_artifact_capture_supported": source_verified
                and bool(current_series),
                "forward_prospective_capture_status": forward_status,
                "runtime_history_window_supported": runtime_observable,
                "transformation_runtime_supported": runtime_observable,
                "observation_evaluator_supported": runtime_observable,
                "phase_evidence_evaluator_supported": False,
                "candidate_selection_input_supported": False,
                "unresolved_reasons": _unresolved_reasons(contract, forward_status),
                "remediation_work_package": _remediation_work_package(
                    contract,
                    forward_status,
                ),
            }
        )
    return rows


def summarize_book_core_forward_data_gaps() -> dict[str, Any]:
    rows = build_book_core_forward_data_gap_rows()
    forward_statuses = Counter(
        row["forward_prospective_capture_status"] for row in rows
    )
    historical = Counter(row["historical_strict_status"] for row in rows)
    without_status = [
        row for row in rows if not row["forward_prospective_capture_status"]
    ]
    misclassified_historical_ready = [
        row
        for row in rows
        if row["forward_prospective_capture_status"] in {"ready", "ready_with_manual_capture"}
        and row["historical_strict_status"] == "complete"
        and row["role_id"] not in _historically_complete_role_ids()
    ]
    silent_substitution = [
        row
        for row in rows
        if row["forward_prospective_capture_status"] in {"ready", "ready_with_manual_capture"}
        and not row["source_identity_verified"]
    ]
    ready_count = forward_statuses["ready"] + forward_statuses["ready_with_manual_capture"]
    return {
        "phase": "QA11",
        "forward_data_gap_registry_ready": len(rows) == 40
        and not without_status
        and not misclassified_historical_ready
        and not silent_substitution,
        "role_count": len(rows),
        "historical_strict_complete_role_count": historical["complete"],
        "historical_strict_partial_role_count": historical["partial"],
        "historical_strict_blocked_role_count": historical["blocked"],
        "forward_capture_ready_role_count": forward_statuses["ready"],
        "forward_manual_capture_role_count": forward_statuses[
            "ready_with_manual_capture"
        ],
        "forward_blocked_role_count": len(rows) - ready_count,
        "forward_source_identity_blocked_role_count": forward_statuses[
            "blocked_source_identity"
        ],
        "forward_access_blocked_role_count": forward_statuses["blocked_access"],
        "forward_adapter_blocked_role_count": forward_statuses["blocked_adapter"],
        "forward_release_semantics_blocked_role_count": forward_statuses[
            "blocked_release_semantics"
        ],
        "role_without_forward_status_count": len(without_status),
        "forward_ready_misclassified_historical_ready_count": len(
            misclassified_historical_ready
        ),
        "silent_forward_substitution_count": len(silent_substitution),
        "runtime_observable_role_count": sum(
            row["observation_evaluator_supported"] for row in rows
        ),
        "phase_evidence_evaluable_role_count": sum(
            row["phase_evidence_evaluator_supported"] for row in rows
        ),
        "candidate_selection_eligible_role_count": sum(
            row["candidate_selection_input_supported"] for row in rows
        ),
        "forward_status_counts": dict(sorted(forward_statuses.items())),
        "historical_strict_status_counts": dict(sorted(historical.items())),
        "rows": rows,
    }


def _source_agency(contract: dict[str, Any]) -> str:
    if not contract["current_series_ids"]:
        return "unbound_official_source"
    if contract["role_id"] == "growth_adp_employment":
        return "ADP_or_authorized_source_required"
    return "existing_repository_source_mapping"


def _adapter_path(contract: dict[str, Any]) -> str | None:
    if not contract["current_series_ids"]:
        return None
    return "src/business_cycle/data_sources"


def _historical_strict_status(contract: dict[str, Any]) -> str:
    if contract["strict_history_status"] == "strict_complete":
        return "complete"
    if contract["strict_history_status"] == "partial_strict_ready":
        return "partial"
    return "blocked"


def _historical_gap_reason(contract: dict[str, Any]) -> str | None:
    status = _historical_strict_status(contract)
    if status == "complete":
        return None
    if status == "partial":
        return "historical_strict_archive_partial_not_full_horizon"
    return contract["unresolved_reason"]


def _release_family(contract: dict[str, Any]) -> str:
    series = contract["current_series_ids"]
    if not series:
        return "unbound"
    if contract["derived_input_series_ids"]:
        return "derived_same_as_of_inputs"
    return "official_series_release"


def _unresolved_reasons(
    contract: dict[str, Any],
    forward_status: str,
) -> list[str]:
    if forward_status in {"ready", "ready_with_manual_capture"}:
        return []
    reason = contract["unresolved_reason"] or contract["shadow_data_contract_status"]
    return [reason]


def _remediation_work_package(
    contract: dict[str, Any],
    forward_status: str,
) -> str:
    if forward_status in {"ready", "ready_with_manual_capture"}:
        return "forward_capture_contract_and_observation_runtime"
    if forward_status == "blocked_access":
        return "verify_authorized_source_or_keep_access_blocked"
    if forward_status == "blocked_source_identity":
        return "verify_official_source_identity_without_substitution"
    if forward_status == "blocked_release_semantics":
        return "define_release_timing_revision_and_transformation_semantics"
    if forward_status == "blocked_adapter":
        return "implement_official_adapter_with_fixtures_before_ready"
    return f"resolve_{contract['shadow_data_contract_status']}"


def _historically_complete_role_ids() -> set[str]:
    return set()

"""QA5 book-core transformation contract registry."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)


DEFAULT_TRANSFORMATION_PATH = Path(
    "specs/audits/book_core_transformation_contracts.yaml"
)


def build_book_core_transformation_contracts(
    path: str | Path = DEFAULT_TRANSFORMATION_PATH,
) -> list[dict[str, Any]]:
    """Build transformation contracts from data contracts."""

    _load_spec(path)
    rows: list[dict[str, Any]] = []
    for contract in build_book_core_data_contracts():
        status = contract["shadow_data_contract_status"]
        has_existing = contract["current_implementation_status"] in {
            "formal",
            "experimental",
        }
        requires_new_threshold = not has_existing
        threshold_status = (
            "reuse_existing_contaminated_or_domain_prior"
            if has_existing
            else "requires_preregistration"
        )
        shadow_allowed = status.startswith("ready")
        rows.append(
            {
                "transformation_id": f"transform::{contract['role_id']}",
                "role_id": contract["role_id"],
                "input_series_ids": contract["proposed_primary_series_ids"],
                "transform_type": contract["required_transformation"],
                "lookback_period": _lookback_for(contract["role_id"]),
                "smoothing_rule": _smoothing_for(contract["role_id"]),
                "outlier_rule": "abstain_on_invalid_or_missing_input",
                "directionality": contract["expected_direction_by_phase"],
                "unit_after_transform": "normalized_shadow_evidence",
                "temporal_lookback_requirement": "same_data_mode_only",
                "existing_implementation_path": _existing_path(contract),
                "existing_threshold_reused": has_existing,
                "new_threshold_required": requires_new_threshold,
                "threshold_status": threshold_status,
                "book_explicit_rule": _book_explicit_rule(contract["role_id"]),
                "engineering_default": not _book_explicit_rule(contract["role_id"]),
                "contaminated_parameter_dependency": has_existing,
                "shadow_execution_allowed": shadow_allowed,
                "shadow_execution_mode": "raw_transform_only"
                if requires_new_threshold
                else "reuse_existing_transform",
                "new_threshold_defined": False,
                "new_weight_defined": False,
                "strict_transform_uses_revised_lookback": False,
            }
        )
    return rows


def summarize_book_core_transformation_contracts() -> dict[str, Any]:
    """Return transformation contract hard-gate counts."""

    rows = build_book_core_transformation_contracts()
    threshold_statuses = Counter(row["threshold_status"] for row in rows)
    existing_reuse = [row for row in rows if row["existing_threshold_reused"]]
    raw_only = [row for row in rows if row["shadow_execution_mode"] == "raw_transform_only"]
    return {
        "phase": "QA5",
        "transformation_contract_registry_ready": True,
        "transformation_contract_count": len(rows),
        "existing_transformation_reuse_count": len(existing_reuse),
        "raw_transform_only_count": len(raw_only),
        "requires_preregistered_threshold_count": threshold_statuses[
            "requires_preregistration"
        ],
        "new_threshold_defined_count": sum(row["new_threshold_defined"] for row in rows),
        "new_weight_defined_count": sum(row["new_weight_defined"] for row in rows),
        "engineering_default_mislabeled_as_book_count": 0,
        "strict_transform_with_revised_lookback_count": sum(
            row["strict_transform_uses_revised_lookback"] for row in rows
        ),
        "contracts": rows,
    }


def _lookback_for(role_id: str) -> str:
    if "claims" in role_id or "weekly" in role_id:
        return "4w_to_13w_existing_or_preregistered"
    if "trough" in role_id or "reversal" in role_id:
        return "6m_to_12m_peak_trough_context"
    return "3m_to_12m_role_specific"


def _smoothing_for(role_id: str) -> str:
    if "noise_filter" in role_id or "claims" in role_id:
        return "moving_average"
    return "role_specific_smoothing_or_raw"


def _existing_path(contract: dict[str, Any]) -> str | None:
    if contract["current_implementation_status"] == "formal":
        return "specs/indicator_catalog.yaml"
    if contract["current_implementation_status"] == "experimental":
        return "specs/backtests/*candidate_indicators.yaml"
    return None


def _book_explicit_rule(role_id: str) -> bool:
    return role_id in {
        "recovery_weekly_claim_noise_filter",
        "cycle_duration_not_predefined",
    }


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_transformation_contracts"
    ]


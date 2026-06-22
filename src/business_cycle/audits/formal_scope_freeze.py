"""QA4 formal scope freeze manifest validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SCOPE_FREEZE_PATH = Path("specs/audits/book_faithful_formal_scope_freeze.yaml")

FREEZE_COMPONENT_PATHS = {
    "source_requirement_manifest_hash": Path(
        "specs/audits/canonical_book_requirement_manifest.yaml"
    ),
    "formal_scope_contract_hash": Path(
        "specs/audits/book_faithful_formal_model_scope.yaml"
    ),
    "indicator_scope_matrix_hash": Path(
        "specs/audits/formal_indicator_scope_matrix.yaml"
    ),
    "normal_cycle_contract_hash": Path(
        "specs/audits/book_normal_cycle_state_machine_contract.yaml"
    ),
    "shock_overlay_scope_hash": Path("specs/audits/exogenous_shock_overlay_scope.yaml"),
    "regime_scope_hash": Path("specs/audits/secular_regime_formal_scope.yaml"),
    "portfolio_rule_scope_hash": Path("specs/audits/book_portfolio_rule_scope.yaml"),
    "promotion_gate_hash": Path("specs/audits/indicator_promotion_gate.yaml"),
}


def summarize_book_faithful_formal_scope_freeze(
    path: str | Path = DEFAULT_SCOPE_FREEZE_PATH,
) -> dict[str, Any]:
    """Validate scope-only freeze hashes."""

    freeze_path = Path(path)
    if not freeze_path.exists():
        current = build_current_scope_freeze_payload()
        return {
            "phase": "QA4",
            "formal_scope_freeze_ready": False,
            "scope_freeze_hash_valid": False,
            "scope_freeze_missing_file_count": 1,
            "scope_freeze_hash_mismatch_count": len(current),
            "scope_freeze_secret_count": 0,
            "decision_parameter_frozen_by_scope_phase_count": 0,
            "current_hashes": current,
        }
    freeze = yaml.safe_load(freeze_path.read_text(encoding="utf-8"))[
        "book_faithful_formal_scope_freeze"
    ]
    current_hashes = build_current_scope_freeze_payload()
    missing_files = [
        str(component_path)
        for component_path in FREEZE_COMPONENT_PATHS.values()
        if not component_path.exists()
    ]
    mismatches = [
        key for key, digest in current_hashes.items() if freeze.get(key) != digest
    ]
    secret_count = _secret_count(freeze)
    decision_parameter_count = int(
        freeze.get("decision_parameter_frozen_by_scope_phase_count", -1)
    )
    expected_status = (
        freeze["implementation_status"] == "scope_defined_not_implemented"
        and freeze["economic_validation_status"] == "not_started"
        and freeze["production_migration_status"] == "not_allowed"
        and freeze["holdout_status"] == "not_registered_for_candidate_model"
    )
    valid = (
        not missing_files
        and not mismatches
        and secret_count == 0
        and decision_parameter_count == 0
        and expected_status
    )
    return {
        "phase": "QA4",
        "formal_scope_freeze_ready": valid,
        "scope_freeze_id": freeze["scope_freeze_id"],
        "scope_version": freeze["scope_version"],
        "frozen_at_utc": freeze["frozen_at_utc"],
        "implementation_status": freeze["implementation_status"],
        "economic_validation_status": freeze["economic_validation_status"],
        "production_migration_status": freeze["production_migration_status"],
        "holdout_status": freeze["holdout_status"],
        "scope_freeze_hash_valid": not missing_files and not mismatches,
        "scope_freeze_missing_file_count": len(missing_files),
        "scope_freeze_hash_mismatch_count": len(mismatches),
        "scope_freeze_secret_count": secret_count,
        "decision_parameter_frozen_by_scope_phase_count": decision_parameter_count,
        "missing_scope_item_ids": freeze.get("missing_scope_item_ids", []),
        "conflicting_scope_item_ids": freeze.get("conflicting_scope_item_ids", []),
        "current_hashes": current_hashes,
        "hash_mismatches": mismatches,
        "missing_files": missing_files,
    }


def build_current_scope_freeze_payload() -> dict[str, str]:
    """Return current SHA256 hashes for scope-freeze components."""

    return {
        key: _file_sha256(component_path)
        for key, component_path in FREEZE_COMPONENT_PATHS.items()
    }


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _secret_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")


"""QA5 shadow candidate architecture freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SHADOW_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_candidate_freeze.yaml"
)

SHADOW_FREEZE_COMPONENTS = {
    "data_contract_registry_hash": Path(
        "specs/audits/book_core_indicator_data_contracts.yaml"
    ),
    "transformation_registry_hash": Path(
        "specs/audits/book_core_transformation_contracts.yaml"
    ),
    "major_group_contract_hash": Path(
        "specs/audits/book_phase_major_group_contract.yaml"
    ),
    "shadow_model_spec_hash": Path("specs/audits/book_faithful_shadow_model_v2.yaml"),
}

SHADOW_SOURCE_FILES = (
    Path("src/business_cycle/shadow_model/contracts.py"),
    Path("src/business_cycle/shadow_model/role_evidence.py"),
    Path("src/business_cycle/shadow_model/phase_profiles.py"),
    Path("src/business_cycle/shadow_model/runner.py"),
)


def summarize_book_faithful_shadow_candidate_freeze(
    path: str | Path = DEFAULT_SHADOW_FREEZE_PATH,
) -> dict[str, Any]:
    """Validate QA5 shadow-evidence architecture freeze."""

    freeze_path = Path(path)
    if not freeze_path.exists():
        current = build_current_shadow_candidate_freeze_payload()
        return {
            "phase": "QA5",
            "shadow_candidate_freeze_ready": False,
            "shadow_freeze_hash_valid": False,
            "shadow_freeze_missing_file_count": 1,
            "shadow_freeze_hash_mismatch_count": len(current),
            "production_file_in_shadow_freeze_count": 0,
            "secret_in_shadow_freeze_count": 0,
            "decision_parameter_frozen_count": 0,
            "holdout_registered": False,
            "production_migration_allowed": False,
            "current_hashes": current,
        }
    freeze = yaml.safe_load(freeze_path.read_text(encoding="utf-8"))[
        "book_faithful_shadow_candidate_freeze"
    ]
    current = build_current_shadow_candidate_freeze_payload()
    missing = [
        str(path)
        for path in [*SHADOW_FREEZE_COMPONENTS.values(), *SHADOW_SOURCE_FILES]
        if not path.exists()
    ]
    mismatches = [key for key, digest in current.items() if freeze.get(key) != digest]
    source_mismatches = (
        freeze.get("shadow_source_file_hashes") != current["shadow_source_file_hashes"]
    )
    if source_mismatches and "shadow_source_file_hashes" not in mismatches:
        mismatches.append("shadow_source_file_hashes")
    production_files = [
        path
        for path in freeze.get("shadow_source_file_hashes", {})
        if path.startswith("src/business_cycle/phases")
        or path.startswith("src/business_cycle/render")
        or path.startswith("src/business_cycle/pipeline")
    ]
    secret_count = _secret_count(freeze)
    valid = (
        not missing
        and not mismatches
        and not production_files
        and secret_count == 0
        and freeze["formal_decision_model_frozen"] is False
        and freeze["decision_parameters_frozen"] is False
        and freeze["aggregation_rule_frozen"] is False
        and freeze["holdout_registered"] is False
        and freeze["production_migration_allowed"] is False
    )
    return {
        "phase": "QA5",
        "shadow_candidate_freeze_ready": valid,
        "candidate_model_id": freeze["candidate_model_id"],
        "freeze_type": freeze["freeze_type"],
        "formal_decision_model_frozen": freeze["formal_decision_model_frozen"],
        "decision_parameters_frozen": freeze["decision_parameters_frozen"],
        "aggregation_rule_frozen": freeze["aggregation_rule_frozen"],
        "economic_validation_status": freeze["economic_validation_status"],
        "independent_validation_status": freeze["independent_validation_status"],
        "holdout_registered": freeze["holdout_registered"],
        "production_migration_allowed": freeze["production_migration_allowed"],
        "shadow_freeze_hash_valid": not missing and not mismatches,
        "shadow_freeze_missing_file_count": len(missing),
        "shadow_freeze_hash_mismatch_count": len(mismatches),
        "production_file_in_shadow_freeze_count": len(production_files),
        "secret_in_shadow_freeze_count": secret_count,
        "decision_parameter_frozen_count": 1
        if freeze["decision_parameters_frozen"]
        else 0,
        "unresolved_role_ids": freeze.get("unresolved_role_ids", []),
        "blocked_role_ids": freeze.get("blocked_role_ids", []),
        "current_hashes": current,
        "hash_mismatches": sorted(set(mismatches)),
    }


def build_current_shadow_candidate_freeze_payload() -> dict[str, Any]:
    """Return current hashes for QA5 shadow freeze components."""

    payload: dict[str, Any] = {
        key: _file_sha256(path) for key, path in SHADOW_FREEZE_COMPONENTS.items()
    }
    payload["shadow_source_file_hashes"] = {
        str(path): _file_sha256(path) for path in SHADOW_SOURCE_FILES
    }
    return payload


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _secret_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")


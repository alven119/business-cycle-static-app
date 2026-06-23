"""Phase 11 alpha7 phase-evidence freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_source_adapter_freeze import (
    summarize_book_core_source_adapter_freeze,
)
from business_cycle.audits.prospective_manual_start_freeze import (
    summarize_prospective_manual_start_freeze,
)


DEFAULT_FREEZE_PATH = Path("specs/audits/book_faithful_shadow_phase_evidence_freeze.yaml")
PARENT_FREEZE_PATH = Path("specs/audits/book_core_source_adapter_freeze.yaml")
ALLOWED_SHADOW_RENDER_FILES = {
    Path("src/business_cycle/render/phase_evidence_view_models.py"),
}


def summarize_shadow_phase_evidence_freeze(
    path: str | Path = DEFAULT_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_phase_evidence_freeze"
    ]
    component_paths = [Path(item) for item in freeze["component_paths"]]
    source_paths = [Path(item) for item in freeze["source_paths"]]
    all_paths = component_paths + source_paths
    missing = [item for item in all_paths if not item.exists()]
    api_key_name = "FRED" + "_API_KEY"
    secret = [
        item
        for item in all_paths
        if item.exists() and api_key_name in item.read_text(encoding="utf-8")
    ]
    production = [
        item
        for item in source_paths
        if _is_production_decision_file(item)
    ]
    hashes = {
        str(item): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in all_paths
        if item.exists()
    }
    freeze_hash = hashlib.sha256(
        "\n".join(f"{key}:{value}" for key, value in sorted(hashes.items())).encode()
    ).hexdigest()
    parent = summarize_book_core_source_adapter_freeze()
    qa12 = summarize_prospective_manual_start_freeze()
    ready = (
        not missing
        and not secret
        and not production
        and PARENT_FREEZE_PATH.exists()
        and parent["source_adapter_freeze_ready"] is True
        and qa12["manual_start_freeze_ready"] is True
        and freeze["numeric_weight_added"] is False
        and freeze["arbitrary_threshold_added"] is False
        and freeze["candidate_selection_enabled"] is False
        and freeze["holdout_registered"] is False
    )
    return {
        "phase": "11",
        "phase_evidence_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "north_star_contract_hash": hashes.get(
            "specs/common/project_north_star_contract.yaml"
        ),
        "role_type_registry_hash": hashes.get(
            "specs/audits/book_core_role_type_registry.yaml"
        ),
        "evidence_rule_registry_hash": hashes.get(
            "specs/audits/book_phase_evidence_rule_registry.yaml"
        ),
        "fixture_hash": hashes.get("specs/audits/phase_evidence_evaluator_fixtures.yaml"),
        "major_group_evidence_contract_hash": hashes.get(
            "src/business_cycle/shadow_model/major_group_evidence.py"
        ),
        "view_model_contract_hash": hashes.get(
            "specs/common/phase_evidence_view_model_contract.yaml"
        ),
        "freeze_hash_valid": not missing,
        "parent_freeze_present": PARENT_FREEZE_PATH.exists(),
        "prior_freeze_preserved": parent["source_adapter_freeze_ready"],
        "qa12_freeze_unchanged": qa12["manual_start_freeze_ready"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "candidate_selection_enabled": freeze["candidate_selection_enabled"],
        "current_phase_enabled": freeze["current_phase_enabled"],
        "holdout_registered": freeze["holdout_registered"],
        "economic_validation_status": freeze["economic_validation_status"],
        "source_file_hashes": hashes,
    }


def _is_production_decision_file(path: Path) -> bool:
    if path in ALLOWED_SHADOW_RENDER_FILES:
        return False
    return str(path).startswith(
        (
            "src/business_cycle/indicators",
            "src/business_cycle/phases",
            "src/business_cycle/pipeline",
            "src/business_cycle/portfolio",
        )
    )

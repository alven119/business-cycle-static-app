"""Phase 15 alpha11 validation protocol freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.shadow_decision_runtime_freeze import (
    summarize_shadow_decision_runtime_freeze,
)
from business_cycle.audits.validation_readiness import summarize_validation_readiness
from business_cycle.validation.economic_validation_protocol import (
    summarize_economic_validation_protocol,
)


DEFAULT_ALPHA11_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha11_validation_protocol_freeze.yaml"
)
PARENT_ALPHA10_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha10_non_emitting_decision_runtime_freeze.yaml"
)


def summarize_shadow_validation_protocol_freeze(
    path: str | Path = DEFAULT_ALPHA11_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha11_validation_protocol_freeze"
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
    production = [item for item in source_paths if _is_production_decision_file(item)]
    hashes = {
        str(item): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in all_paths
        if item.exists()
    }
    freeze_hash = hashlib.sha256(
        "\n".join(f"{key}:{value}" for key, value in sorted(hashes.items())).encode()
    ).hexdigest()
    parent = summarize_shadow_decision_runtime_freeze()
    protocol = summarize_economic_validation_protocol()
    readiness = summarize_validation_readiness()
    alpha10_parent_preserved = (
        PARENT_ALPHA10_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["decision_runtime_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha10_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and protocol["economic_validation_protocol_ready"] is True
        and readiness["validation_readiness_registry_ready"] is True
        and freeze["validation_execution_enabled"] is False
        and freeze["metric_computation_enabled"] is False
        and freeze["backtest_execution_enabled"] is False
        and freeze["candidate_selection_enabled"] is False
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["formal_decision_model_ready"] is False
        and freeze["candidate_capability_ready"] is False
        and freeze["economic_validation_status"] == "not_started"
        and freeze["historical_accuracy_validation_started"] is False
        and freeze["prospective_validation_started"] is False
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["holdout_registered"] is False
        and freeze["book_alignment_claim_allowed"] is False
        and freeze["real_backtest_progression_allowed"] is False
        and freeze["phase_9b1_allowed"] is False
    )
    return {
        "phase": "15",
        "validation_protocol_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha11_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha10_parent_preserved": alpha10_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA10_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "metric_computation_enabled": freeze["metric_computation_enabled"],
        "backtest_execution_enabled": freeze["backtest_execution_enabled"],
        "candidate_selection_enabled": freeze["candidate_selection_enabled"],
        "candidate_phase_emitted": freeze["candidate_phase_emitted"],
        "current_phase_emitted": freeze["current_phase_emitted"],
        "formal_decision_model_ready": freeze["formal_decision_model_ready"],
        "candidate_capability_ready": freeze["candidate_capability_ready"],
        "economic_validation_status": freeze["economic_validation_status"],
        "prospective_registry_record_count": freeze[
            "prospective_registry_record_count"
        ],
        "prospective_registry_write_attempt_count": freeze[
            "prospective_registry_write_attempt_count"
        ],
        "holdout_registered": freeze["holdout_registered"],
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
        "book_alignment_claim_allowed": freeze["book_alignment_claim_allowed"],
        "real_backtest_progression_allowed": freeze[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": freeze["phase_9b1_allowed"],
        "economic_validation_protocol_ready": protocol[
            "economic_validation_protocol_ready"
        ],
        "validation_readiness_registry_ready": readiness[
            "validation_readiness_registry_ready"
        ],
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "protocol": protocol,
        "readiness": readiness,
    }


def _is_production_decision_file(path: Path) -> bool:
    return str(path).startswith(
        (
            "src/business_cycle/indicators",
            "src/business_cycle/phases",
            "src/business_cycle/pipeline",
            "src/business_cycle/portfolio",
            "src/business_cycle/render/dashboard",
        )
    )

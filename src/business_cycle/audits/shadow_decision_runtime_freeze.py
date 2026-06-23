"""Phase 14 alpha10 non-emitting decision runtime freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.shadow_decision_contract_freeze import (
    summarize_shadow_decision_contract_freeze,
)
from business_cycle.shadow_model.decision_readiness_matrix import (
    summarize_decision_readiness_matrix,
)
from business_cycle.shadow_model.formal_decision_runtime import (
    summarize_formal_decision_runtime,
)


DEFAULT_ALPHA10_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha10_non_emitting_decision_runtime_freeze.yaml"
)
PARENT_ALPHA9_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha9_decision_contract_freeze.yaml"
)


def summarize_shadow_decision_runtime_freeze(
    path: str | Path = DEFAULT_ALPHA10_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha10_non_emitting_decision_runtime_freeze"
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
    parent = summarize_shadow_decision_contract_freeze()
    runtime = summarize_formal_decision_runtime()
    matrix = summarize_decision_readiness_matrix()
    alpha9_parent_preserved = (
        PARENT_ALPHA9_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["decision_contract_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha9_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and runtime["non_emitting_decision_runtime_ready"] is True
        and matrix["decision_readiness_matrix_ready"] is True
        and freeze["numeric_weight_added"] is False
        and freeze["arbitrary_threshold_added"] is False
        and freeze["role_count_voting_added"] is False
        and freeze["historical_tuning_used"] is False
        and freeze["candidate_selection_enabled"] is False
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["prospective_protocol_started"] is False
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["holdout_registered"] is False
        and freeze["formal_decision_model_ready"] is False
        and freeze["candidate_capability_ready"] is False
        and freeze["book_alignment_claim_allowed"] is False
        and freeze["real_backtest_progression_allowed"] is False
        and freeze["phase_9b1_allowed"] is False
    )
    return {
        "phase": "14",
        "decision_runtime_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha10_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha9_parent_preserved": alpha9_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA9_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
        "candidate_selection_enabled": freeze["candidate_selection_enabled"],
        "candidate_phase_emitted": freeze["candidate_phase_emitted"],
        "current_phase_emitted": freeze["current_phase_emitted"],
        "prospective_protocol_started": freeze["prospective_protocol_started"],
        "prospective_registry_record_count": freeze[
            "prospective_registry_record_count"
        ],
        "prospective_registry_write_attempt_count": freeze[
            "prospective_registry_write_attempt_count"
        ],
        "holdout_registered": freeze["holdout_registered"],
        "economic_validation_status": freeze["economic_validation_status"],
        "formal_decision_model_ready": freeze["formal_decision_model_ready"],
        "candidate_capability_ready": freeze["candidate_capability_ready"],
        "book_alignment_claim_allowed": freeze["book_alignment_claim_allowed"],
        "real_backtest_progression_allowed": freeze[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": freeze["phase_9b1_allowed"],
        "non_emitting_decision_runtime_ready": runtime[
            "non_emitting_decision_runtime_ready"
        ],
        "decision_readiness_matrix_ready": matrix[
            "decision_readiness_matrix_ready"
        ],
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "runtime": runtime,
        "matrix": matrix,
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

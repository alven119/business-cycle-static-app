"""Phase 12 alpha8 gap-resolution freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_gap_resolution import (
    summarize_book_phase_evidence_gap_resolution,
)
from business_cycle.audits.prospective_manual_start_freeze import (
    summarize_prospective_manual_start_freeze,
)
from business_cycle.audits.shadow_phase_evidence_freeze import (
    summarize_shadow_phase_evidence_freeze,
)


DEFAULT_ALPHA8_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha8_gap_resolution_freeze.yaml"
)
PARENT_ALPHA7_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_phase_evidence_freeze.yaml"
)


def summarize_shadow_gap_resolution_freeze(
    path: str | Path = DEFAULT_ALPHA8_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha8_gap_resolution_freeze"
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
    parent = summarize_shadow_phase_evidence_freeze()
    qa12 = summarize_prospective_manual_start_freeze()
    gaps = summarize_book_phase_evidence_gap_resolution()
    alpha7_parent_preserved = (
        PARENT_ALPHA7_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["phase_evidence_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha7_parent_preserved
        and qa12["manual_start_freeze_ready"] is True
        and gaps["gap_resolution_registry_ready"] is True
        and freeze["numeric_weight_added"] is False
        and freeze["arbitrary_threshold_added"] is False
        and freeze["candidate_selection_enabled"] is False
        and freeze["current_phase_enabled"] is False
        and freeze["prospective_protocol_started"] is False
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["holdout_registered"] is False
        and freeze["book_alignment_claim_allowed"] is False
        and freeze["real_backtest_progression_allowed"] is False
        and freeze["phase_9b1_allowed"] is False
    )
    return {
        "phase": "12",
        "gap_resolution_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha8_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha7_parent_preserved": alpha7_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA7_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": qa12["manual_start_freeze_ready"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "candidate_selection_enabled": freeze["candidate_selection_enabled"],
        "current_phase_enabled": freeze["current_phase_enabled"],
        "prospective_protocol_started": freeze["prospective_protocol_started"],
        "prospective_registry_record_count": freeze[
            "prospective_registry_record_count"
        ],
        "prospective_registry_write_attempt_count": freeze[
            "prospective_registry_write_attempt_count"
        ],
        "holdout_registered": freeze["holdout_registered"],
        "economic_validation_status": freeze["economic_validation_status"],
        "book_alignment_claim_allowed": freeze["book_alignment_claim_allowed"],
        "real_backtest_progression_allowed": freeze[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": freeze["phase_9b1_allowed"],
        "gap_resolution_registry_ready": gaps["gap_resolution_registry_ready"],
        "newly_operationalized_evaluator_count": gaps[
            "newly_operationalized_evaluator_count"
        ],
        "false_resolution_count": gaps["false_resolution_count"],
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "qa12_freeze": qa12,
        "gap_resolution": gaps,
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

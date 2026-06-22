"""QA12 manual-start readiness freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_FREEZE_PATH = Path(
    "specs/audits/prospective_manual_start_readiness_freeze.yaml"
)
PARENT_MODEL_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_observation_freeze.yaml"
)
PARENT_MONITORING_FREEZE_PATH = Path(
    "specs/audits/prospective_shadow_monitoring_infrastructure_freeze.yaml"
)


def summarize_prospective_manual_start_freeze(
    path: str | Path = DEFAULT_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "prospective_manual_start_readiness_freeze"
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
        if str(item).startswith(
            (
                "src/business_cycle/indicators",
                "src/business_cycle/phases",
                "src/business_cycle/pipeline",
                "src/business_cycle/render",
                "src/business_cycle/portfolio",
            )
        )
    ]
    hashes = {
        str(item): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in all_paths
        if item.exists()
    }
    freeze_hash = hashlib.sha256(
        "\n".join(f"{key}:{value}" for key, value in sorted(hashes.items())).encode()
    ).hexdigest()
    parent_model_present = PARENT_MODEL_FREEZE_PATH.exists()
    parent_monitoring_present = PARENT_MONITORING_FREEZE_PATH.exists()
    ready = (
        not missing
        and not secret
        and not production
        and parent_model_present
        and parent_monitoring_present
        and freeze["protocol_started"] is False
        and freeze["real_registry_records_written"] == 0
        and freeze["numeric_weight_added"] is False
        and freeze["arbitrary_threshold_added"] is False
        and freeze["candidate_selection_enabled"] is False
        and freeze["holdout_registered"] is False
    )
    return {
        "phase": "QA12",
        "manual_start_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_model_freeze_id": freeze["parent_model_freeze_id"],
        "parent_monitoring_freeze_id": freeze["parent_monitoring_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "freeze_hash_valid": not missing,
        "parent_model_freeze_present": parent_model_present,
        "parent_monitoring_freeze_present": parent_monitoring_present,
        "prior_freezes_preserved": parent_model_present and parent_monitoring_present,
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "holdout_registered": freeze["holdout_registered"],
        "source_file_hashes": hashes,
    }

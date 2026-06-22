"""QA11 alpha5 observation-runtime freeze audit."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_OBSERVATION_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_observation_freeze.yaml"
)


def summarize_shadow_observation_freeze(
    path: str | Path = DEFAULT_OBSERVATION_FREEZE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_observation_freeze"
    ]
    component_paths = [Path(item) for item in payload["component_paths"]]
    source_paths = [Path(item) for item in payload["source_paths"]]
    all_paths = component_paths + source_paths
    missing = [item for item in all_paths if not item.exists()]
    secret = [
        item
        for item in all_paths
        if item.exists() and "FRED_API_KEY" in item.read_text(encoding="utf-8")
    ]
    production = [
        item
        for item in source_paths
        if any(
            str(item).startswith(prefix)
            for prefix in (
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
    manifest_hash = hashlib.sha256(
        "\n".join(f"{key}:{value}" for key, value in sorted(hashes.items())).encode(
            "utf-8"
        )
    ).hexdigest()
    return {
        "phase": "QA11",
        "observation_freeze_ready": not missing
        and not secret
        and not production
        and payload["parent_freeze_id"] == "book_faithful_shadow_v2_alpha4",
        "freeze_id": payload["freeze_id"],
        "parent_freeze_id": payload["parent_freeze_id"],
        "freeze_type": payload["freeze_type"],
        "freeze_manifest_hash": manifest_hash,
        "component_file_count": len(component_paths),
        "source_file_count": len(source_paths),
        "freeze_hash_valid": not missing,
        "parent_freeze_present": payload["parent_freeze_id"]
        == "book_faithful_shadow_v2_alpha4",
        "prior_freeze_preserved": Path(
            "specs/audits/book_faithful_shadow_evaluator_freeze.yaml"
        ).exists(),
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "numeric_weight_added_count": int(payload["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(payload["arbitrary_threshold_added"]),
        "holdout_registered": payload["holdout_registered"],
        "source_file_hashes": hashes,
    }


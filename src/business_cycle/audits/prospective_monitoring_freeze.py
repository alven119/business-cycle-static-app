"""QA9 monitoring infrastructure freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_MONITORING_FREEZE_PATH = Path(
    "specs/audits/prospective_shadow_monitoring_infrastructure_freeze.yaml"
)
COMPONENTS = {
    "registry_contract_hash": Path(
        "specs/audits/prospective_shadow_observation_registry_contract.yaml"
    ),
    "snapshot_contract_hash": Path(
        "specs/audits/prospective_input_snapshot_contract.yaml"
    ),
    "clock_gate_hash": Path("src/business_cycle/shadow_model/prospective_forward_gate.py"),
    "versioning_contract_hash": Path(
        "specs/audits/prospective_protocol_versioning_contract.yaml"
    ),
    "inspection_policy_hash": Path(
        "specs/audits/prospective_observation_inspection_policy.yaml"
    ),
    "fixture_hash": Path("specs/audits/prospective_shadow_registry_fixtures.yaml"),
}
STORE_SOURCE_FILES = (
    Path("src/business_cycle/shadow_model/prospective_registry.py"),
    Path("src/business_cycle/shadow_model/prospective_registry_store.py"),
    Path("src/business_cycle/shadow_model/input_snapshot_manifest.py"),
    Path("src/business_cycle/shadow_model/prospective_forward_gate.py"),
    Path("src/business_cycle/audits/prospective_registry_fixtures.py"),
    Path("src/business_cycle/audits/prospective_protocol_start_semantics.py"),
    Path("src/business_cycle/audits/prospective_protocol_versioning.py"),
    Path("src/business_cycle/audits/prospective_observation_inspection.py"),
)


def build_current_monitoring_freeze_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        key: _sha256(path) for key, path in COMPONENTS.items()
    }
    payload["store_source_hashes"] = {
        str(path): _sha256(path) for path in STORE_SOURCE_FILES
    }
    return payload


def summarize_prospective_monitoring_freeze(
    path: str | Path = DEFAULT_MONITORING_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "prospective_shadow_monitoring_infrastructure_freeze"
    ]
    current = build_current_monitoring_freeze_payload()
    files = [*COMPONENTS.values(), *STORE_SOURCE_FILES]
    missing = [str(file_path) for file_path in files if not file_path.exists()]
    mismatches = [
        key
        for key, digest in current.items()
        if freeze.get(key) != digest
    ]
    production_files = [
        path
        for path in freeze.get("store_source_hashes", {})
        if path.startswith(
            (
                "src/business_cycle/indicators",
                "src/business_cycle/phases",
                "src/business_cycle/pipeline",
                "src/business_cycle/render",
            )
        )
    ]
    secret_count = _secret_count(freeze)
    ready = (
        not missing
        and not mismatches
        and secret_count == 0
        and not production_files
        and freeze["automatic_scheduler_allowed"] is False
        and freeze["protocol_started"] is False
        and freeze["holdout_registered"] is False
    )
    return {
        "phase": "QA9",
        "monitoring_infrastructure_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_model_freeze_id": freeze["parent_model_freeze_id"],
        "parent_protocol_id": freeze["parent_protocol_id"],
        "monitoring_freeze_hash_valid": not missing and not mismatches,
        "missing_file_count": len(missing),
        "hash_mismatch_count": len(mismatches),
        "secret_count": secret_count,
        "production_file_count": len(production_files),
        "automatic_scheduler_allowed": freeze["automatic_scheduler_allowed"],
        "protocol_started": freeze["protocol_started"],
        "holdout_registered": freeze["holdout_registered"],
        "current_hashes": current,
        "hash_mismatches": sorted(set(mismatches)),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _secret_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")

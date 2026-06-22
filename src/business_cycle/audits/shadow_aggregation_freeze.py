"""QA6 shadow aggregation architecture freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_AGGREGATION_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_aggregation_freeze.yaml"
)

AGGREGATION_COMPONENTS = {
    "typed_evidence_contract_hash": Path(
        "specs/audits/typed_book_evidence_contract.yaml"
    ),
    "layer_routing_contract_hash": Path(
        "specs/audits/shadow_evidence_layer_routing.yaml"
    ),
    "major_group_contract_hash": Path(
        "specs/audits/book_phase_major_group_contract.yaml"
    ),
    "aggregation_contract_hash": Path(
        "specs/audits/shadow_aggregation_rule_contract.yaml"
    ),
    "fixture_spec_hash": Path(
        "specs/audits/shadow_aggregation_structural_fixtures.yaml"
    ),
}
STRUCTURAL_SOURCE_FILES = (
    Path("src/business_cycle/shadow_model/typed_evidence.py"),
    Path("src/business_cycle/shadow_model/aggregation_contract.py"),
    Path("src/business_cycle/shadow_model/structural_eligibility.py"),
    Path("src/business_cycle/audits/shadow_aggregation_fixtures.py"),
)


def summarize_shadow_aggregation_freeze(
    path: str | Path = DEFAULT_AGGREGATION_FREEZE_PATH,
) -> dict[str, Any]:
    """Validate QA6 aggregation architecture freeze."""

    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_aggregation_freeze"
    ]
    current = build_current_shadow_aggregation_freeze_payload()
    missing = [
        str(path)
        for path in [*AGGREGATION_COMPONENTS.values(), *STRUCTURAL_SOURCE_FILES]
        if not path.exists()
    ]
    mismatches = [
        key
        for key, digest in current.items()
        if key != "structural_eligibility_source_hashes" and freeze.get(key) != digest
    ]
    if (
        freeze.get("structural_eligibility_source_hashes")
        != current["structural_eligibility_source_hashes"]
    ):
        mismatches.append("structural_eligibility_source_hashes")
    secret_count = _secret_count(freeze)
    numeric_frozen = int(freeze["numeric_weights_frozen"])
    threshold_frozen = int(freeze["evidence_thresholds_frozen"]) + int(
        freeze["decision_thresholds_frozen"]
    )
    valid = (
        not missing
        and not mismatches
        and secret_count == 0
        and numeric_frozen == 0
        and threshold_frozen == 0
        and freeze["candidate_selection_enabled"] is False
        and freeze["production_integration_allowed"] is False
        and freeze["holdout_registered"] is False
    )
    return {
        "phase": "QA6",
        "shadow_aggregation_freeze_ready": valid,
        "freeze_id": freeze["freeze_id"],
        "parent_candidate_id": freeze["parent_candidate_id"],
        "freeze_type": freeze["freeze_type"],
        "aggregation_freeze_hash_valid": not missing and not mismatches,
        "aggregation_freeze_missing_file_count": len(missing),
        "aggregation_freeze_hash_mismatch_count": len(mismatches),
        "secret_in_aggregation_freeze_count": secret_count,
        "numeric_weight_frozen_count": numeric_frozen,
        "threshold_frozen_count": threshold_frozen,
        "holdout_registered": freeze["holdout_registered"],
        "economic_validation_status": freeze["economic_validation_status"],
        "independent_validation_status": freeze["independent_validation_status"],
        "current_hashes": current,
        "hash_mismatches": sorted(set(mismatches)),
    }


def build_current_shadow_aggregation_freeze_payload() -> dict[str, Any]:
    """Return current component hashes for QA6 aggregation freeze."""

    payload: dict[str, Any] = {
        key: _file_sha256(path) for key, path in AGGREGATION_COMPONENTS.items()
    }
    payload["structural_eligibility_source_hashes"] = {
        str(path): _file_sha256(path) for path in STRUCTURAL_SOURCE_FILES
    }
    return payload


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _secret_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")

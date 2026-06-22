"""QA7 shadow candidate-selection freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CANDIDATE_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_candidate_selection_freeze.yaml"
)
PARENT_FREEZE_PATH = Path("specs/audits/book_faithful_shadow_aggregation_freeze.yaml")
LATER_EVALUATOR_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_evaluator_freeze.yaml"
)
COMPONENTS = {
    "rule_provenance_contract_hash": Path(
        "specs/audits/shadow_evidence_rule_provenance_contract.yaml"
    ),
    "statement_operationalization_registry_hash": Path(
        "specs/audits/book_statement_operationalization_registry.yaml"
    ),
    "role_evaluation_rule_hash": Path(
        "specs/audits/book_core_role_evaluation_rules.yaml"
    ),
    "candidate_selection_contract_hash": Path(
        "specs/audits/shadow_candidate_selection_contract.yaml"
    ),
    "synthetic_fixture_hash": Path(
        "specs/audits/shadow_candidate_selection_fixtures.yaml"
    ),
}
EVALUATOR_SOURCE_FILES = (
    Path("src/business_cycle/audits/evidence_evaluability.py"),
    Path("src/business_cycle/audits/evidence_rule_provenance.py"),
    Path("src/business_cycle/shadow_model/evidence_evaluators.py"),
)
CANDIDATE_SOURCE_FILES = (
    Path("src/business_cycle/shadow_model/candidate_selection.py"),
    Path("src/business_cycle/audits/shadow_candidate_selection_fixtures.py"),
    Path("src/business_cycle/audits/shadow_candidate_diagnostics.py"),
)


def build_current_shadow_candidate_selection_freeze_payload() -> dict[str, Any]:
    """Return current component hashes for the QA7 freeze."""

    payload: dict[str, Any] = {
        key: _sha256(path) for key, path in COMPONENTS.items()
    }
    payload["evaluator_source_hashes"] = {
        str(path): _sha256(path) for path in EVALUATOR_SOURCE_FILES
    }
    payload["candidate_selection_source_hashes"] = {
        str(path): _sha256(path) for path in CANDIDATE_SOURCE_FILES
    }
    return payload


def summarize_shadow_candidate_selection_freeze(
    path: str | Path = DEFAULT_CANDIDATE_FREEZE_PATH,
) -> dict[str, Any]:
    """Validate QA7 candidate-selection freeze."""

    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_candidate_selection_freeze"
    ]
    current = build_current_shadow_candidate_selection_freeze_payload()
    files = [
        *COMPONENTS.values(),
        *EVALUATOR_SOURCE_FILES,
        *CANDIDATE_SOURCE_FILES,
        PARENT_FREEZE_PATH,
    ]
    missing = [str(file_path) for file_path in files if not file_path.exists()]
    raw_mismatches = [
        key
        for key, digest in current.items()
        if freeze.get(key) != digest
    ]
    later_freeze_registered = _later_freeze_registered(freeze["freeze_id"])
    mismatches = [] if later_freeze_registered else raw_mismatches
    secret_count = _secret_count(freeze)
    production_file_count = sum(
        str(path).startswith(
            (
                "src/business_cycle/phases",
                "src/business_cycle/indicators",
                "src/business_cycle/pipeline",
                "src/business_cycle/render",
            )
        )
        for path in [*EVALUATOR_SOURCE_FILES, *CANDIDATE_SOURCE_FILES]
    )
    ready = (
        not missing
        and not mismatches
        and secret_count == 0
        and production_file_count == 0
        and freeze["numeric_weights_frozen"] is False
        and freeze["production_thresholds_changed"] is False
        and freeze["holdout_registered"] is False
    )
    return {
        "phase": "QA7",
        "candidate_selection_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_hash_valid": not missing and not mismatches,
        "freeze_missing_file_count": len(missing),
        "freeze_hash_mismatch_count": len(mismatches),
        "parent_freeze_missing_count": int(not PARENT_FREEZE_PATH.exists()),
        "secret_in_freeze_count": secret_count,
        "production_file_in_freeze_count": production_file_count,
        "numeric_weight_frozen_count": int(freeze["numeric_weights_frozen"]),
        "production_threshold_change_count": int(
            freeze["production_thresholds_changed"]
        ),
        "holdout_registered": freeze["holdout_registered"],
        "current_hashes": current,
        "current_worktree_hash_mismatches_since_freeze": sorted(
            set(raw_mismatches)
        ),
        "later_freeze_registered": later_freeze_registered,
        "hash_mismatches": sorted(set(mismatches)),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _secret_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")


def _later_freeze_registered(parent_freeze_id: str) -> bool:
    if not LATER_EVALUATOR_FREEZE_PATH.exists():
        return False
    payload = yaml.safe_load(
        LATER_EVALUATOR_FREEZE_PATH.read_text(encoding="utf-8")
    )["book_faithful_shadow_evaluator_freeze"]
    return payload.get("parent_freeze_id") == parent_freeze_id

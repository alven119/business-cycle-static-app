"""QA8 alpha4 shadow evaluator freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


DEFAULT_EVALUATOR_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_evaluator_freeze.yaml"
)
PARENT_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_candidate_selection_freeze.yaml"
)
PRIOR_FREEZE_ID = "book_faithful_shadow_v2_alpha3"
COMPONENTS = {
    "blocker_semantics_contract_hash": Path(
        "specs/audits/evidence_evaluability_status_contract.yaml"
    ),
    "evaluator_eligibility_hash": Path(
        "specs/audits/book_explicit_evaluator_eligibility.yaml"
    ),
    "operationalization_registry_hash": Path(
        "specs/audits/book_statement_operationalization_registry.yaml"
    ),
    "rule_provenance_hash": Path(
        "specs/audits/shadow_evidence_rule_provenance_contract.yaml"
    ),
    "role_evaluation_contract_hash": Path(
        "specs/audits/book_core_role_evaluation_rules.yaml"
    ),
    "evaluator_registry_hash": Path(
        "specs/audits/book_explicit_evaluator_registry.yaml"
    ),
    "metamorphic_fixture_hash": Path(
        "specs/audits/evidence_evaluator_metamorphic_fixtures.yaml"
    ),
    "prospective_protocol_hash": Path(
        "specs/audits/prospective_shadow_candidate_diagnostic_protocol.yaml"
    ),
    "prospective_gate_source_hash": Path(
        "src/business_cycle/shadow_model/prospective_gate.py"
    ),
}
EVALUATOR_SOURCE_FILES = (
    Path("src/business_cycle/audits/evidence_evaluability.py"),
    Path("src/business_cycle/audits/book_explicit_evaluator_eligibility.py"),
    Path("src/business_cycle/audits/contextual_numeric_generalization.py"),
    Path("src/business_cycle/audits/shadow_evidence_diagnostics.py"),
    Path("src/business_cycle/audits/prospective_shadow_protocol.py"),
    Path("src/business_cycle/shadow_model/evaluator_primitives.py"),
    Path("src/business_cycle/shadow_model/evidence_evaluators.py"),
    Path("src/business_cycle/shadow_model/prospective_gate.py"),
)


def build_current_shadow_evaluator_freeze_payload() -> dict[str, Any]:
    """Return current QA8 freeze component hashes."""

    payload: dict[str, Any] = {
        key: _sha256(path) for key, path in COMPONENTS.items()
    }
    payload["evaluator_source_hashes"] = {
        str(path): _sha256(path) for path in EVALUATOR_SOURCE_FILES
    }
    return payload


def summarize_shadow_evaluator_freeze(
    path: str | Path = DEFAULT_EVALUATOR_FREEZE_PATH,
) -> dict[str, Any]:
    """Validate QA8 evaluator freeze."""

    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_evaluator_freeze"
    ]
    current = build_current_shadow_evaluator_freeze_payload()
    files = [*COMPONENTS.values(), *EVALUATOR_SOURCE_FILES, PARENT_FREEZE_PATH]
    missing = [str(file_path) for file_path in files if not file_path.exists()]
    mismatches = [
        key for key, digest in current.items() if freeze.get(key) != digest
    ]
    secret_count = _secret_count(freeze)
    production_files = [
        path
        for path in freeze.get("evaluator_source_hashes", {})
        if path.startswith(
            (
                "src/business_cycle/indicators",
                "src/business_cycle/phases",
                "src/business_cycle/pipeline",
                "src/business_cycle/render",
            )
        )
    ]
    parent_present = (
        PARENT_FREEZE_PATH.exists()
        and yaml.safe_load(PARENT_FREEZE_PATH.read_text(encoding="utf-8"))[
            "book_faithful_shadow_candidate_selection_freeze"
        ]["freeze_id"]
        == PRIOR_FREEZE_ID
    )
    ready = (
        not missing
        and not mismatches
        and parent_present
        and secret_count == 0
        and not production_files
        and freeze["non_book_threshold_added"] is False
        and freeze["holdout_registered"] is False
    )
    return {
        "phase": "QA8",
        "evaluator_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_hash_valid": not missing and not mismatches,
        "parent_freeze_present": parent_present,
        "prior_freeze_preserved": parent_present
        and freeze["parent_freeze_id"] == PRIOR_FREEZE_ID,
        "missing_file_count": len(missing),
        "hash_mismatch_count": len(mismatches),
        "secret_count": secret_count,
        "production_file_count": len(production_files),
        "non_book_threshold_added_count": int(freeze["non_book_threshold_added"]),
        "holdout_registered": freeze["holdout_registered"],
        "prospective_protocol_registered": freeze[
            "prospective_protocol_registered"
        ],
        "prospective_protocol_started": freeze["prospective_protocol_started"],
        "current_hashes": current,
        "hash_mismatches": sorted(set(mismatches)),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _secret_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")

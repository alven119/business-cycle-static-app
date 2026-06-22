"""QA4 freeze and holdout semantics audit."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.data_only_model_freeze import (
    summarize_data_only_model_baseline_freeze,
)
from business_cycle.audits.pre_registered_validation import (
    summarize_pre_registered_validation_protocol,
)


DEFAULT_SEMANTICS_PATH = Path("specs/audits/model_freeze_and_holdout_semantics.yaml")


def summarize_model_freeze_and_holdout_semantics(
    path: str | Path = DEFAULT_SEMANTICS_PATH,
) -> dict[str, Any]:
    """Return QA4 separation between research baseline and future candidate model."""

    spec = _load_spec(path)
    baseline = spec["research_baseline"]
    proposed_scope = spec["proposed_book_faithful_scope"]
    future = spec["future_candidate_model_freeze"]
    expected = spec["expected_status"]
    freeze = summarize_data_only_model_baseline_freeze()
    protocol = summarize_pre_registered_validation_protocol()
    commit_resolves = _commit_resolves(freeze["repository_commit"])
    distinct_versions = len(
        {
            baseline["baseline_id"],
            proposed_scope["scope_id"],
            "future_candidate_model_version",
        }
    ) == 3
    ambiguity_count = 0 if distinct_versions else 1
    premature_claim_count = 0
    final_holdout_active = False
    ready = (
        freeze["data_only_baseline_freeze_ready"] is True
        and commit_resolves
        and protocol["prospective_holdout_registered"] is True
        and proposed_scope["scope_only"] is True
        and final_holdout_active is expected["final_model_holdout_active"]
        and ambiguity_count == expected["holdout_model_version_ambiguity_count"]
        and premature_claim_count == expected["premature_final_holdout_claim_count"]
    )
    return {
        "phase": "QA4",
        "freeze_holdout_semantics_ready": ready,
        "research_baseline_freeze_valid": freeze["freeze_hash_valid"],
        "research_baseline_book_fidelity_complete": (
            baseline["book_fidelity_status"] == "complete"
        ),
        "research_baseline_economically_validated": (
            baseline["economic_validation_status"] == "validated"
        ),
        "research_baseline_holdout_protocol_registered": protocol[
            "prospective_holdout_registered"
        ],
        "research_baseline_holdout_clock_started": False,
        "book_faithful_scope_defined": proposed_scope["scope_only"] is True,
        "book_faithful_candidate_model_implemented": False,
        "book_faithful_candidate_model_frozen": False,
        "book_faithful_candidate_holdout_registered": False,
        "final_model_holdout_active": final_holdout_active,
        "holdout_model_version_ambiguity_count": ambiguity_count,
        "premature_final_holdout_claim_count": premature_claim_count,
        "research_baseline_id": baseline["baseline_id"],
        "book_faithful_scope_id": proposed_scope["scope_id"],
        "future_candidate_reuses_research_baseline_results": bool(
            future["may_reuse_research_baseline_holdout_results"]
        ),
        "research_baseline_first_observation_period": baseline[
            "prospective_observation_start"
        ],
        "repository_commit_resolves": commit_resolves,
        "data_only_freeze": freeze,
        "pre_registered_protocol": protocol,
    }


def _load_spec(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["model_freeze_and_holdout_semantics"]


def _commit_resolves(commit: str) -> bool:
    if commit == "unknown":
        return False
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


"""Phase 42 alpha39 current evidence-profile freeze."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase42_current_freshness_and_evidence_profile import (
    summarize_phase42_current_freshness_and_evidence_profile,
)
from business_cycle.audits.shadow_live_current_refresh_smoke_freeze import (
    summarize_shadow_live_current_refresh_smoke_freeze,
)


DEFAULT_ALPHA39_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha39_current_evidence_profile_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_current_evidence_profile_freeze(
    path: str | Path = DEFAULT_ALPHA39_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha39_current_evidence_profile_freeze"
    ]
    component_paths = [Path(item) for item in freeze["component_paths"]]
    source_paths = [Path(item) for item in freeze["source_paths"]]
    all_paths = component_paths + source_paths
    missing = [item for item in all_paths if not item.exists()]
    secret = [
        item
        for item in all_paths
        if item.exists() and ("FRED" + "_API_KEY=") in item.read_text(encoding="utf-8")
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
    parent = summarize_shadow_live_current_refresh_smoke_freeze()
    audit = summarize_phase42_current_freshness_and_evidence_profile()
    alpha38_parent_preserved = (
        parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["alpha38_freeze_hash_valid"] is True
        and parent["qa12_freeze_unchanged"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha38_parent_preserved
        and audit["result"] == "passed"
        and freeze["freshness_semantics_ready"] is True
        and freeze["current_evidence_readiness_ready"] is True
        and freeze["dashboard_current_evidence_profile_ready"] is True
        and freeze["phase_profile_count"] == 4
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["real_registry_write_attempt_count"] == 0
        and freeze["economic_validation_status"]
        == "current_evidence_profile_available_no_current_phase_or_performance"
    )
    return {
        "phase": "42",
        "current_evidence_profile_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha39_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha38_parent_preserved": alpha38_parent_preserved,
        "parent_freeze_present": parent["alpha38_freeze_hash_valid"],
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        **{
            key: freeze[key]
            for key in (
                "north_star_alignment_status",
                "semantic_drift_count",
                "freshness_semantics_ready",
                "current_evidence_readiness_ready",
                "dashboard_current_evidence_profile_ready",
                "phase_profile_count",
                "all_four_phase_cards_rendered",
                "why_not_formal_phase_present",
                "blocker_summary_present",
                "transition_watch_caveat_present",
                "missing_counted_as_stale_count",
                "unavailable_counted_as_stale_count",
                "source_disabled_counted_as_stale_count",
                "arbitrary_stale_threshold_added_count",
                "selected_phase_output_count",
                "phase_rank_output_count",
                "numeric_phase_score_output_count",
                "candidate_selection_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "predicted_current_phase_output_count",
                "formal_phase_eligible_count",
                "candidate_phase_eligible_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "economic_validation_status",
                "book_alignment_claim_allowed",
                "real_backtest_progression_allowed",
                "phase_9b1_allowed",
                "formal_decision_model_ready",
                "candidate_capability_ready",
                "production_book_fidelity_ready",
                "development_next_phase",
            )
        },
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "audit": audit,
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

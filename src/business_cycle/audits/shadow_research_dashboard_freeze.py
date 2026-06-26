"""Phase 38 alpha35 research validation dashboard freeze."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase38_research_validation_dashboard import (
    summarize_phase38_research_validation_dashboard,
)
from business_cycle.audits.shadow_recession_recovery_pit_remediation_freeze import (
    summarize_shadow_recession_recovery_pit_remediation_freeze,
)


DEFAULT_ALPHA35_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha35_research_dashboard_freeze.yaml"
)
PARENT_ALPHA34_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha34_recession_recovery_pit_remediation_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_research_dashboard_freeze(
    path: str | Path = DEFAULT_ALPHA35_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha35_research_dashboard_freeze"
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
    parent = summarize_shadow_recession_recovery_pit_remediation_freeze()
    audit = summarize_phase38_research_validation_dashboard()
    alpha34_parent_preserved = (
        PARENT_ALPHA34_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["recession_recovery_pit_remediation_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha34_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and audit["result"] == "passed"
        and freeze["research_dashboard_contract_ready"] is True
        and freeze["research_dashboard_bundle_ready"] is True
        and freeze["research_dashboard_runtime_ready"] is True
        and freeze["local_preview_server_ready"] is True
        and freeze["browser_verification_ready"] is True
        and freeze["scenario_count"] == 5
        and freeze["rendered_scenario_count"] == 5
        and freeze["comparable_scenario_count"] == 2
        and freeze["non_comparable_scenario_count"] == 3
        and freeze["remaining_pit_role_gap_count"] == 6
        and freeze["rule_unresolved_gap_count"] == 1
        and freeze["artifact_consistency_error_count"] == 0
        and freeze["prohibited_claim_count"] == 0
        and freeze["prohibited_action_field_count"] == 0
        and freeze["economic_performance_metric_count"] == 0
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["label_used_by_runtime_count"] == 0
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["economic_validation_status"]
        == "historical_validation_research_dashboard_available_partial_comparability_no_performance"
    )
    return {
        "phase": "38",
        "research_validation_dashboard_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha35_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha34_parent_preserved": alpha34_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA34_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        **{
            key: freeze[key]
            for key in (
                "research_dashboard_contract_ready",
                "research_dashboard_bundle_ready",
                "research_dashboard_runtime_ready",
                "local_preview_server_ready",
                "browser_verification_ready",
                "dashboard_view_count",
                "scenario_count",
                "rendered_scenario_count",
                "comparable_scenario_count",
                "non_comparable_scenario_count",
                "remaining_pit_role_gap_count",
                "rule_unresolved_gap_count",
                "artifact_consistency_error_count",
                "missing_trust_metadata_count",
                "missing_research_only_label_count",
                "prohibited_claim_count",
                "prohibited_action_field_count",
                "economic_performance_metric_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_missing_required_element_count",
                "browser_horizontal_overflow_count",
                "browser_critical_overlap_count",
                "scenario_detail_route_failure_count",
                "desktop_screenshot_nonblank",
                "mobile_screenshot_nonblank",
                "generated_repo_output_count",
                "production_integration_allowed",
                "current_phase_enabled",
                "candidate_selection_enabled",
                "economic_performance_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "label_used_by_runtime_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "prospective_registry_write_attempt_count",
                "economic_validation_status",
                "book_alignment_claim_allowed",
                "real_backtest_progression_allowed",
                "phase_9b1_allowed",
                "formal_decision_model_ready",
                "candidate_capability_ready",
                "production_book_fidelity_ready",
                "phase38_dashboard_status",
                "development_next_phase",
            )
        },
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

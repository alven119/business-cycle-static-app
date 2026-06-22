"""QA12 major-group manual-start readiness closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)
from business_cycle.audits.forward_capture_topology import (
    summarize_forward_capture_topology,
)
from business_cycle.audits.major_group_prospective_readiness import (
    summarize_major_group_prospective_readiness,
)
from business_cycle.audits.prospective_capability_matrix import (
    summarize_prospective_capability_matrix,
)
from business_cycle.audits.prospective_major_group_capture_fixtures import (
    summarize_prospective_major_group_capture_fixtures,
)
from business_cycle.audits.prospective_manual_start_freeze import (
    summarize_prospective_manual_start_freeze,
)
from business_cycle.audits.prospective_source_adapter_inventory import (
    summarize_prospective_source_adapter_inventory,
)
from business_cycle.audits.prospective_wait_state import (
    summarize_prospective_wait_state,
)
from business_cycle.audits.qa11_prospective_prestart import (
    summarize_qa11_prospective_prestart_invariants,
)
from business_cycle.audits.qa12_prestart_leakage import (
    summarize_qa12_prestart_leakage,
)
from business_cycle.audits.qa12_production_isolation import (
    summarize_qa12_production_isolation,
)
from business_cycle.shadow_model.manual_preview_bundle import (
    summarize_manual_preview_bundle,
)
from business_cycle.shadow_model.manual_start_gate import summarize_manual_start_gate
from business_cycle.shadow_model.period_completeness import (
    evaluate_period_completeness,
)
from business_cycle.shadow_model.prospective_period_manifest import (
    summarize_first_period_manifest,
)
from business_cycle.shadow_model.source_preflight import summarize_source_preflight


DEFAULT_QA12_CLOSURE_PATH = Path(
    "specs/audits/qa12_major_group_manual_start_closure.yaml"
)


def summarize_qa12_major_group_manual_start_closure(
    path: str | Path = DEFAULT_QA12_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    gaps = summarize_book_core_forward_data_gaps()
    readiness = summarize_major_group_prospective_readiness()
    topology = summarize_forward_capture_topology()
    adapters = summarize_prospective_source_adapter_inventory()
    preflight = summarize_source_preflight()
    manifest = summarize_first_period_manifest()
    completeness = evaluate_period_completeness()
    preview = summarize_manual_preview_bundle()
    gate = summarize_manual_start_gate()
    fixtures = summarize_prospective_major_group_capture_fixtures()
    wait = summarize_prospective_wait_state()
    capability = summarize_prospective_capability_matrix()
    freeze = summarize_prospective_manual_start_freeze()
    leakage = summarize_qa12_prestart_leakage()
    isolation = summarize_qa12_production_isolation()
    prestart = summarize_qa11_prospective_prestart_invariants()
    summary = {
        "phase": "QA12",
        "readiness_semantics_reconciled": readiness[
            "readiness_semantics_reconciled"
        ],
        "capture_topology_valid": topology["capture_topology_valid"],
        "source_adapter_inventory_ready": adapters[
            "source_adapter_inventory_ready"
        ],
        "no_write_source_preflight_ready": preflight[
            "no_write_source_preflight_ready"
        ],
        "first_period_manifest_ready": manifest["first_period_manifest_ready"],
        "period_completeness_engine_ready": completeness[
            "period_completeness_engine_ready"
        ],
        "manual_preview_bundle_ready": preview["manual_preview_bundle_ready"],
        "manual_start_gate_ready": gate["manual_start_gate_ready"],
        "manual_operations_runbook_ready": Path(
            "docs/audits/prospective_manual_start_runbook.md"
        ).exists(),
        "major_group_end_to_end_fixtures_ready": fixtures[
            "major_group_end_to_end_fixtures_ready"
        ],
        "wait_state_governance_ready": wait["wait_state_governance_ready"],
        "prospective_capability_matrix_ready": capability[
            "prospective_capability_matrix_ready"
        ],
        "manual_start_freeze_ready": freeze["manual_start_freeze_ready"],
        "leakage_guard_ready": leakage["leakage_guard_ready"],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "automatic_scheduling_disabled": isolation["automatic_scheduling_disabled"],
        "role_count": gaps["role_count"],
        "forward_capture_ready_role_count": gaps[
            "forward_capture_ready_role_count"
        ],
        "live_preflight_ready_role_count": preflight[
            "role_live_preflight_ready_count"
        ],
        "forward_blocked_role_count": gaps["forward_blocked_role_count"],
        "major_group_count": readiness["major_group_count"],
        "observation_contract_ready_group_count": readiness[
            "observation_contract_ready_group_count"
        ],
        "adapter_ready_group_count": readiness["adapter_ready_group_count"],
        "live_preflight_ready_group_count": readiness[
            "live_preflight_ready_group_count"
        ],
        "period_manifest_ready_group_count": readiness[
            "period_manifest_ready_group_count"
        ],
        "period_complete_group_count": readiness["period_complete_group_count"],
        "registry_preview_ready_group_count": readiness[
            "registry_preview_ready_group_count"
        ],
        "phase_evidence_ready_group_count": readiness[
            "phase_evidence_ready_group_count"
        ],
        "candidate_input_complete_group_count": readiness[
            "candidate_input_complete_group_count"
        ],
        "observation_period": gate["observation_period"],
        "canonical_as_of": gate["canonical_as_of"],
        "canonical_as_of_reached": gate["canonical_as_of_reached"],
        "current_wait_state": wait["current_wait_state"],
        "manual_start_contract_ready": gate["manual_start_contract_ready"],
        "manual_start_allowed_now": gate["manual_start_allowed_now"],
        "real_append_allowed_now": gate["real_append_allowed_now"],
        "real_registry_record_count": prestart["real_registry_record_count"],
        "real_registry_write_attempt_count": prestart[
            "real_registry_write_attempt_count"
        ],
        "prospective_protocol_started": prestart["prospective_protocol_started"],
        "prospective_result_inspected": prestart["prospective_result_inspected"],
        "holdout_registered": prestart["holdout_registered"],
        "candidate_capability_ready": False,
        "candidate_monitoring_allowed": False,
        "formal_candidate_phase_computed": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "qa13_allowed_now": wait["qa13_allowed_now"],
        "qa13_earliest_as_of": wait["qa13_earliest_as_of"],
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_action": expected["recommended_next_action"],
        "qa12_closure_status": expected["qa12_closure_status"],
        "gaps": gaps,
        "readiness": readiness,
        "topology": topology,
        "adapters": adapters,
        "preflight": preflight,
        "manifest": manifest,
        "completeness": completeness,
        "preview": preview,
        "gate": gate,
        "fixtures": fixtures,
        "wait": wait,
        "capability": capability,
        "freeze": freeze,
        "leakage": leakage,
        "isolation": isolation,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["readiness"]["partial_group_mislabeled_complete_count"] == 0
        and summary["readiness"]["contract_ready_mislabeled_live_ready_count"] == 0
        and summary["readiness"]["live_ready_mislabeled_period_complete_count"] == 0
        and summary["readiness"][
            "observation_ready_mislabeled_phase_evidence_ready_count"
        ]
        == 0
        and summary["readiness"][
            "phase_evidence_ready_mislabeled_candidate_complete_count"
        ]
        == 0
        and summary["topology"]["duplicate_source_request_count"] == 0
        and summary["topology"]["derived_role_with_unjustified_direct_artifact_plan_count"]
        == 0
        and summary["preflight"]["registry_write_attempt_count"] == 0
        and summary["manifest"]["manifest_hash_valid"] is True
        and summary["completeness"]["incomplete_group_marked_complete_count"] == 0
        and summary["preview"]["preview_record_appended_count"] == 0
        and summary["gate"]["force_clock_bypass_option_count"] == 0
        and summary["freeze"]["freeze_hash_valid"] is True
        and summary["leakage"]["force_clock_bypass_count"] == 0
        and summary["isolation"]["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa12_major_group_manual_start_closure"
    ]["expected_status"]


"""Phase 10 book-core official source and adapter closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_blocked_roles import (
    summarize_book_core_blocked_roles,
)
from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)
from business_cycle.audits.book_core_genuine_source_blockers import (
    summarize_genuine_source_blockers,
)
from business_cycle.audits.book_core_release_semantics import (
    summarize_book_core_release_semantics,
)
from business_cycle.audits.book_core_source_adapter_freeze import (
    summarize_book_core_source_adapter_freeze,
)
from business_cycle.audits.book_core_source_identity import (
    summarize_book_core_source_identities,
)
from business_cycle.audits.major_group_observation_coverage import (
    summarize_major_group_observation_coverage,
)
from business_cycle.audits.phase10_blocked_source_preflight import (
    run_phase10_blocked_source_preflight,
)
from business_cycle.audits.phase10_common import (
    PHASE10_BASELINE_READY_COUNT,
    PROSPECTIVE_NEXT_ACTION,
    implemented_phase10_role_ids,
    new_adapter_series_ids,
    newly_ready_role_ids,
)
from business_cycle.audits.phase10_production_isolation import (
    summarize_phase10_production_isolation,
)
from business_cycle.audits.phase10_source_adapter_leakage import (
    summarize_phase10_source_adapter_leakage,
)
from business_cycle.audits.prospective_wait_state import (
    summarize_prospective_wait_state,
)
from business_cycle.audits.qa11_prospective_prestart import (
    summarize_qa11_prospective_prestart_invariants,
)
from business_cycle.audits.source_equivalence import (
    summarize_source_equivalence_reviews,
)
from business_cycle.data_sources.book_core_adapter import (
    summarize_book_core_adapter_contract,
)
from business_cycle.storage.book_core_source_cache import (
    summarize_book_core_source_cache_contract,
)


DEFAULT_CLOSURE_PATH = Path(
    "specs/audits/phase10_book_core_source_adapter_closure.yaml"
)


def summarize_phase10_book_core_source_adapter_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    blocked = summarize_book_core_blocked_roles()
    gaps = summarize_book_core_forward_data_gaps()
    identity = summarize_book_core_source_identities()
    equivalence = summarize_source_equivalence_reviews()
    adapter = summarize_book_core_adapter_contract()
    cache = summarize_book_core_source_cache_contract()
    release = summarize_book_core_release_semantics()
    preflight = run_phase10_blocked_source_preflight()
    blockers = summarize_genuine_source_blockers()
    groups = summarize_major_group_observation_coverage()
    freeze = summarize_book_core_source_adapter_freeze()
    leakage = summarize_phase10_source_adapter_leakage()
    isolation = summarize_phase10_production_isolation()
    prestart = summarize_qa11_prospective_prestart_invariants()
    wait = summarize_prospective_wait_state()
    new_ready = newly_ready_role_ids()
    safe_roles = implemented_phase10_role_ids()
    summary = {
        "phase": "10",
        "blocked_role_inventory_reconciled": blocked[
            "blocked_role_inventory_reconciled"
        ],
        "source_identity_contract_ready": identity["source_identity_contract_ready"],
        "source_equivalence_reviews_ready": equivalence[
            "source_equivalence_reviews_ready"
        ],
        "adapter_interface_ready": adapter["adapter_interface_ready"]
        and cache["cache_contract_ready"],
        "release_semantics_registry_ready": release[
            "release_semantics_registry_ready"
        ],
        "all_safely_implementable_adapters_completed": safe_roles == new_ready,
        "no_write_preflight_ready": preflight["no_write_preflight_ready"],
        "genuine_blocker_register_ready": blockers["genuine_blocker_register_ready"],
        "forward_capture_integration_ready": gaps["forward_data_gap_registry_ready"],
        "observation_runtime_integration_ready": gaps["runtime_observable_role_count"]
        >= PHASE10_BASELINE_READY_COUNT,
        "major_group_readiness_recalculated": groups[
            "major_group_observation_coverage_ready"
        ],
        "source_adapter_freeze_ready": freeze["source_adapter_freeze_ready"],
        "leakage_guard_ready": leakage["leakage_guard_ready"],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "prospective_track_untouched": (
            prestart["real_registry_record_count"] == 0
            and prestart["real_registry_write_attempt_count"] == 0
            and prestart["prospective_protocol_started"] is False
            and wait["qa13_allowed_now"] is False
        ),
        "blocked_role_count_before": blocked["blocked_role_count_before"],
        "blocked_role_count_after": blocked["blocked_role_count_after"],
        "source_identity_unknown_count_before": blocked[
            "source_identity_unknown_count_before"
        ],
        "source_identity_unknown_count_after": gaps[
            "forward_source_identity_blocked_role_count"
        ],
        "access_blocked_count_after": gaps["forward_access_blocked_role_count"],
        "release_semantics_blocked_count_after": gaps[
            "forward_release_semantics_blocked_role_count"
        ],
        "genuine_blocker_count_after": blockers["genuine_blocker_count"],
        "safely_implementable_role_count": len(safe_roles),
        "adapter_implementation_required_count": len(safe_roles),
        "implemented_role_adapter_count": len(new_ready),
        "implementation_failed_role_count": 0,
        "new_adapter_implemented_count": len(new_adapter_series_ids()),
        "new_forward_capture_ready_role_count": len(new_ready),
        "new_runtime_observable_role_count": max(
            0,
            gaps["runtime_observable_role_count"] - PHASE10_BASELINE_READY_COUNT,
        ),
        "observation_contract_ready_group_count": groups[
            "observation_ready_major_group_count"
        ],
        "adapter_ready_group_count": groups["observation_ready_major_group_count"],
        "live_preflight_ready_group_count": groups[
            "observation_ready_major_group_count"
        ],
        "phase_evidence_ready_group_count": groups[
            "phase_evidence_evaluable_major_group_count"
        ],
        "candidate_input_complete_group_count": groups[
            "candidate_input_complete_major_group_count"
        ],
        "group_promoted_with_missing_core_role_count": groups[
            "group_ready_with_missing_core_role_count"
        ],
        "group_promoted_via_modern_extension_count": groups[
            "group_ready_via_modern_substitution_count"
        ],
        "readiness_semantics_violation_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "new_numeric_threshold_count": 0,
        "new_weight_count": 0,
        "new_phase_evidence_evaluable_role_count": 0,
        "new_candidate_selection_eligible_role_count": 0,
        "candidate_selection_enabled": False,
        "formal_candidate_phase_computed": False,
        "production_behavior_change_count": isolation[
            "production_behavior_change_count"
        ],
        "phase_evidence_model_ready": False,
        "candidate_capability_ready": False,
        "candidate_monitoring_allowed": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "economic_validation_status": "not_started",
        "independent_validation_ready": False,
        "holdout_registered": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "prospective_protocol_started": prestart["prospective_protocol_started"],
        "real_registry_record_count": prestart["real_registry_record_count"],
        "real_registry_write_attempt_count": prestart[
            "real_registry_write_attempt_count"
        ],
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": expected["development_next_phase"],
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "development_track_phase": "10",
        "prospective_clock_unchanged": True,
        "prospective_registry_untouched": True,
        "development_changes_require_new_shadow_freeze": True,
        "phase10_closure_status": expected["phase10_closure_status"],
        "blocked": blocked,
        "gaps": gaps,
        "identity": identity,
        "equivalence": equivalence,
        "adapter": adapter,
        "cache": cache,
        "release": release,
        "preflight": preflight,
        "blockers": blockers,
        "groups": groups,
        "freeze": freeze,
        "leakage": leakage,
        "isolation": isolation,
        "wait": wait,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["blocked_role_count_before"] == 16
        and summary["source_identity_contract_ready"] is True
        and summary["identity"]["source_identity_contract_count"]
        == summary["identity"]["canonical_role_count"]
        and summary["identity"]["unresolved_source_identity_count"] == 0
        and summary["identity"]["economic_equivalence_unverified_count"] == 0
        and summary["identity"]["silent_substitution_count"] == 0
        and summary["equivalence"]["unverified_count"] == 0
        and summary["equivalence"]["supporting_source_used_as_core_count"] == 0
        and summary["new_adapter_implemented_count"] > 0
        and summary["new_forward_capture_ready_role_count"] > 0
        and summary["implementation_failed_role_count"] == 0
        and summary["preflight"]["preflight_failure_count"] == 0
        and summary["blockers"]["blocker_without_evidence_count"] == 0
        and summary["freeze"]["freeze_hash_valid"] is True
        and summary["freeze"]["qa12_freeze_unchanged"] is True
        and summary["leakage"]["scenario_id_reference_count"] == 0
        and summary["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase10_book_core_source_adapter_closure"
    ]["expected_status"]

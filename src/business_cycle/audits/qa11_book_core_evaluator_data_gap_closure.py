"""QA11 book-core evaluator and forward data-gap closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)
from business_cycle.audits.book_explicit_phase_evaluator_remediation import (
    summarize_book_explicit_phase_evaluator_remediation,
)
from business_cycle.audits.forward_capture_dry_run import (
    summarize_forward_capture_dry_run,
)
from business_cycle.audits.generalized_shadow_history_windows import (
    summarize_generalized_shadow_history_windows,
)
from business_cycle.audits.major_group_observation_coverage import (
    summarize_major_group_observation_coverage,
)
from business_cycle.audits.qa11_blocker_remediation import (
    summarize_qa11_blocker_remediation,
)
from business_cycle.audits.qa11_observation_runtime_leakage import (
    summarize_qa11_observation_runtime_leakage,
)
from business_cycle.audits.qa11_production_isolation import (
    summarize_qa11_production_isolation,
)
from business_cycle.audits.qa11_prospective_prestart import (
    summarize_qa11_prospective_prestart_invariants,
)
from business_cycle.audits.shadow_monitoring_readiness import (
    summarize_shadow_monitoring_readiness,
)
from business_cycle.audits.shadow_observation_freeze import (
    summarize_shadow_observation_freeze,
)
from business_cycle.audits.shadow_role_observation_diagnostics import (
    summarize_retrospective_observation_diagnostics,
)
from business_cycle.shadow_model.evidence_observation_record import (
    summarize_role_observation_record_contract,
)
from business_cycle.shadow_model.forward_capture_contract import (
    summarize_forward_capture_contracts,
)
from business_cycle.shadow_model.observation_evaluators import (
    summarize_book_core_observation_evaluators,
)


DEFAULT_QA11_CLOSURE_PATH = Path(
    "specs/audits/qa11_book_core_evaluator_data_gap_closure.yaml"
)


def summarize_qa11_book_core_evaluator_data_gap_closure(
    path: str | Path = DEFAULT_QA11_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    readiness = summarize_shadow_monitoring_readiness()
    gaps = summarize_book_core_forward_data_gaps()
    capture = summarize_forward_capture_contracts()
    observation = summarize_book_core_observation_evaluators()
    phase_remediation = summarize_book_explicit_phase_evaluator_remediation()
    runtime = summarize_generalized_shadow_history_windows()
    records = summarize_role_observation_record_contract()
    groups = summarize_major_group_observation_coverage()
    diagnostics = summarize_retrospective_observation_diagnostics()
    dry_run = summarize_forward_capture_dry_run()
    prestart = summarize_qa11_prospective_prestart_invariants()
    blockers = summarize_qa11_blocker_remediation()
    freeze = summarize_shadow_observation_freeze()
    leakage = summarize_qa11_observation_runtime_leakage()
    isolation = summarize_qa11_production_isolation()
    summary = {
        "phase": "QA11",
        "monitoring_readiness_semantics_ready": readiness[
            "monitoring_readiness_semantics_ready"
        ],
        "forward_data_gap_registry_ready": gaps["forward_data_gap_registry_ready"],
        "forward_capture_contract_ready": capture["forward_capture_contract_ready"],
        "observation_evaluator_layer_ready": observation[
            "observation_evaluator_layer_ready"
        ],
        "book_explicit_evaluator_remediation_ready": phase_remediation[
            "book_explicit_evaluator_remediation_ready"
        ],
        "generalized_history_window_runtime_ready": runtime[
            "generalized_history_window_runtime_ready"
        ],
        "role_observation_record_contract_ready": records[
            "role_observation_record_contract_ready"
        ],
        "major_group_observation_coverage_ready": groups[
            "major_group_observation_coverage_ready"
        ],
        "retrospective_observation_diagnostics_ready": diagnostics[
            "retrospective_observation_diagnostics_ready"
        ],
        "forward_capture_dry_run_ready": dry_run["forward_capture_dry_run_ready"],
        "prospective_prestart_invariants_preserved": prestart[
            "prospective_prestart_invariants_preserved"
        ],
        "blocker_remediation_registry_ready": blockers[
            "blocker_remediation_registry_ready"
        ],
        "observation_freeze_ready": freeze["observation_freeze_ready"],
        "leakage_guard_ready": leakage["leakage_guard_ready"],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "role_count": gaps["role_count"],
        "forward_capture_ready_role_count": gaps["forward_capture_ready_role_count"],
        "forward_blocked_role_count": gaps["forward_blocked_role_count"],
        "runtime_observable_role_count": gaps["runtime_observable_role_count"],
        "new_runtime_observable_role_count": observation[
            "new_runtime_observable_role_count"
        ],
        "phase_evidence_evaluable_role_count": gaps[
            "phase_evidence_evaluable_role_count"
        ],
        "candidate_selection_eligible_role_count": gaps[
            "candidate_selection_eligible_role_count"
        ],
        "observation_ready_major_group_count": groups[
            "observation_ready_major_group_count"
        ],
        "phase_evidence_evaluable_major_group_count": groups[
            "phase_evidence_evaluable_major_group_count"
        ],
        "candidate_input_complete_major_group_count": groups[
            "candidate_input_complete_major_group_count"
        ],
        "evidence_recording_runtime_ready": readiness[
            "evidence_recording_runtime_ready"
        ],
        "single_role_observation_monitoring_ready": readiness[
            "single_role_observation_monitoring_ready"
        ],
        "multi_role_observation_monitoring_ready": readiness[
            "multi_role_observation_monitoring_ready"
        ],
        "major_group_observation_monitoring_ready": readiness[
            "major_group_observation_monitoring_ready"
        ],
        "phase_evidence_monitoring_ready": readiness[
            "phase_evidence_monitoring_ready"
        ],
        "candidate_capability_ready": False,
        "candidate_monitoring_allowed": False,
        "real_registry_record_count": prestart["real_registry_record_count"],
        "real_registry_write_attempt_count": prestart[
            "real_registry_write_attempt_count"
        ],
        "prospective_protocol_started": prestart["prospective_protocol_started"],
        "prospective_result_inspected": prestart["prospective_result_inspected"],
        "holdout_registered": prestart["holdout_registered"],
        "formal_candidate_phase_computed": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "qa12_allowed": expected["qa12_allowed"],
        "real_backtest_progression_allowed": expected[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": expected["phase_9b1_allowed"],
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa11_closure_status": expected["qa11_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "readiness": readiness,
        "gaps": gaps,
        "capture": capture,
        "observation": observation,
        "phase_remediation": phase_remediation,
        "runtime": runtime,
        "records": records,
        "groups": groups,
        "diagnostics": diagnostics,
        "dry_run": dry_run,
        "prestart": prestart,
        "blockers": blockers,
        "freeze": freeze,
        "leakage": leakage,
        "isolation": isolation,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "recommended_next_phase_title":
            continue
        if summary.get(key) != value:
            return False
    return (
        summary["role_count"] == 40
        and summary["runtime_observable_role_count"] > 1
        and summary["new_runtime_observable_role_count"] > 0
        and summary["gaps"]["role_without_forward_status_count"] == 0
        and summary["capture"]["ready_role_without_capture_contract_count"] == 0
        and summary["observation"][
            "observation_evaluator_with_numeric_threshold_count"
        ]
        == 0
        and summary["runtime"]["runtime_window_contract_missing_count"] == 0
        and summary["records"][
            "observation_record_marked_candidate_eligible_count"
        ]
        == 0
        and summary["groups"]["group_ready_via_modern_substitution_count"] == 0
        and summary["prestart"]["real_registry_record_count"] == 0
        and summary["freeze"]["freeze_hash_valid"] is True
        and summary["leakage"]["scenario_id_reference_count"] == 0
        and summary["isolation"]["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa11_book_core_evaluator_data_gap_closure"
    ]["expected_status"]

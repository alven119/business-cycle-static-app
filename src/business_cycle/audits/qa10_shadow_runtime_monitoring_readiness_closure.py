"""QA10 shadow runtime and pre-start monitoring readiness closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.prospective_shadow_revision_policy import (
    summarize_prospective_shadow_revision_policy,
)
from business_cycle.audits.qa10_automatic_scheduling import (
    summarize_qa10_automatic_scheduling,
)
from business_cycle.audits.qa10_production_isolation import (
    summarize_qa10_production_isolation,
)
from business_cycle.audits.qa_phase_lineage import summarize_qa_phase_lineage
from business_cycle.audits.shadow_candidate_capability import (
    summarize_shadow_candidate_capability,
)
from business_cycle.audits.shadow_runtime_end_to_end import (
    validate_shadow_runtime_end_to_end_fixtures,
)
from business_cycle.shadow_model.evidence_observation_record import (
    summarize_evidence_observation_record_contract,
)
from business_cycle.shadow_model.history_window import summarize_history_window_contract
from business_cycle.shadow_model.prospective_forward_gate import (
    summarize_forward_clock_gate,
)
from business_cycle.shadow_model.prospective_registry_runtime import (
    summarize_registry_idempotency,
)
from business_cycle.shadow_model.runtime_input_snapshot import (
    summarize_runtime_input_snapshot_contract,
)
from business_cycle.shadow_model.runtime_path import (
    summarize_implemented_evaluator_runtime_path,
)


DEFAULT_QA10_CLOSURE_PATH = Path(
    "specs/audits/qa10_shadow_runtime_monitoring_readiness_closure.yaml"
)


def summarize_qa10_shadow_runtime_monitoring_readiness_closure(
    path: str | Path = DEFAULT_QA10_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    lineage = summarize_qa_phase_lineage()
    history = summarize_history_window_contract()
    snapshot = summarize_runtime_input_snapshot_contract()
    runtime = summarize_implemented_evaluator_runtime_path()
    record = summarize_evidence_observation_record_contract()
    registry = summarize_registry_idempotency()
    e2e = validate_shadow_runtime_end_to_end_fixtures()
    gate = summarize_forward_clock_gate()
    revision = summarize_prospective_shadow_revision_policy()
    capability = summarize_shadow_candidate_capability()
    scheduling = summarize_qa10_automatic_scheduling()
    isolation = summarize_qa10_production_isolation()
    summary = {
        "phase": "QA10",
        "qa8_qa9_lineage_verified": lineage["qa8_qa9_lineage_valid"],
        "runtime_history_window_contract_ready": history[
            "runtime_history_window_contract_ready"
        ],
        "runtime_input_snapshot_contract_ready": snapshot[
            "runtime_input_snapshot_contract_ready"
        ],
        "implemented_evaluator_runtime_path_ready": runtime[
            "implemented_evaluator_runtime_path_ready"
        ],
        "typed_evidence_record_builder_ready": record[
            "typed_evidence_record_builder_ready"
        ],
        "append_only_registry_runtime_ready": registry[
            "append_only_registry_runtime_ready"
        ],
        "idempotency_contract_ready": registry["idempotency_contract_ready"],
        "end_to_end_tmp_fixtures_ready": e2e["end_to_end_tmp_fixtures_ready"],
        "prospective_clock_gate_ready": gate["forward_clock_gate_ready"],
        "revision_policy_ready": revision["revision_policy_ready"],
        "candidate_capability_gate_ready": capability[
            "candidate_capability_gate_ready"
        ],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "automatic_scheduling_disabled": scheduling[
            "automatic_scheduling_disabled"
        ],
        "implemented_evaluator_count": runtime["implemented_evaluator_count"],
        "runtime_executable_evaluator_count": runtime[
            "runtime_executable_evaluator_count"
        ],
        "runtime_output_on_2019_revised_count": runtime[
            "runtime_output_on_2019_revised_count"
        ],
        "runtime_output_on_2019_strict_count": runtime[
            "runtime_output_on_2019_strict_count"
        ],
        "legitimate_temporal_abstention_count": runtime[
            "legitimate_temporal_abstention_count"
        ],
        "unexplained_runtime_abstention_count": runtime[
            "unexplained_runtime_abstention_count"
        ],
        "real_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "pre_start_record_written_count": 0,
        "backdated_record_written_count": 0,
        "evaluator_runtime_ready": capability["evaluator_runtime_ready"],
        "evidence_monitoring_ready": capability["evidence_monitoring_ready"],
        "candidate_capability_ready": capability["candidate_capability_ready"],
        "candidate_monitoring_allowed": capability["candidate_monitoring_allowed"],
        "real_data_candidate_selection_enabled": False,
        "formal_candidate_phase_computed": False,
        "prospective_protocol_registered": True,
        "prospective_protocol_started": False,
        "prospective_result_inspected": False,
        "holdout_registered": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "qa11_allowed": expected["qa11_allowed"],
        "real_backtest_progression_allowed": expected[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": expected["phase_9b1_allowed"],
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa10_closure_status": expected["qa10_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "lineage": lineage,
        "history": history,
        "snapshot": snapshot,
        "runtime": runtime,
        "record": record,
        "registry": registry,
        "e2e": e2e,
        "gate": gate,
        "revision": revision,
        "capability": capability,
        "scheduling": scheduling,
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
        summary["lineage"]["phase_sequence_gap_count"] == 0
        and summary["lineage"]["freeze_parent_mismatch_count"] == 0
        and summary["history"]["future_data_window_count"] == 0
        and summary["history"]["mixed_data_mode_window_count"] == 0
        and summary["snapshot"]["snapshot_with_future_data_count"] == 0
        and summary["record"]["prohibited_decision_field_count"] == 0
        and summary["registry"]["duplicate_append_record_written_count"] == 0
        and summary["registry"]["hash_chain_validation_failure_count"] == 0
        and summary["e2e"]["end_to_end_fixture_pass_count"]
        == summary["e2e"]["end_to_end_fixture_count"]
        and summary["e2e"]["duplicate_record_written_count"] == 0
        and summary["e2e"]["invalid_fixture_accepted_count"] == 0
        and summary["revision"]["revised_mode_real_registry_record_count"] == 0
        and summary["capability"]["capability_promoted_by_single_evaluator_count"]
        == 0
        and summary["scheduling"]["automatic_scheduler_added_count"] == 0
        and summary["isolation"]["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa10_shadow_runtime_monitoring_readiness_closure"
    ]["expected_status"]

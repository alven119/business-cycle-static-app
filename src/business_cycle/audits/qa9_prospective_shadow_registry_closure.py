"""QA9 prospective shadow registry closure contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.prospective_monitoring_freeze import (
    summarize_prospective_monitoring_freeze,
)
from business_cycle.audits.prospective_observation_inspection import (
    summarize_prospective_observation_inspection_policy,
)
from business_cycle.audits.prospective_protocol_start_semantics import (
    summarize_protocol_start_semantics,
)
from business_cycle.audits.prospective_protocol_versioning import (
    summarize_prospective_protocol_versioning,
)
from business_cycle.audits.prospective_registry_fixtures import (
    validate_prospective_shadow_registry_fixtures,
)
from business_cycle.audits.prospective_registry_production_isolation import (
    summarize_prospective_registry_production_isolation,
)
from business_cycle.audits.shadow_evaluator_runtime import (
    summarize_shadow_evaluator_runtime,
    validate_shadow_evaluator_runtime_fixtures,
)
from business_cycle.shadow_model.input_snapshot_manifest import (
    summarize_input_snapshot_contract,
)
from business_cycle.shadow_model.prospective_forward_gate import (
    summarize_forward_clock_gate,
)
from business_cycle.shadow_model.prospective_registry import (
    summarize_registry_contract,
)
from business_cycle.shadow_model.prospective_registry_store import (
    summarize_append_only_store,
)


DEFAULT_QA9_CLOSURE_PATH = Path(
    "specs/audits/qa9_prospective_shadow_registry_closure.yaml"
)


def summarize_qa9_prospective_shadow_registry_closure(
    path: str | Path = DEFAULT_QA9_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    runtime = summarize_shadow_evaluator_runtime()
    runtime_fixtures = validate_shadow_evaluator_runtime_fixtures()
    registry = summarize_registry_contract()
    store = summarize_append_only_store()
    snapshot = summarize_input_snapshot_contract()
    gate = summarize_forward_clock_gate()
    start = summarize_protocol_start_semantics()
    versioning = summarize_prospective_protocol_versioning()
    inspection = summarize_prospective_observation_inspection_policy()
    registry_fixtures = validate_prospective_shadow_registry_fixtures()
    freeze = summarize_prospective_monitoring_freeze()
    isolation = summarize_prospective_registry_production_isolation()
    summary = {
        "phase": "QA9",
        "evaluator_runtime_audit_ready": runtime["evaluator_runtime_audit_ready"],
        "implemented_evaluator_runtime_wired": runtime[
            "implemented_evaluator_runtime_wired"
        ],
        "evaluator_runtime_fixture_suite_ready": runtime_fixtures[
            "evaluator_runtime_fixture_suite_ready"
        ],
        "registry_contract_ready": registry["registry_contract_ready"],
        "append_only_store_ready": store["append_only_store_ready"],
        "input_snapshot_contract_ready": snapshot["input_snapshot_contract_ready"],
        "forward_clock_gate_ready": gate["forward_clock_gate_ready"],
        "protocol_start_semantics_ready": start["protocol_start_semantics_ready"],
        "protocol_versioning_ready": versioning["protocol_versioning_ready"],
        "inspection_governance_ready": inspection["inspection_governance_ready"],
        "registry_fixture_validation_ready": registry_fixtures[
            "registry_fixture_validation_ready"
        ],
        "monitoring_infrastructure_freeze_ready": freeze[
            "monitoring_infrastructure_freeze_ready"
        ],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "contract_evaluable_evaluator_count": runtime[
            "contract_evaluable_evaluator_count"
        ],
        "runtime_executable_evaluator_count": runtime[
            "runtime_executable_evaluator_count"
        ],
        "runtime_output_available_evaluator_count": runtime[
            "runtime_output_available_evaluator_count"
        ],
        "directional_evidence_evaluable_count": runtime[
            "directional_evidence_evaluable_count"
        ],
        "candidate_selection_eligible_evaluator_count": runtime[
            "candidate_selection_eligible_evaluator_count"
        ],
        "protocol_registered": start["protocol_registered"],
        "registry_armed": start["registry_armed"],
        "protocol_started": start["protocol_started"],
        "first_record_written": start["first_record_written"],
        "real_record_count": start["real_record_count"],
        "prospective_result_inspected": start["prospective_result_inspected"],
        "candidate_capability_ready": gate["candidate_capability_ready"],
        "candidate_monitoring_allowed": gate["candidate_monitoring_allowed"],
        "holdout_registered": start["holdout_registered"],
        "retrospective_backfill_allowed": False,
        "retrospective_candidate_selection_allowed": False,
        "real_data_candidate_selection_enabled": False,
        "formal_candidate_phase_computed": False,
        "formal_decision_model_ready": False,
        "economic_validation_status": "not_started",
        "independent_validation_ready": False,
        "qa10_allowed": expected["qa10_allowed"],
        "real_backtest_progression_allowed": expected[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": expected["phase_9b1_allowed"],
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa9_closure_status": expected["qa9_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "runtime": runtime,
        "runtime_fixtures": runtime_fixtures,
        "registry": registry,
        "store": store,
        "snapshot": snapshot,
        "gate": gate,
        "start_semantics": start,
        "versioning": versioning,
        "inspection": inspection,
        "registry_fixtures": registry_fixtures,
        "freeze": freeze,
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
        summary["runtime"]["implemented_evaluator_count"] == 1
        and summary["runtime"]["runtime_registered_evaluator_count"] == 1
        and summary["runtime"][
            "evaluator_marked_evaluable_but_runner_unwired_count"
        ]
        == 0
        and summary["runtime"]["unexplained_runtime_abstention_count"] == 0
        and summary["runtime"]["smoothing_output_mislabeled_directional_count"] == 0
        and summary["runtime"]["smoothing_output_mislabeled_confirmation_count"] == 0
        and summary["runtime_fixtures"]["synthetic_runtime_fixture_pass_count"]
        == summary["runtime_fixtures"]["synthetic_runtime_fixture_count"]
        and summary["registry_fixtures"]["valid_pass_count"]
        == summary["registry_fixtures"]["valid_fixture_count"]
        and summary["registry_fixtures"]["invalid_rejected_count"]
        == summary["registry_fixtures"]["invalid_fixture_count"]
        and summary["registry_fixtures"]["expected_error_mismatch_count"] == 0
        and summary["snapshot"]["snapshot_hash_mismatch_count"] == 0
        and summary["gate"]["arbitrary_real_as_of_override_count"] == 0
        and summary["versioning"]["silent_freeze_update_count"] == 0
        and summary["versioning"]["start_date_moved_earlier_count"] == 0
        and summary["versioning"]["required_successor_missing_count"] == 0
        and summary["versioning"]["protocol_version_lineage_valid"] is True
        and summary["inspection"]["real_result_inspection_count"] == 0
        and summary["freeze"]["monitoring_freeze_hash_valid"] is True
        and summary["isolation"]["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa9_prospective_shadow_registry_closure"
    ]["expected_status"]

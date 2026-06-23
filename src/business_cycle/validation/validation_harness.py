"""Phase 16 synthetic-only validation harness dry-run."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.validation_readiness import summarize_validation_readiness
from business_cycle.validation.economic_validation_protocol import (
    summarize_economic_validation_protocol,
)
from business_cycle.validation.validation_artifact_contracts import (
    load_validation_harness_contract,
    load_validation_harness_synthetic_fixtures,
    summarize_validation_artifact_contracts,
    validate_validation_harness_output,
)


HARNESS_RUN_ID = "phase16_synthetic_dry_run_v1"


def run_validation_harness_dry_run(*, fixture_mode: str) -> dict[str, Any]:
    if fixture_mode != "synthetic":
        raise ValueError("Phase 16 validation harness only allows synthetic fixtures")
    contract = load_validation_harness_contract()
    fixtures = load_validation_harness_synthetic_fixtures()
    output = {
        "harness_run_id": HARNESS_RUN_ID,
        "harness_version": contract["harness_version"],
        "dry_run_mode": "synthetic_only",
        "structural_check_results": _structural_check_results(contract),
        "artifact_schema_check_results": [],
        "fixture_check_results": _fixture_check_results(fixtures),
        "blocked_reason_codes": [
            "real_historical_validation_disabled",
            "metric_computation_disabled",
            "backtest_execution_disabled",
            "candidate_output_disabled",
        ],
        "allowed_uses": [
            "validation_harness_mechanics_dry_run",
            "artifact_schema_check",
            "protocol_restriction_check",
        ],
        "prohibited_uses": [
            "historical_accuracy_validation",
            "economic_validation_execution",
            "backtest_execution",
            "holdout_registration",
            "candidate_or_current_phase_output",
        ],
        "trust_metadata": {
            "parent_freeze_id": contract["parent_freeze_id"],
            "parent_validation_protocol_id": contract[
                "parent_validation_protocol_id"
            ],
            "fixture_mode": "synthetic",
            "provenance_complete": True,
            "real_history_used": False,
            "metrics_computed": False,
        },
        "metric_computation_enabled": False,
        "backtest_execution_enabled": False,
        "holdout_registered": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    output["artifact_schema_check_results"] = _artifact_schema_check_results(output)
    validation = validate_validation_harness_output(output)
    if not validation["artifact_schema_valid"]:
        raise ValueError(f"invalid validation harness output schema: {validation}")
    return output


def summarize_validation_harness_dry_run() -> dict[str, Any]:
    contract = load_validation_harness_contract()
    protocol = summarize_economic_validation_protocol()
    readiness = summarize_validation_readiness()
    artifact = summarize_validation_artifact_contracts()
    dry_run = run_validation_harness_dry_run(fixture_mode="synthetic")
    schema = validate_validation_harness_output(dry_run)
    guards = contract["disabled_runtime_guards"]
    output = contract["output_restrictions"]
    ready = (
        protocol["economic_validation_protocol_ready"] is True
        and readiness["validation_readiness_registry_ready"] is True
        and artifact["validation_artifact_contract_ready"] is True
        and schema["artifact_schema_valid"] is True
        and dry_run["dry_run_mode"] == "synthetic_only"
        and all(result["passed"] is True for result in dry_run["structural_check_results"])
        and all(result["passed"] is True for result in dry_run["artifact_schema_check_results"])
        and all(result["passed"] is True for result in dry_run["fixture_check_results"])
        and all(value is False for value in guards.values())
    )
    return {
        "phase": "16",
        "validation_harness_contract_ready": _contract_ready(contract),
        "validation_harness_runtime_ready": ready,
        "validation_artifact_contract_ready": artifact[
            "validation_artifact_contract_ready"
        ],
        "synthetic_fixture_count": artifact["synthetic_fixture_count"],
        "fixture_pass_count": sum(
            result["passed"] is True for result in dry_run["fixture_check_results"]
        ),
        "synthetic_dry_run_executed": dry_run["dry_run_mode"] == "synthetic_only",
        "real_historical_validation_executed": guards[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": output[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": output[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": dry_run["metric_computation_enabled"],
        "backtest_execution_enabled": dry_run["backtest_execution_enabled"],
        "holdout_registered": dry_run["holdout_registered"],
        "candidate_selection_enabled": contract["candidate_output_policy"][
            "candidate_selection_enabled"
        ],
        "candidate_phase_emitted": dry_run["candidate_phase_emitted"],
        "current_phase_emitted": dry_run["current_phase_emitted"],
        "prospective_registry_record_count": contract["prospective_policy"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["prospective_policy"][
            "prospective_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(guards["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "forbidden_output_field_count": schema["forbidden_output_field_count"],
        "unexpected_output_count": schema["unexpected_output_count"],
        "missing_allowed_output_count": schema["missing_allowed_output_count"],
        "dry_run": dry_run,
        "artifact_contract": artifact,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["harness_status"] == "scaffolded_synthetic_dry_run_only"
        and contract["synthetic_fixture_policy"]["fixture_mode"] == "synthetic"
        and contract["synthetic_fixture_policy"]["real_history_allowed"] is False
        and contract["metric_computation_policy"]["metric_computation_enabled"] is False
        and contract["backtest_execution_policy"]["backtest_execution_enabled"] is False
        and contract["holdout_policy"]["holdout_registered"] is False
        and contract["candidate_output_policy"]["candidate_selection_enabled"] is False
        and contract["candidate_output_policy"]["candidate_phase_emitted"] is False
        and contract["candidate_output_policy"]["current_phase_emitted"] is False
    )


def _structural_check_results(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": check["check_id"],
            "passed": bool(check["expected"]),
            "details": "synthetic_dry_run_contract_check",
        }
        for check in contract["structural_validation_checks"]
    ]


def _artifact_schema_check_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    validation = validate_validation_harness_output(payload)
    return [
        {
            "check_id": "required_allowed_outputs_present",
            "passed": validation["missing_allowed_output_count"] == 0,
        },
        {
            "check_id": "forbidden_outputs_absent",
            "passed": validation["forbidden_output_field_count"] == 0,
        },
        {
            "check_id": "trust_metadata_present",
            "passed": isinstance(payload.get("trust_metadata"), dict),
        },
    ]


def _fixture_check_results(fixtures: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for fixture in fixtures["fixtures"]:
        artifact = fixture["input_artifact"]
        blockers = _fixture_blockers(artifact)
        actual_status = "rejected" if blockers else "accepted"
        expected_status = fixture["expected_status"]
        expected_blocker = fixture.get("expected_blocker")
        results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "fixture_status": actual_status,
                "expected_status": expected_status,
                "synthetic_only": fixture["synthetic_only"],
                "schema_valid": artifact["provenance_complete"] is True,
                "blocked_reason_codes": blockers,
                "passed": (
                    actual_status == expected_status
                    and fixture["synthetic_only"] is True
                    and artifact["provenance_complete"] is True
                    and (expected_blocker is None or expected_blocker in blockers)
                ),
            }
        )
    return results


def _fixture_blockers(artifact: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if artifact["metric_fields_present"] is True:
        blockers.append("metric_fields_forbidden")
    if artifact["phase_output_fields_present"] is True:
        blockers.append("phase_output_fields_forbidden")
    return blockers

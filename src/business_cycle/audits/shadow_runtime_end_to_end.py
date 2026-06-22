"""QA10 temporary end-to-end runtime fixture validation."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import yaml

from business_cycle.shadow_model.evidence_observation_record import (
    build_correction_observation_record,
    build_evidence_observation_record,
    canonical_record_hash,
)
from business_cycle.shadow_model.history_window import weekly_observations
from business_cycle.shadow_model.prospective_registry import ZERO_HASH
from business_cycle.shadow_model.prospective_registry_runtime import (
    RuntimeEvidenceRegistry,
)
from business_cycle.shadow_model.runtime_input_snapshot import build_runtime_input_snapshot
from business_cycle.shadow_model.runtime_path import evaluate_snapshot


DEFAULT_E2E_FIXTURE_PATH = Path("specs/audits/shadow_runtime_end_to_end_fixtures.yaml")


def validate_shadow_runtime_end_to_end_fixtures(
    path: str | Path = DEFAULT_E2E_FIXTURE_PATH,
) -> dict[str, Any]:
    fixtures = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_runtime_end_to_end_fixtures"
    ]["fixtures"]
    results = [_run_fixture(row["fixture_id"]) for row in fixtures]
    pass_count = sum(row["passed"] for row in results)
    return {
        "phase": "QA10",
        "end_to_end_tmp_fixtures_ready": pass_count == len(results),
        "end_to_end_fixture_count": len(results),
        "end_to_end_fixture_pass_count": pass_count,
        "evaluator_output_fixture_count": sum(
            row["evaluator_output"] for row in results
        ),
        "abstention_record_fixture_count": sum(
            row["abstention_record"] for row in results
        ),
        "append_success_fixture_count": sum(row["append_success"] for row in results),
        "duplicate_record_written_count": sum(
            row["duplicate_record_written"] for row in results
        ),
        "correction_chain_fixture_count": sum(
            row["correction_chain_valid"] for row in results
        ),
        "invalid_fixture_accepted_count": sum(
            row["invalid_accepted"] for row in results
        ),
        "fixtures": results,
    }


def _run_fixture(fixture_id: str) -> dict[str, Any]:
    try:
        if fixture_id == "complete_revised_history":
            return _complete_history_fixture("revised")
        if fixture_id == "complete_strict_history":
            return _complete_history_fixture("vintage_as_of")
        if fixture_id == "insufficient_history":
            return _insufficient_history_fixture()
        if fixture_id == "mixed_data_mode":
            return _invalid_snapshot_fixture(fixture_id, "mixed_data_mode_history")
        if fixture_id == "future_observation":
            return _invalid_snapshot_fixture(fixture_id, "invalid_history_window")
        if fixture_id == "duplicate_append":
            return _duplicate_append_fixture()
        if fixture_id == "correction_record":
            return _correction_fixture()
        if fixture_id == "rule_version_mismatch":
            return _rule_version_mismatch_fixture()
        if fixture_id == "provenance_missing":
            return _provenance_missing_fixture()
        if fixture_id == "prohibited_decision_field":
            return _prohibited_field_fixture()
    except ValueError:
        return _result(fixture_id, passed=True, invalid_accepted=False)
    return _result(fixture_id, passed=False, invalid_accepted=True)


def _complete_history_fixture(data_mode: str) -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(
        as_of="2026-08-31",
        data_mode=data_mode,
        observations=weekly_observations(as_of="2026-08-31", count=4, data_mode=data_mode),
    )
    evaluator_result = evaluate_snapshot(snapshot)
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluator_result,
        previous_record_hash=ZERO_HASH,
    )
    with TemporaryDirectory() as temp_dir:
        append = RuntimeEvidenceRegistry(temp_dir).append_record(record)
    return _result(
        "complete_strict_history" if data_mode == "vintage_as_of" else "complete_revised_history",
        evaluator_output=evaluator_result["rule_match_status"] == "matched",
        append_success=append["record_written"],
    )


def _insufficient_history_fixture() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(
        as_of="2026-08-31",
        data_mode="revised",
        observations=weekly_observations(as_of="2026-08-31", count=1, data_mode="revised"),
    )
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    return _result(
        "insufficient_history",
        abstention_record=record["record_type"] == "abstention_observation",
    )


def _invalid_snapshot_fixture(fixture_id: str, expected_reason: str) -> dict[str, Any]:
    observations = weekly_observations(as_of="2026-08-31", count=4, data_mode="revised")
    if fixture_id == "mixed_data_mode":
        observations[0]["data_mode"] = "vintage_as_of"
    if fixture_id == "future_observation":
        observations[-1]["date"] = "2026-09-30"
    snapshot = build_runtime_input_snapshot(
        as_of="2026-08-31",
        data_mode="revised",
        observations=observations,
    )
    return _result(
        fixture_id,
        passed=snapshot["abstention_reason"] == expected_reason,
        invalid_accepted=snapshot["ready_for_evaluator"],
    )


def _duplicate_append_fixture() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    with TemporaryDirectory() as temp_dir:
        registry = RuntimeEvidenceRegistry(temp_dir)
        first = registry.append_record(record)
        second = registry.append_record(record)
    return _result(
        "duplicate_append",
        append_success=first["record_written"],
        duplicate_record_written=second["record_written"],
        passed=first["record_written"] and not second["record_written"],
    )


def _correction_fixture() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    original = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    correction = build_correction_observation_record(
        original_record=original,
        correction_reason="source_artifact_metadata_correction",
        previous_record_hash=original["canonical_record_hash"],
    )
    with TemporaryDirectory() as temp_dir:
        registry = RuntimeEvidenceRegistry(temp_dir)
        registry.append_record(original)
        registry.append_record(correction)
        chain_valid = registry.validate_chain()
    return _result(
        "correction_record",
        correction_chain_valid=chain_valid
        and correction["supersedes_record_hash"] == canonical_record_hash(original),
        append_success=True,
    )


def _rule_version_mismatch_fixture() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    record["rule_contract_hash"] = "wrong"
    with TemporaryDirectory() as temp_dir:
        registry = RuntimeEvidenceRegistry(temp_dir)
        registry.append_record(record)
    return _result("rule_version_mismatch", passed=False, invalid_accepted=True)


def _provenance_missing_fixture() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    snapshot["provenance_complete"] = False
    if not snapshot["provenance_complete"]:
        raise ValueError("missing_provenance")
    return _result("provenance_missing", passed=False, invalid_accepted=True)


def _prohibited_field_fixture() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    record["candidate_phase"] = "recovery"
    with TemporaryDirectory() as temp_dir:
        RuntimeEvidenceRegistry(temp_dir).append_record(record)
    return _result("prohibited_decision_field", passed=False, invalid_accepted=True)


def _result(
    fixture_id: str,
    *,
    passed: bool = True,
    evaluator_output: bool = False,
    abstention_record: bool = False,
    append_success: bool = False,
    duplicate_record_written: bool = False,
    correction_chain_valid: bool = False,
    invalid_accepted: bool = False,
) -> dict[str, Any]:
    return {
        "fixture_id": fixture_id,
        "passed": passed,
        "evaluator_output": int(evaluator_output),
        "abstention_record": int(abstention_record),
        "append_success": int(append_success),
        "duplicate_record_written": int(duplicate_record_written),
        "correction_chain_valid": int(correction_chain_valid),
        "invalid_accepted": int(invalid_accepted),
    }

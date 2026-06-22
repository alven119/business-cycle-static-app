from __future__ import annotations

from business_cycle.shadow_model.evidence_observation_record import (
    PROHIBITED_FIELDS,
    build_correction_observation_record,
    build_evidence_observation_record,
    validate_evidence_observation_record,
)
from business_cycle.shadow_model.prospective_registry import ZERO_HASH
from business_cycle.shadow_model.runtime_input_snapshot import build_runtime_input_snapshot
from business_cycle.shadow_model.runtime_path import evaluate_snapshot


def test_evidence_record_contains_no_decision_fields() -> None:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    validation = validate_evidence_observation_record(record)

    assert PROHIBITED_FIELDS.isdisjoint(record)
    assert validation["record_without_snapshot_hash_count"] == 0
    assert validation["record_without_rule_hash_count"] == 0
    assert validation["prohibited_decision_field_count"] == 0


def test_abstention_record_requires_reason_and_correction_has_lineage() -> None:
    snapshot = build_runtime_input_snapshot(
        as_of="2026-08-31",
        data_mode="vintage_as_of",
    )
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )
    correction = build_correction_observation_record(
        original_record=record,
        correction_reason="metadata_correction",
        previous_record_hash=record["canonical_record_hash"],
    )

    assert record["record_type"] == "abstention_observation"
    assert validate_evidence_observation_record(record)["abstention_without_reason_count"] == 0
    assert correction["supersedes_record_hash"] == record["canonical_record_hash"]
    assert validate_evidence_observation_record(correction)[
        "correction_without_superseded_hash_count"
    ] == 0

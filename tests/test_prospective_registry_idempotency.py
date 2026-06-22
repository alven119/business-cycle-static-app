from __future__ import annotations

import pytest

from business_cycle.shadow_model.evidence_observation_record import (
    build_evidence_observation_record,
)
from business_cycle.shadow_model.prospective_registry import ZERO_HASH
from business_cycle.shadow_model.prospective_registry_runtime import (
    RuntimeEvidenceRegistry,
    summarize_registry_idempotency,
)
from business_cycle.shadow_model.runtime_input_snapshot import build_runtime_input_snapshot
from business_cycle.shadow_model.runtime_path import evaluate_snapshot


def _record(previous: str = ZERO_HASH) -> dict:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    return build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=previous,
    )


def test_duplicate_append_does_not_write_second_record(tmp_path) -> None:
    registry = RuntimeEvidenceRegistry(tmp_path)
    record = _record()

    first = registry.append_record(record)
    second = registry.append_record(record)

    assert first["record_written"] is True
    assert second["append_status"] == "duplicate_rejected"
    assert second["record_written"] is False
    assert len(registry.load_records()) == 1


def test_hash_chain_rejects_out_of_order_append(tmp_path) -> None:
    registry = RuntimeEvidenceRegistry(tmp_path)
    first = _record()
    registry.append_record(first)
    snapshot = build_runtime_input_snapshot(as_of="2026-09-30", data_mode="revised")
    second = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
        previous_record_hash=ZERO_HASH,
    )

    with pytest.raises(ValueError, match="out_of_order_append"):
        registry.append_record(second)


def test_registry_idempotency_summary_hard_gates() -> None:
    summary = summarize_registry_idempotency()

    assert summary["duplicate_append_record_written_count"] == 0
    assert summary["hash_chain_validation_failure_count"] == 0
    assert summary["out_of_order_append_count"] == 0
    assert summary["overwrite_api_count"] == 0
    assert summary["delete_api_count"] == 0
    assert summary["compact_api_count"] == 0

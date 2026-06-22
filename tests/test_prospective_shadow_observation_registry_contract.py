from __future__ import annotations

from business_cycle.shadow_model.prospective_registry import (
    build_prospective_record,
    semantic_record_hash,
    summarize_registry_contract,
)


def test_prospective_registry_contract_is_append_only() -> None:
    summary = summarize_registry_contract()

    assert summary["registry_contract_ready"] is True
    assert summary["registry_status"] == "armed_not_started"
    assert summary["append_only"] is True
    assert summary["overwrite_allowed"] is False
    assert summary["delete_api_allowed"] is False
    assert summary["rewrite_api_allowed"] is False


def test_prospective_record_hash_is_canonical() -> None:
    record = build_prospective_record(
        sequence_number=1,
        previous_record_hash="0" * 64,
        observation_period="2026-07",
        as_of="2026-08-31",
        input_snapshot_manifest_hash="abc",
    )

    assert record["record_hash"] == semantic_record_hash(record)

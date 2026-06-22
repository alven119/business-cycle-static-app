from __future__ import annotations

from business_cycle.shadow_model.runtime_input_snapshot import (
    build_runtime_input_snapshot,
    summarize_runtime_input_snapshot_contract,
    validate_runtime_input_snapshot,
)


def test_runtime_input_snapshot_hash_is_deterministic() -> None:
    first = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    second = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")

    assert first["snapshot_payload_hash"] == second["snapshot_payload_hash"]
    assert validate_runtime_input_snapshot(first)["snapshot_hash_mismatch_count"] == 0


def test_runtime_input_snapshot_contract_hard_gates() -> None:
    summary = summarize_runtime_input_snapshot_contract()

    assert summary["runtime_input_snapshot_contract_ready"] is True
    assert summary["snapshot_without_payload_hash_count"] == 0
    assert summary["snapshot_without_contract_hash_count"] == 0
    assert summary["snapshot_with_future_data_count"] == 0
    assert summary["snapshot_with_mixed_data_mode_count"] == 0
    assert summary["snapshot_with_proxy_count"] == 0
    assert summary["strict_snapshot_with_revised_fallback_count"] == 0

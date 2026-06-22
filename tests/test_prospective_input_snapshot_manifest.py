from __future__ import annotations

from business_cycle.shadow_model.input_snapshot_manifest import (
    build_input_snapshot_manifest,
    summarize_input_snapshot_contract,
    validate_input_snapshot_manifest,
)


def test_prospective_input_snapshot_contract_passes() -> None:
    summary = summarize_input_snapshot_contract()

    assert summary["input_snapshot_contract_ready"] is True
    assert summary["future_availability_in_snapshot_count"] == 0
    assert summary["mixed_data_mode_snapshot_count"] == 0
    assert summary["strict_snapshot_with_proxy_count"] == 0
    assert summary["strict_snapshot_with_revised_fallback_count"] == 0
    assert summary["snapshot_hash_mismatch_count"] == 0


def test_strict_snapshot_rejects_proxy() -> None:
    manifest = build_input_snapshot_manifest(
        as_of="2026-08-31",
        data_mode="vintage_as_of",
        series_ids=["ICSA"],
        availability_dates={"ICSA": "2026-08-31"},
        selected_observation_dates={"ICSA": ["2026-08-05"]},
        proxy_series=["ICSA_PROXY"],
    )
    summary = validate_input_snapshot_manifest(manifest)

    assert summary["strict_snapshot_with_proxy_count"] == 1

from __future__ import annotations

from business_cycle.shadow_model.source_preflight import run_source_preflight


def test_source_preflight_is_no_write_and_no_network() -> None:
    summary = run_source_preflight(no_write=True, reuse_existing=True, no_network=True)

    assert summary["no_write_source_preflight_ready"] is True
    assert summary["adapter_preflight_pass_count"] == summary[
        "adapter_preflight_requested_count"
    ]
    assert summary["role_live_preflight_ready_count"] == 24
    assert summary["major_group_live_preflight_ready_count"] == 15
    assert summary["source_identity_mismatch_count"] == 0
    assert summary["schema_mismatch_count"] == 0
    assert summary["release_semantics_mismatch_count"] == 0
    assert summary["registry_write_attempt_count"] == 0
    assert all(not row["network_attempted"] for row in summary["adapters"])
    assert all(not row["registry_write_attempted"] for row in summary["adapters"])


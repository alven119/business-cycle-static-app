from __future__ import annotations

from business_cycle.audits.forward_capture_topology import (
    summarize_forward_capture_topology,
)


def test_forward_capture_topology_has_no_leaf_derived_double_count() -> None:
    summary = summarize_forward_capture_topology()

    assert summary["capture_topology_valid"] is True
    assert summary["forward_ready_role_count"] == 35
    assert summary["direct_leaf_capture_role_count"] == 34
    assert summary["derived_capture_role_count"] == 1
    assert summary["hybrid_capture_role_count"] == 0
    assert summary["unique_source_request_count"] == 28
    assert summary["duplicate_source_request_count"] == 0
    assert summary["duplicate_release_artifact_plan_count"] == 0
    assert summary["derived_role_with_unjustified_direct_artifact_plan_count"] == 0
    assert summary["capture_role_without_terminal_source_count"] == 0
    assert summary["capture_cycle_count"] == 0
    assert summary["capture_path_ambiguity_count"] == 0

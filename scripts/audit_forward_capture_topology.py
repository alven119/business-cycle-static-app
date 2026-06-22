from __future__ import annotations

from business_cycle.audits.forward_capture_topology import (
    summarize_forward_capture_topology,
)


def main() -> None:
    summary = summarize_forward_capture_topology()
    for key in (
        "phase",
        "capture_topology_valid",
        "forward_ready_role_count",
        "direct_leaf_capture_role_count",
        "derived_capture_role_count",
        "hybrid_capture_role_count",
        "unique_source_request_count",
        "unique_release_artifact_plan_count",
        "derived_capture_plan_count",
        "duplicate_source_request_count",
        "duplicate_release_artifact_plan_count",
        "derived_role_with_unjustified_direct_artifact_plan_count",
        "capture_role_without_terminal_source_count",
        "capture_cycle_count",
        "capture_path_ambiguity_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


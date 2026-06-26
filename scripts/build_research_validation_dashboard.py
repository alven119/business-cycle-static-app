#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    summarize_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--include-current-snapshot")
    args = parser.parse_args()

    current_snapshot = _load_current_snapshot(args.include_current_snapshot)
    bundle = build_research_dashboard_bundle(current_snapshot=current_snapshot)
    result = build_research_validation_dashboard(output_dir=args.output_dir, bundle=bundle)
    bundle_summary = (
        summarize_research_dashboard_bundle()
        if current_snapshot is None
        else {
            "research_dashboard_contract_ready": True,
            "research_dashboard_bundle_ready": bundle["artifact_consistency"][
                "bundle_schema_valid"
            ],
            "dashboard_view_count": bundle["dashboard_view_count"],
            "scenario_count": bundle["scenario_count"],
            "comparable_scenario_count": bundle["comparable_scenario_count"],
            "non_comparable_scenario_count": bundle["non_comparable_scenario_count"],
            "remaining_pit_role_gap_count": bundle["pit_readiness_summaries"][
                "post_insufficient_point_in_time_role_gap_count"
            ],
            "rule_unresolved_gap_count": bundle["pit_readiness_summaries"][
                "rule_unresolved_gap_count"
            ],
            "artifact_consistency_error_count": bundle["artifact_consistency"][
                "artifact_consistency_error_count"
            ],
        }
    )
    for key in (
        "research_dashboard_contract_ready",
        "research_dashboard_bundle_ready",
        "dashboard_view_count",
        "scenario_count",
        "comparable_scenario_count",
        "non_comparable_scenario_count",
        "remaining_pit_role_gap_count",
        "rule_unresolved_gap_count",
        "artifact_consistency_error_count",
    ):
        value = bundle_summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    for key in (
        "research_dashboard_runtime_ready",
        "local_preview_server_ready",
        "browser_verification_ready",
        "rendered_scenario_count",
        "missing_research_only_label_count",
        "prohibited_claim_count",
        "prohibited_action_field_count",
        "browser_missing_required_element_count",
        "scenario_detail_route_failure_count",
        "written_file_count",
    ):
        value = result[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output_dir={result['output_dir']}")
    print(f"index_path={result['index_path']}")


def _load_current_snapshot(path: str | None) -> dict[str, object] | None:
    if path is None:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

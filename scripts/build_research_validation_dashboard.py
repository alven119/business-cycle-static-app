#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.boom_transition_dashboard_surface import (
    build_boom_transition_dashboard_surface,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--include-current-snapshot")
    parser.add_argument(
        "--include-boom-transition-monitor",
        action="store_true",
        help="include the Phase49 declared boom transition dashboard surface",
    )
    parser.add_argument(
        "--include-latest-evidence-drilldown",
        action="store_true",
        help="include the Phase63 latest evidence / indicator drilldown page",
    )
    parser.add_argument(
        "--include-phase-start-confirmation",
        action="store_true",
        help="include the Phase69 declared boom start confirmation panel",
    )
    args = parser.parse_args()

    current_snapshot = _load_current_snapshot(args.include_current_snapshot)
    boom_transition_surface = (
        build_boom_transition_dashboard_surface()
        if args.include_boom_transition_monitor
        else None
    )
    latest_evidence_drilldown = (
        build_indicator_dashboard_explanation_drilldown_view_model()
        if args.include_latest_evidence_drilldown
        or args.include_phase_start_confirmation
        else None
    )
    phase_start_confirmation = (
        build_declared_phase_start_confirmation_view_model()
        if args.include_phase_start_confirmation
        else None
    )
    bundle = build_research_dashboard_bundle(
        current_snapshot=current_snapshot,
        boom_transition_surface=boom_transition_surface,
        indicator_dashboard_explanation_drilldown=latest_evidence_drilldown,
        declared_phase_start_confirmation=phase_start_confirmation,
    )
    result = build_research_validation_dashboard(output_dir=args.output_dir, bundle=bundle)
    bundle_summary = _bundle_summary(bundle)
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
    print(
        "boom_transition_dashboard_view_ready="
        f"{str(bool(bundle.get('boom_transition_dashboard'))).lower()}"
    )
    print(
        "latest_evidence_dashboard_view_ready="
        f"{str(bool(bundle.get('indicator_dashboard_explanation_drilldown'))).lower()}"
    )
    print(
        "phase_start_confirmation_view_ready="
        f"{str(bool(bundle.get('declared_phase_start_confirmation'))).lower()}"
    )
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


def _bundle_summary(bundle: dict[str, object]) -> dict[str, object]:
    pit = bundle["pit_readiness_summaries"]
    consistency = bundle["artifact_consistency"]
    return {
        "research_dashboard_contract_ready": True,
        "research_dashboard_bundle_ready": consistency["bundle_schema_valid"],
        "dashboard_view_count": bundle["dashboard_view_count"],
        "scenario_count": bundle["scenario_count"],
        "comparable_scenario_count": bundle["comparable_scenario_count"],
        "non_comparable_scenario_count": bundle["non_comparable_scenario_count"],
        "remaining_pit_role_gap_count": pit[
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "rule_unresolved_gap_count": pit["rule_unresolved_gap_count"],
        "artifact_consistency_error_count": consistency[
            "artifact_consistency_error_count"
        ],
    }


if __name__ == "__main__":
    main()

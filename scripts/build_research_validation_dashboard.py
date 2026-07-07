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
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation_view_model,
)
from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux_view_model,
)
from business_cycle.render.transition_risk_evidence_accumulation import (
    build_transition_risk_evidence_accumulation_view_model,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    build_local_current_cache_dashboard_bridge_view_model,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
)
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate_view_model,
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
    parser.add_argument(
        "--include-phase-start-update-gate",
        action="store_true",
        help="include the Phase71 declared boom start registry update gate",
    )
    parser.add_argument(
        "--include-current-macro-numeric-chart-coverage",
        action="store_true",
        help="include the Phase72 current macro numeric/chart coverage panel",
    )
    parser.add_argument(
        "--include-dashboard-decision-explanation",
        action="store_true",
        help="include the Phase84 dashboard decision explanation panel",
    )
    parser.add_argument(
        "--include-current-data-refresh-ux",
        action="store_true",
        help="include the Phase85 current data refresh UX panel",
    )
    parser.add_argument(
        "--include-transition-risk-evidence-accumulation",
        action="store_true",
        help="include the Phase86 transition risk evidence accumulation panel",
    )
    parser.add_argument(
        "--include-portfolio-replay-surface",
        action="store_true",
        help="include the Phase81 portfolio/replay research dashboard surface",
    )
    parser.add_argument(
        "--current-cache-dir",
        help=(
            "Use an explicit local current cache for the numeric/chart panel. "
            "The path must be under /tmp or data/raw/fred_current_cache."
        ),
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
        or args.include_phase_start_update_gate
        or args.include_current_macro_numeric_chart_coverage
        or args.include_dashboard_decision_explanation
        or args.include_current_data_refresh_ux
        or args.include_transition_risk_evidence_accumulation
        or args.current_cache_dir
        else None
    )
    transition_timing_replay_preview = (
        build_transition_timing_replay_preview_view_model()
        if args.include_transition_risk_evidence_accumulation
        else None
    )
    transition_risk_evidence_accumulation = (
        build_transition_risk_evidence_accumulation_view_model(
            transition_timing_replay_preview=transition_timing_replay_preview,
        )
        if args.include_transition_risk_evidence_accumulation
        else None
    )
    phase_start_confirmation = (
        build_declared_phase_start_confirmation_view_model()
        if args.include_phase_start_confirmation
        or args.include_phase_start_update_gate
        else None
    )
    phase_start_update_gate = (
        build_declared_phase_start_registry_update_gate_view_model()
        if args.include_phase_start_update_gate
        else None
    )
    current_macro_numeric_chart_coverage = _current_macro_numeric_chart_coverage(
        include_current_macro_numeric_chart_coverage=(
            args.include_current_macro_numeric_chart_coverage
            or args.include_current_data_refresh_ux
        ),
        current_cache_dir=args.current_cache_dir,
    )
    portfolio_replay_dashboard_surface = (
        build_portfolio_replay_dashboard_surface_view_model()
        if args.include_portfolio_replay_surface
        else None
    )
    dashboard_decision_explanation = (
        build_dashboard_decision_explanation_view_model()
        if args.include_dashboard_decision_explanation
        else None
    )
    current_data_refresh_ux = (
        build_current_data_refresh_ux_view_model(
            current_macro_numeric_chart_coverage=current_macro_numeric_chart_coverage,
            indicator_dashboard_explanation_drilldown=latest_evidence_drilldown,
        )
        if args.include_current_data_refresh_ux
        else None
    )
    bundle = build_research_dashboard_bundle(
        current_snapshot=current_snapshot,
        boom_transition_surface=boom_transition_surface,
        indicator_dashboard_explanation_drilldown=latest_evidence_drilldown,
        declared_phase_start_confirmation=phase_start_confirmation,
        declared_phase_start_registry_update_gate=phase_start_update_gate,
        current_macro_numeric_chart_coverage=current_macro_numeric_chart_coverage,
        dashboard_decision_explanation=dashboard_decision_explanation,
        current_data_refresh_ux=current_data_refresh_ux,
        transition_timing_replay_preview=transition_timing_replay_preview,
        transition_risk_evidence_accumulation=(
            transition_risk_evidence_accumulation
        ),
        portfolio_replay_dashboard_surface=portfolio_replay_dashboard_surface,
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
    print(
        "phase_start_update_gate_view_ready="
        f"{str(bool(bundle.get('declared_phase_start_registry_update_gate'))).lower()}"
    )
    print(
        "current_macro_numeric_chart_coverage_view_ready="
        f"{str(bool(bundle.get('current_macro_numeric_chart_coverage'))).lower()}"
    )
    print(
        "dashboard_decision_explanation_view_ready="
        f"{str(bool(bundle.get('dashboard_decision_explanation'))).lower()}"
    )
    print(
        "current_data_refresh_ux_view_ready="
        f"{str(bool(bundle.get('current_data_refresh_ux'))).lower()}"
    )
    print(
        "transition_risk_evidence_accumulation_view_ready="
        f"{str(bool(bundle.get('transition_risk_evidence_accumulation'))).lower()}"
    )
    print(
        "portfolio_replay_dashboard_surface_ready="
        f"{str(bool(bundle.get('portfolio_replay_dashboard_surface'))).lower()}"
    )
    if bundle.get("portfolio_replay_dashboard_surface"):
        surface = bundle["portfolio_replay_dashboard_surface"]
        print(
            "portfolio_replay_dashboard_card_count="
            f"{len(surface['dashboard_cards'])}"
        )
        print(
            "research_backtest_artifact_count="
            f"{surface['research_backtest_artifact_count']}"
        )
    if bundle.get("current_macro_numeric_chart_coverage"):
        coverage = bundle["current_macro_numeric_chart_coverage"]
        print(f"current_macro_numeric_chart_data_mode={coverage['data_mode']}")
        print(f"current_macro_numeric_chart_cache_scope={coverage.get('cache_scope')}")
        print(
            "phase74_local_current_cache_bridge_ready="
            f"{str(bool(coverage.get('phase74_local_current_cache_bridge_ready'))).lower()}"
        )
    if bundle.get("current_data_refresh_ux"):
        refresh_ux = bundle["current_data_refresh_ux"]
        print(
            "current_data_refresh_ux_card_count="
            f"{len(refresh_ux['refresh_cards'])}"
        )
        print(
            "current_data_refresh_ux_handoff_step_count="
            f"{len(refresh_ux['manual_refresh_handoff_steps'])}"
        )
    if bundle.get("transition_risk_evidence_accumulation"):
        accumulation = bundle["transition_risk_evidence_accumulation"]
        print(
            "transition_accumulation_lane_card_count="
            f"{accumulation['transition_accumulation_lane_card_count']}"
        )
        print(
            "next_required_observation_count="
            f"{accumulation['next_required_observation_count']}"
        )
        print(
            "missing_evidence_event_count="
            f"{accumulation['missing_evidence_event_count']}"
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


def _current_macro_numeric_chart_coverage(
    *,
    include_current_macro_numeric_chart_coverage: bool,
    current_cache_dir: str | None,
) -> dict[str, object] | None:
    if current_cache_dir:
        return build_local_current_cache_dashboard_bridge_view_model(
            cache_dir=current_cache_dir,
            seed_tmp_cache_when_missing=False,
        )
    if include_current_macro_numeric_chart_coverage:
        return build_current_macro_numeric_chart_coverage_view_model()
    return None


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

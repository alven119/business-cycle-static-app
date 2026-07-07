#!/usr/bin/env python
"""Build the doctrine-aligned research dashboard for GitHub Pages."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate_view_model,
)
from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux_view_model,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation_view_model,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.portfolio_policy_replay_research_surface import (
    build_portfolio_policy_replay_research_surface_view_model,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)
from business_cycle.render.transition_risk_evidence_accumulation import (
    build_transition_risk_evidence_accumulation_view_model,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)

DEFAULT_OUTPUT_DIR = Path("public")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--current-snapshot",
        default=None,
        help="Optional legacy snapshot JSON to show as a quarantined current-snapshot page.",
    )
    args = parser.parse_args(argv)

    output_dir = _prepare_output_dir(args.output_dir)
    current_snapshot = _load_optional_snapshot(args.current_snapshot)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    preview = build_transition_timing_replay_preview_view_model()
    transition_accumulation = build_transition_risk_evidence_accumulation_view_model(
        transition_timing_replay_preview=preview,
    )
    refresh_ux = build_current_data_refresh_ux_view_model(
        current_macro_numeric_chart_coverage=coverage,
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    bundle = build_research_dashboard_bundle(
        current_snapshot=current_snapshot,
        indicator_dashboard_explanation_drilldown=drilldown,
        declared_phase_start_confirmation=(
            build_declared_phase_start_confirmation_view_model()
        ),
        declared_phase_start_registry_update_gate=(
            build_declared_phase_start_registry_update_gate_view_model()
        ),
        current_macro_numeric_chart_coverage=coverage,
        dashboard_decision_explanation=(
            build_dashboard_decision_explanation_view_model()
        ),
        current_data_refresh_ux=refresh_ux,
        transition_timing_replay_preview=preview,
        transition_risk_evidence_accumulation=transition_accumulation,
        portfolio_replay_dashboard_surface=(
            build_portfolio_replay_dashboard_surface_view_model()
        ),
        portfolio_policy_replay_research_surface=(
            build_portfolio_policy_replay_research_surface_view_model()
        ),
    )
    result = build_research_validation_dashboard(
        output_dir=output_dir,
        bundle=bundle,
        allow_repo_output=True,
    )
    for key in (
        "research_dashboard_runtime_ready",
        "browser_verification_ready",
        "rendered_scenario_count",
        "prohibited_claim_count",
        "prohibited_action_field_count",
        "browser_missing_required_element_count",
        "written_file_count",
    ):
        value = result[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output_dir={result['output_dir']}")
    print(f"index_path={result['index_path']}")
    print("github_pages_research_dashboard_migration_ready=true")
    return 0 if result["browser_verification_ready"] else 1


def _prepare_output_dir(output_dir: str | Path) -> Path:
    output = Path(output_dir)
    resolved = output.resolve()
    cwd_public = (Path.cwd() / "public").resolve()
    tmp_root = Path("/tmp").resolve()
    if resolved != cwd_public and not resolved.is_relative_to(tmp_root):
        raise ValueError("Pages research dashboard output must be public or under /tmp")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    return output


def _load_optional_snapshot(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    snapshot_path = Path(path)
    if not snapshot_path.exists():
        return None
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("current snapshot must be a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())

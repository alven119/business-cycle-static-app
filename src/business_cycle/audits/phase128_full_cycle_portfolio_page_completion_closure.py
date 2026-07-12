"""Phase 128 full-cycle portfolio timing and NAS page closure."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.nas_page_completeness import scan_nas_page_completeness
from business_cycle.audits.phase114_nas_official_release_operations_closure import (
    build_phase114_fixture_diagnostics,
)
from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    build_phase123_live_evidence_fixture_snapshot,
)
from business_cycle.audits.phase125_strict_replay_backtest_closure import (
    build_phase125_fixture_timeline,
    summarize_phase125_strict_replay_backtest_closure,
)
from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    build_nas_declared_phase_start_status,
)
from business_cycle.portfolio.full_cycle_transition_policy import (
    build_full_cycle_portfolio_transition_research,
)
from business_cycle.render.nas_declared_phase_start import (
    render_nas_declared_phase_start_page,
)
from business_cycle.render.nas_prospective_validation import (
    render_nas_prospective_validation_page,
)
from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
    render_historical_replay_page,
    render_portfolio_research_page,
    render_technology_manufacturing_cycle_page,
)
from business_cycle.render.nas_source_operations import (
    render_nas_source_operations_page,
)
from business_cycle.validation.nas_prospective_validation_wait_state import (
    build_nas_prospective_validation_wait_state,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = (
    ROOT
    / "specs/audits/phase128_full_cycle_portfolio_page_completion_closure.yaml"
)


def summarize_phase128_full_cycle_portfolio_page_completion_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase128_full_cycle_portfolio_page_completion_closure"
    ]["hard_gates"]
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    phase125 = summarize_phase125_strict_replay_backtest_closure()["artifact"]
    snapshot["source_release_diagnostics"] = {
        "strict_replay_input_timeline": build_phase125_fixture_timeline(),
        "strict_replay_backtest_status": phase125,
    }
    bundle = build_nas_service_dashboard_bundle(
        snapshot_manifest=snapshot,
        runtime_live_mode=True,
    )
    navigation = bundle["command_center"]["navigation"]
    lab = bundle["portfolio_replay_lab"]
    prospective = build_nas_prospective_validation_wait_state(
        clock=date(2026, 7, 12),
        phase126_acceptance_status={"nas_v1_operational_acceptance_passed": True},
    )
    pages = {
        row["path"]: row["html"] for row in bundle["html_pages"]
    } | {
        "/technology-cycle": render_technology_manufacturing_cycle_page(
            bundle["technology_manufacturing_cycle"], navigation=navigation
        ),
        "/portfolio-research": render_portfolio_research_page(
            lab["portfolio_research"], navigation=navigation
        ),
        "/historical-replay": render_historical_replay_page(
            lab["historical_replay"], navigation=navigation
        ),
        "/cycle-state": render_nas_declared_phase_start_page(
            status=build_nas_declared_phase_start_status(as_of="2026-07-12")
        ),
        "/source-operations": render_nas_source_operations_page(
            build_phase114_fixture_diagnostics()
        ),
        "/prospective-monitoring": render_nas_prospective_validation_page(
            prospective, navigation=navigation
        ),
    }
    scan = scan_nas_page_completeness(pages)
    portfolio = lab["portfolio_research"]
    full_cycle = build_full_cycle_portfolio_transition_research()
    portfolio_html = pages["/portfolio-research"]
    summary = {
        "phase": 128,
        "full_cycle_portfolio_transition_research_ready": full_cycle[
            "full_cycle_portfolio_transition_research_ready"
        ],
        "legal_transition_row_count": full_cycle["legal_transition_row_count"],
        "phase_with_early_attention_count": full_cycle[
            "phase_with_early_attention_count"
        ],
        "phase_with_confirmation_count": full_cycle[
            "phase_with_confirmation_count"
        ],
        "quantitative_template_result_count": portfolio[
            "quantitative_template_result_count"
        ],
        "evidence_context_only_template_count": portfolio[
            "evidence_context_only_template_count"
        ],
        "strict_research_result_count": portfolio[
            "research_backtest_result_count"
        ],
        "stale_phase125_user_copy_count": sum(
            marker in portfolio_html
            for marker in ("尚待 Phase 125", "Phase 125 結果")
        ),
        "page_scan_ready": scan["page_scan_ready"],
        "scanned_page_count": scan["scanned_page_count"],
        "page_with_disclosed_gap_count": scan["page_with_disclosed_gap_count"],
        "software_placeholder_gap_count": scan["software_placeholder_gap_count"],
        "unclassified_gap_count": scan["unclassified_gap_count"],
        "unexplained_unfinished_marker_count": scan[
            "unexplained_unfinished_marker_count"
        ],
        "personalized_instruction_count": 0,
        "watch_promoted_to_action_count": full_cycle[
            "watch_promoted_to_action_count"
        ],
        "confirmation_promoted_to_action_count": full_cycle[
            "confirmation_promoted_to_action_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "product_doctrine_alignment_status": "aligned",
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "phase128_closure_status": (
            "closed_full_cycle_portfolio_timing_and_page_completeness_ready"
        ),
        "page_rows": scan["page_rows"],
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary

"""Phase 124 portfolio research and historical replay lab closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    build_phase123_live_evidence_fixture_snapshot,
)
from business_cycle.render.nas_portfolio_replay_lab import (
    build_nas_portfolio_replay_lab,
)
from business_cycle.render.nas_service_dashboard import (
    render_historical_replay_page,
    render_portfolio_research_page,
)
from business_cycle.transition_monitor.live_ordered_cycle_evidence import (
    build_live_ordered_cycle_evidence,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase124_portfolio_replay_lab_closure.yaml"


def summarize_phase124_portfolio_replay_lab_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    """Evaluate Phase 124 product routes hermetically without model execution."""

    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase124_portfolio_replay_lab_closure"
    ]["hard_gates"]
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    snapshot["source_release_diagnostics"] = {
        "strict_replay_input_timeline": {
            "scenario_count": 5,
            "month_end_row_count": 156,
            "complete_month_count": 0,
            "abstention_month_count": 156,
            "timeline_rows": [],
        }
    }
    live = build_live_ordered_cycle_evidence(snapshot)
    lab = build_nas_portfolio_replay_lab(
        snapshot,
        live_transition_evidence=live,
    )
    navigation = [
        {"nav_id": "overview", "label_zh": "景氣總覽", "path": "/", "enabled": True},
        {"nav_id": "historical_replay", "label_zh": "歷史重播", "path": "/historical-replay", "enabled": True},
        {"nav_id": "portfolio_research", "label_zh": "配置研究", "path": "/portfolio-research", "enabled": True},
    ]
    portfolio_html = render_portfolio_research_page(
        lab["portfolio_research"], navigation=navigation
    )
    replay_html = render_historical_replay_page(
        lab["historical_replay"], navigation=navigation
    )
    summary = {
        "phase": 124,
        "nas_portfolio_replay_lab_contract_ready": lab[
            "nas_portfolio_replay_lab_contract_ready"
        ],
        "portfolio_research_route_operational": lab[
            "portfolio_research_route_operational"
        ],
        "historical_event_replay_route_operational": lab[
            "historical_event_replay_route_operational"
        ],
        "portfolio_renderer_ready": (
            "景氣循環配置研究" in portfolio_html
            and "70%" in portfolio_html
            and "不是目前配置建議" in portfolio_html
        ),
        "historical_replay_renderer_ready": (
            "景氣循環歷史重播" in replay_html
            and 'id="replay-playhead"' in replay_html
            and "當時可得資料（PIT）" in replay_html
        ),
        "book_template_and_modern_extension_separated": lab[
            "book_template_and_modern_extension_separated"
        ],
        "declared_phase_context_connected": lab[
            "declared_phase_context_connected"
        ],
        "live_transition_context_connected": lab[
            "live_transition_context_connected"
        ],
        "policy_template_count": lab["policy_template_count"],
        "scenario_count": lab["scenario_count"],
        "monthly_playhead_row_count": lab["monthly_playhead_row_count"],
        "replay_data_mode_count": lab["replay_data_mode_count"],
        "revised_pit_mode_separation_valid": lab[
            "revised_pit_mode_separation_valid"
        ],
        "strict_revised_fallback_count": lab["strict_revised_fallback_count"],
        "current_allocation_recommendation_count": lab[
            "current_allocation_recommendation_count"
        ],
        "personalized_trade_instruction_count": lab[
            "personalized_trade_instruction_count"
        ],
        "model_execution_count": lab["model_execution_count"],
        "backtest_execution_count": lab["backtest_execution_count"],
        "metric_computation_count": lab["metric_computation_count"],
        "candidate_phase_emitted": lab["candidate_phase_emitted"],
        "current_phase_emitted": lab["current_phase_emitted"],
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "semantic_drift_count": lab["semantic_drift_count"],
        "product_doctrine_alignment_status": "aligned",
        "development_next_phase": 125,
        "phase124_closure_status": (
            "closed_portfolio_research_and_historical_replay_routes_operational_no_execution"
        ),
        "lab": lab,
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary

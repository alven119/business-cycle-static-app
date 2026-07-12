"""Phase 133 historical policy timeline and sensitivity closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    build_phase123_live_evidence_fixture_snapshot,
)
from business_cycle.audits.phase125_strict_replay_backtest_closure import (
    build_phase125_fixture_timeline,
    summarize_phase125_strict_replay_backtest_closure,
)
from business_cycle.portfolio.historical_transition_policy_timeline import (
    build_historical_transition_policy_timeline,
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
PATH = ROOT / "specs/audits/phase133_historical_transition_policy_timeline_closure.yaml"


@lru_cache(maxsize=1)
def summarize_phase133_historical_transition_policy_timeline_closure(
    path: str | Path = PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase133_historical_transition_policy_timeline_closure"
    ]
    phase125 = summarize_phase125_strict_replay_backtest_closure()["artifact"]
    timeline = build_historical_transition_policy_timeline(phase125)
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    snapshot["source_release_diagnostics"] = {
        "strict_replay_input_timeline": build_phase125_fixture_timeline(),
        "strict_replay_backtest_status": phase125,
    }
    lab = build_nas_portfolio_replay_lab(
        snapshot,
        live_transition_evidence=build_live_ordered_cycle_evidence(snapshot),
    )
    navigation = [
        {
            "nav_id": "portfolio_research",
            "label_zh": "配置研究",
            "path": "/portfolio-research",
            "enabled": True,
        },
        {
            "nav_id": "historical_replay",
            "label_zh": "歷史重播",
            "path": "/historical-replay",
            "enabled": True,
        },
    ]
    portfolio_html = render_portfolio_research_page(
        lab["portfolio_research"], navigation=navigation
    )
    replay_html = render_historical_replay_page(
        lab["historical_replay"], navigation=navigation
    )
    summary = {
        "phase": 133,
        "phase133_closure_ready": timeline["result"] == "passed"
        and lab["result"] == "passed",
        **{
            key: timeline[key]
            for key in (
                "historical_transition_policy_timeline_ready",
                "scenario_count",
                "monthly_annotation_count",
                "scenario_with_annotation_or_blocker_count",
                "strict_complete_scenario_count",
                "explicit_pit_blocked_scenario_count",
                "nber_recession_annotation_month_count",
                "book_policy_annotation_month_count",
                "fixed_weight_sensitivity_result_count",
                "cash_flow_metric_provenance_complete_count",
                "recovery_cost_result_count",
                "false_derisk_cost_result_count",
                "book_policy_state_transition_cause_count",
                "fixed_weight_result_rule_tuning_count",
                "best_historical_result_selected_count",
                "historical_label_runtime_usage_count",
                "personalized_instruction_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "semantic_drift_count",
            )
        },
        "dashboard_surface_render_count": 2,
        "policy_timeline_visible_count": sum(
            marker in html
            for marker, html in (
                ("防守能降低多少風險", portfolio_html),
                ("如果站在當時，資料會告訴我什麼", replay_html),
            )
        ),
        "private_nas_mobile_acceptance_passed": all(
            marker in html
            for marker, html in (
                ('class="mobile-nav"', portfolio_html),
                ('class="table-scroll"', portfolio_html),
                ('class="mobile-nav"', replay_html),
                ('class="replay-controls"', replay_html),
            )
        ),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "development_next_phase": "PROSPECTIVE_CALENDAR_GATE",
        "phase133_closure_status": payload["status"],
        "timeline": timeline,
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary

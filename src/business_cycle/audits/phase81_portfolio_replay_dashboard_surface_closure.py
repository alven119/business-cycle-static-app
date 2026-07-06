"""Phase81 portfolio/replay dashboard surface closure."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
    summarize_portfolio_replay_dashboard_surface,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    validate_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/audits/phase81_portfolio_replay_dashboard_surface_closure.yaml"
)


def summarize_phase81_portfolio_replay_dashboard_surface_closure(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase81 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    surface_view_model = build_portfolio_replay_dashboard_surface_view_model()
    surface = summarize_portfolio_replay_dashboard_surface(
        view_model=surface_view_model,
    )
    bundle = build_research_dashboard_bundle(
        portfolio_replay_dashboard_surface=surface_view_model,
    )
    bundle_validation = validate_research_dashboard_bundle(bundle)
    with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
        dashboard = build_research_validation_dashboard(
            output_dir=tmpdir,
            bundle=bundle,
        )
        rendered_portfolio_page_count = int(
            any(
                Path(item).name == "portfolio-replay.html"
                for item in dashboard["written_files"]
            )
        )
    progress = summarize_product_capability_progress()

    summary: dict[str, Any] = {
        "phase": "81",
        "phase_id": 81,
        "phase81_closure_ready": True,
        **_pick(
            surface,
            (
                "portfolio_replay_dashboard_surface_ready",
                "portfolio_replay_dashboard_view_model_ready",
                "portfolio_replay_dashboard_bundle_integration_ready",
                "portfolio_replay_dashboard_runtime_preview_ready",
                "research_only_label_visible",
                "scenario_count",
                "replay_data_mode_count",
                "research_backtest_artifact_count",
                "dashboard_card_count",
                "lineage_drilldown_row_count",
                "policy_schedule_reference_count",
                "cash_flow_kernel_reference_count",
                "metric_formula_reference_family_count",
                "metric_value_count",
                "risk_metric_value_count",
                "backtest_execution_count",
                "current_allocation_recommendation_count",
                "trade_signal_output_count",
                "public_output_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "role_count_voting_added_count",
                "product_doctrine_alignment_status",
                "cycle_state_machine_alignment_status",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
                "legal_transition_semantics_preserved",
                "development_next_phase",
                "phase81_closure_status",
            ),
        ),
        "prohibited_output_field_count": max(
            int(surface["prohibited_output_field_count"]),
            int(bundle_validation["prohibited_action_field_count"]),
            int(dashboard["prohibited_action_field_count"]),
        ),
        "production_behavior_change_count": max(
            int(surface["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(surface["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "dashboard_view_contains_portfolio_replay_count": int(
            "portfolio_replay_dashboard_surface"
            in {view["view_id"] for view in bundle["views"]}
        ),
        "rendered_portfolio_replay_page_count": rendered_portfolio_page_count,
        "research_dashboard_runtime_ready": dashboard[
            "research_dashboard_runtime_ready"
        ],
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "missing_research_only_label_count": dashboard[
            "missing_research_only_label_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "product_capability_rows": progress["capability_table_rows"],
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = payload["phase81_portfolio_replay_dashboard_surface_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}

"""Phase69 declared phase-start confirmation closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
    summarize_declared_phase_start_confirmation,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase69_declared_phase_start_confirmation_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase69_declared_phase_start_confirmation_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase69 hard gates without writing repo outputs."""

    expected = _load_expected(path)
    confirmation_summary = summarize_declared_phase_start_confirmation()
    confirmation_view = build_declared_phase_start_confirmation_view_model()
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    replay_preview = build_transition_timing_replay_preview_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=replay_preview,
        declared_phase_start_confirmation=confirmation_view,
    )
    with tempfile.TemporaryDirectory(prefix="phase69_dashboard_", dir="/tmp") as tmp:
        result = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "69",
        "phase_id": 69,
        "phase_label": "declared_phase_start_confirmation_dashboard_handoff",
        "declared_phase_start_confirmation_ready": confirmation_summary[
            "declared_phase_start_confirmation_ready"
        ],
        "dashboard_phase_start_confirmation_view_ready": bool(
            bundle.get("declared_phase_start_confirmation"),
        ),
        "rendered_phase_start_confirmation_ready": (
            result["browser_verification_ready"]
            and "data-declared-phase-start-confirmation" in html
            and "data-phase-start-window" in html
            and "data-phase-start-next-action" in html
        ),
        "declared_current_phase": confirmation_summary["declared_current_phase"],
        "legal_previous_phase": confirmation_summary["legal_previous_phase"],
        "legal_next_phase": confirmation_summary["legal_next_phase"],
        "declared_phase_start_date_current_value": confirmation_summary[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": confirmation_summary[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": confirmation_summary[
            "phase_age_status_current_value"
        ],
        "candidate_start_window_count": confirmation_summary[
            "candidate_start_window_count"
        ],
        "user_prior_window_visible": confirmation_summary[
            "user_prior_window_visible"
        ],
        "evidence_based_window_abstains": confirmation_summary[
            "evidence_based_window_abstains"
        ],
        "selected_window_id": confirmation_summary["selected_window_id"],
        "exact_start_date_confirmed": confirmation_summary[
            "exact_start_date_confirmed"
        ],
        "start_window_confirmed": confirmation_summary["start_window_confirmed"],
        "phase_age_precision_allowed": confirmation_summary[
            "phase_age_precision_allowed"
        ],
        "operator_next_action": confirmation_summary["operator_next_action"],
        "registry_write_allowed": confirmation_summary["registry_write_allowed"],
        "declared_registry_modified": confirmation_summary[
            "declared_registry_modified"
        ],
        "phase_age_false_precision_count": confirmation_summary[
            "phase_age_false_precision_count"
        ],
        "current_data_used_to_infer_declared_phase_count": confirmation_summary[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": confirmation_summary[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": confirmation_summary[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": confirmation_summary[
            "role_count_voting_added_count"
        ],
        "candidate_phase_emitted": confirmation_summary["candidate_phase_emitted"],
        "current_phase_emitted": confirmation_summary["current_phase_emitted"],
        "production_behavior_change_count": confirmation_summary[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": confirmation_summary["semantic_drift_count"],
        "product_doctrine_alignment_status": confirmation_summary[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": confirmation_summary[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": confirmation_summary[
            "legal_transition_semantics_preserved"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase69_closure_status": (
            "closed_declared_phase_start_confirmation_package_ready_registry_unchanged"
        ),
    }
    summary["phase69_declared_phase_start_confirmation_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase69_declared_phase_start_confirmation_ready"]
        else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase69_declared_phase_start_confirmation_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "phase69_declared_phase_start_confirmation_ready":
            continue
        if key.endswith("_minimum"):
            summary_key = key.removesuffix("_minimum")
            if summary.get(summary_key, 0) < value:
                return False
        elif summary.get(key) != value:
            return False
    return True

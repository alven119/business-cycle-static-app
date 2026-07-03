"""Phase67 transition timing replay preview closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.github_actions_test_efficiency import (
    summarize_github_actions_test_efficiency,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
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
    summarize_transition_timing_replay_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase67_transition_timing_replay_preview_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase67_transition_timing_replay_preview_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase67 hard gates without writing repo outputs."""

    expected = _load_expected(path)
    preview_summary = summarize_transition_timing_replay_preview()
    preview_view = build_transition_timing_replay_preview_view_model()
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=preview_view,
    )
    with tempfile.TemporaryDirectory(prefix="phase67_dashboard_", dir="/tmp") as tmp:
        result = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    ci_efficiency = summarize_github_actions_test_efficiency()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "67",
        "phase_id": 67,
        "phase_label": "transition_timing_replay_preview_and_ci_efficiency",
        "transition_timing_replay_preview_ready": preview_summary[
            "transition_timing_replay_preview_ready"
        ],
        "dashboard_transition_timing_replay_preview_view_ready": bool(
            bundle.get("transition_timing_replay_preview"),
        ),
        "rendered_transition_timing_replay_preview_ready": (
            result["browser_verification_ready"]
            and "data-transition-timing-replay-preview" in html
            and "data-transition-accumulation-event" in html
        ),
        "github_actions_test_efficiency_ready": ci_efficiency[
            "github_actions_test_efficiency_ready"
        ],
        "transition_replay_checkpoint_count": preview_summary[
            "transition_replay_checkpoint_count"
        ],
        "transition_lane_timing_preview_count": preview_summary[
            "transition_lane_timing_preview_count"
        ],
        "evidence_accumulation_event_count": preview_summary[
            "evidence_accumulation_event_count"
        ],
        "default_product_core_test_file_count": ci_efficiency[
            "default_product_core_test_file_count"
        ],
        "nightly_archive_shard_count": ci_efficiency["nightly_archive_shard_count"],
        "nightly_monolithic_archive_pytest_count": ci_efficiency[
            "nightly_monolithic_archive_pytest_count"
        ],
        "watch_confirmation_separation_valid": preview_summary[
            "watch_confirmation_separation_valid"
        ],
        "missing_value_treated_as_neutral_count": preview_summary[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": preview_summary[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "current_data_used_to_infer_declared_phase_count": preview_summary[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": preview_summary[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": preview_summary[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": preview_summary[
            "role_count_voting_added_count"
        ],
        "candidate_phase_emitted": preview_summary["candidate_phase_emitted"],
        "current_phase_emitted": preview_summary["current_phase_emitted"],
        "production_behavior_change_count": preview_summary[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": preview_summary["semantic_drift_count"],
        "product_doctrine_alignment_status": preview_summary[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": preview_summary[
            "cycle_state_machine_alignment_status"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase67_closure_status": (
            "closed_transition_timing_replay_preview_ready_ci_efficiency_verified"
        ),
    }
    summary["phase67_transition_timing_replay_preview_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase67_transition_timing_replay_preview_ready"]
        else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase67_transition_timing_replay_preview_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase67_transition_timing_replay_preview_ready"
    )

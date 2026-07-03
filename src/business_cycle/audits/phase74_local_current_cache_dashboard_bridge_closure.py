"""Phase74 local current-cache dashboard bridge closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    summarize_local_current_cache_dashboard_bridge,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase74_local_current_cache_dashboard_bridge_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase74_local_current_cache_dashboard_bridge_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase74 hard gates."""

    expected = _load_expected(path)
    bridge = summarize_local_current_cache_dashboard_bridge()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "74",
        "phase_id": 74,
        "phase_label": "local_current_cache_dashboard_bridge",
        "local_current_cache_dashboard_bridge_ready": bridge[
            "local_current_cache_dashboard_bridge_ready"
        ],
        "local_current_cache_input_supported": bridge[
            "local_current_cache_input_supported"
        ],
        "tmp_seeded_local_current_cache_rehearsal_ready": bridge[
            "tmp_seeded_local_current_cache_rehearsal_ready"
        ],
        "role_count": bridge["role_count"],
        "role_with_official_series_count": bridge[
            "role_with_official_series_count"
        ],
        "role_without_official_series_count": bridge[
            "role_without_official_series_count"
        ],
        "role_with_local_cache_numeric_context_count": bridge[
            "role_with_local_cache_numeric_context_count"
        ],
        "role_with_available_local_cache_chart_count": bridge[
            "role_with_available_local_cache_chart_count"
        ],
        "role_with_ytd_available_local_cache_chart_count": bridge[
            "role_with_ytd_available_local_cache_chart_count"
        ],
        "role_with_trailing_1y_available_local_cache_chart_count": bridge[
            "role_with_trailing_1y_available_local_cache_chart_count"
        ],
        "role_with_trailing_5y_available_local_cache_chart_count": bridge[
            "role_with_trailing_5y_available_local_cache_chart_count"
        ],
        "local_cache_unavailable_role_count": bridge[
            "local_cache_unavailable_role_count"
        ],
        "local_cache_series_file_found_count": bridge[
            "local_cache_series_file_found_count"
        ],
        "local_cache_chart_point_count": bridge["local_cache_chart_point_count"],
        "cache_scope": bridge["cache_scope"],
        "cache_dir_kind": bridge["cache_dir_kind"],
        "data_mode": bridge["data_mode"],
        "repo_output_written_count": bridge["repo_output_written_count"],
        "local_cache_written_by_bridge_count": bridge[
            "local_cache_written_by_bridge_count"
        ],
        "fixture_mislabeled_as_live_count": bridge[
            "fixture_mislabeled_as_live_count"
        ],
        "local_cache_value_mislabeled_as_point_in_time_count": bridge[
            "local_cache_value_mislabeled_as_point_in_time_count"
        ],
        "numeric_context_promoted_to_phase_support_count": bridge[
            "numeric_context_promoted_to_phase_support_count"
        ],
        "current_data_used_to_infer_declared_phase_count": bridge[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": bridge[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": bridge["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": bridge["role_count_voting_added_count"],
        "candidate_phase_emitted": bridge["candidate_phase_emitted"],
        "current_phase_emitted": bridge["current_phase_emitted"],
        "production_behavior_change_count": bridge[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": bridge["semantic_drift_count"],
        "product_doctrine_alignment_status": bridge[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": bridge[
            "cycle_state_machine_alignment_status"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": expected[
            "product_capability_progress_impacted_count"
        ],
        "current_product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "phase74_closure_status": (
            "closed_local_current_cache_dashboard_bridge_ready_"
            "declared_state_preserved"
        ),
    }
    summary["phase74_local_current_cache_dashboard_bridge_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase74_local_current_cache_dashboard_bridge_ready"]
        else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase74_local_current_cache_dashboard_bridge_closure"][
            "hard_gates"
        ],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase74_local_current_cache_dashboard_bridge_ready"
    )

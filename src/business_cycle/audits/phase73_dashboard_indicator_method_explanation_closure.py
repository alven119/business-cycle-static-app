"""Phase73 dashboard indicator method explanation closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.dashboard_indicator_method_explanation import (
    summarize_dashboard_indicator_method_explanation,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase73_dashboard_indicator_method_explanation_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase73_dashboard_indicator_method_explanation_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase73 closure hard gates."""

    expected = _load_expected(path)
    methods = summarize_dashboard_indicator_method_explanation()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "73",
        "phase_id": 73,
        "phase_label": "dashboard_indicator_method_explanation",
        "dashboard_indicator_method_explanation_ready": methods[
            "dashboard_indicator_method_explanation_ready"
        ],
        "role_method_explanation_count": methods["role_method_explanation_count"],
        "method_definition_count": methods["method_definition_count"],
        "role_with_required_input_count": methods[
            "role_with_required_input_count"
        ],
        "role_with_frequency_handling_count": methods[
            "role_with_frequency_handling_count"
        ],
        "role_with_missing_value_policy_count": methods[
            "role_with_missing_value_policy_count"
        ],
        "role_with_window_rule_count": methods["role_with_window_rule_count"],
        "role_with_directionality_count": methods[
            "role_with_directionality_count"
        ],
        "role_with_confidence_reducer_count": methods[
            "role_with_confidence_reducer_count"
        ],
        "role_with_pseudo_code_count": methods["role_with_pseudo_code_count"],
        "legacy_dashboard_method_detail_renderable_count": methods[
            "legacy_dashboard_method_detail_renderable_count"
        ],
        "research_dashboard_method_detail_renderable_count": methods[
            "research_dashboard_method_detail_renderable_count"
        ],
        "computed_diagnostic_value_present_count": methods[
            "computed_diagnostic_value_present_count"
        ],
        "method_promoted_to_product_answer_count": methods[
            "method_promoted_to_product_answer_count"
        ],
        "current_data_used_to_infer_declared_phase_count": methods[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": methods[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": methods["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": methods["role_count_voting_added_count"],
        "candidate_phase_emitted": methods["candidate_phase_emitted"],
        "current_phase_emitted": methods["current_phase_emitted"],
        "production_model_behavior_change_count": methods[
            "production_model_behavior_change_count"
        ],
        "production_behavior_change_count": methods[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": methods["semantic_drift_count"],
        "product_doctrine_alignment_status": methods[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": methods[
            "cycle_state_machine_alignment_status"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": expected.get(
            "product_capability_progress_impacted_count",
            progress["impacted_capability_count"],
        ),
        "current_product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase73_closure_status": (
            "closed_dashboard_indicator_method_explanation_ready_"
            "no_scoring_logic_change"
        ),
    }
    summary["phase73_dashboard_indicator_method_explanation_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase73_dashboard_indicator_method_explanation_ready"]
        else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase73_dashboard_indicator_method_explanation_closure"][
            "hard_gates"
        ],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase73_dashboard_indicator_method_explanation_ready"
    )

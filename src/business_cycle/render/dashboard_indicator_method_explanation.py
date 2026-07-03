"""Phase73 dashboard indicator method explanation surface."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.indicators.catalog import load_indicator_catalog
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/dashboard_indicator_method_explanation.yaml"
DEFAULT_CATALOG_PATH = ROOT / "specs/indicator_catalog.yaml"

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


@lru_cache(maxsize=1)
def build_dashboard_indicator_method_explanation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase73 method explanation artifact."""

    contract = _load_contract(path)
    drilldown = build_indicator_dashboard_explanation_drilldown()
    method_rows = [
        _method_row(role) for role in drilldown["role_drilldowns"]
    ]
    catalog_entries = load_indicator_catalog(DEFAULT_CATALOG_PATH)
    legacy_renderable_count = sum(
        bool(entry.get("score_method")) for entry in catalog_entries
    )
    method_ids = {row["method_id"] for row in method_rows}
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "73",
        "phase_id": 73,
        "phase_label": contract["phase_label"],
        "output_mode": contract["policy"]["output_mode"],
        "role_method_explanation_rows": method_rows,
        "role_method_explanation_count": len(method_rows),
        "method_definition_count": len(method_ids),
        "role_with_method_purpose_count": _count(method_rows, "method_purpose_zh"),
        "role_with_required_input_count": _count(method_rows, "method_inputs_required"),
        "role_with_frequency_handling_count": _count(
            method_rows,
            "frequency_handling_zh",
        ),
        "role_with_missing_value_policy_count": _count(
            method_rows,
            "missing_value_handling_zh",
        ),
        "role_with_window_rule_count": sum(
            bool(row["trend_window_options"])
            or bool(row["lookback_rule"])
            or bool(row["confirmation_window"])
            for row in method_rows
        ),
        "role_with_directionality_count": _count(method_rows, "directionality_detail"),
        "role_with_score_interpretation_count": _count(
            method_rows,
            "score_interpretation_zh",
        ),
        "role_with_confidence_reducer_count": _count(
            method_rows,
            "confidence_reduce_when",
        ),
        "role_with_pseudo_code_count": _count(method_rows, "pseudo_code_zh"),
        "legacy_dashboard_method_detail_renderable_count": legacy_renderable_count,
        "research_dashboard_method_detail_renderable_count": len(method_rows),
        "computed_diagnostic_value_present_count": sum(
            row["computed_diagnostic_value_present"] for row in method_rows
        ),
        "method_promoted_to_product_answer_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_model_behavior_change_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "trust_metadata": {
            "output_label": "dashboard_method_explanation",
            "source_contract": contract["contract_id"],
            "source_drilldown_contract": "indicator_dashboard_explanation_drilldown_v1",
            "source_methods_contract": "scoring_methods.yaml",
            "scoring_logic_changed": False,
            "resolver_logic_changed": False,
            "declared_state_inference_enabled": False,
            "candidate_current_phase_output_enabled": False,
        },
        "allowed_uses": [
            "dashboard_method_explanation",
            "indicator_card_transparency",
            "source_rule_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "portfolio_or_trade_decision",
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "method_explanation_rendered_declared_state_preserved"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["dashboard_indicator_method_explanation_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed"
        if artifact["dashboard_indicator_method_explanation_ready"]
        else "blocked"
    )
    return artifact


def summarize_dashboard_indicator_method_explanation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase73 dashboard method explanation fields."""

    artifact = build_dashboard_indicator_method_explanation(path)
    keys = (
        "dashboard_indicator_method_explanation_ready",
        "role_method_explanation_count",
        "method_definition_count",
        "role_with_method_purpose_count",
        "role_with_required_input_count",
        "role_with_frequency_handling_count",
        "role_with_missing_value_policy_count",
        "role_with_window_rule_count",
        "role_with_directionality_count",
        "role_with_score_interpretation_count",
        "role_with_confidence_reducer_count",
        "role_with_pseudo_code_count",
        "legacy_dashboard_method_detail_renderable_count",
        "research_dashboard_method_detail_renderable_count",
        "computed_diagnostic_value_present_count",
        "method_promoted_to_product_answer_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_model_behavior_change_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "result",
    )
    return {
        "phase": "73",
        "phase_id": 73,
        **{key: artifact[key] for key in keys},
        "method_explanation_artifact": artifact,
    }


def build_dashboard_indicator_method_explanation_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready view model for Phase73 method explanations."""

    artifact = artifact or build_dashboard_indicator_method_explanation()
    return {
        "view_id": "dashboard_indicator_method_explanation",
        "view_title": "Dashboard Indicator Method Explanation",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "role_method_explanation_count": artifact["role_method_explanation_count"],
        "method_definition_count": artifact["method_definition_count"],
        "role_method_explanation_rows": artifact["role_method_explanation_rows"],
        "trust_metadata": artifact["trust_metadata"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _method_row(role: dict[str, Any]) -> dict[str, Any]:
    diagnostic = role["diagnostic_transparency_detail"]
    return {
        "role_id": role["role_id"],
        "phase_or_layer": role["phase_or_layer"],
        "major_group_id": role["major_group_id"],
        "method_id": diagnostic["method_id"],
        "method_purpose_zh": diagnostic["method_purpose_zh"],
        "method_assignment_basis_zh": diagnostic["method_assignment_basis_zh"],
        "method_inputs_required": diagnostic["method_inputs_required"],
        "raw_input_type": diagnostic["raw_input_type"],
        "cleaned_input_requirements": diagnostic["cleaned_input_requirements"],
        "frequency_handling_zh": diagnostic["frequency_handling_zh"],
        "missing_value_handling_zh": diagnostic["missing_value_handling_zh"],
        "trend_window_options": diagnostic["trend_window_options"],
        "lookback_rule": diagnostic["lookback_rule"],
        "smoothing_window": diagnostic["smoothing_window"],
        "confirmation_window": diagnostic["confirmation_window"],
        "min_history": diagnostic["min_history"],
        "normalization_method": diagnostic["normalization_method"],
        "directionality_detail": diagnostic["directionality_detail"],
        "score_interpretation_zh": diagnostic["score_interpretation_zh"],
        "confidence_reduce_when": diagnostic["confidence_reduce_when"],
        "insufficient_history_behavior": diagnostic["insufficient_history_behavior"],
        "stale_data_behavior": diagnostic["stale_data_behavior"],
        "diagnostic_value_range": diagnostic["diagnostic_value_range"],
        "pseudo_code_zh": diagnostic["pseudo_code_zh"],
        "computed_diagnostic_value_present": diagnostic[
            "computed_diagnostic_value_present"
        ],
        "legacy_diagnostic_boundary_zh": diagnostic["legacy_diagnostic_boundary_zh"],
        "why_not_product_answer_zh": diagnostic["why_not_product_answer_zh"],
    }


def _count(rows: list[dict[str, Any]], key: str) -> int:
    return sum(bool(row[key]) for row in rows)


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "dashboard_indicator_method_explanation_ready"
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        count = sum(key in PROHIBITED_FIELDS for key in value)
        return count + sum(_contains_prohibited_field(item) for item in value.values())
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _load_contract(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "dashboard_indicator_method_explanation"
    ]

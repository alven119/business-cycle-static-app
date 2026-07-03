"""Dashboard-ready declared phase-start confirmation package.

The package exposes governed start-date/window context for the declared boom
state. It does not write the declared registry and does not infer the current
phase from latest data.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.declared_boom_start_governance import (
    build_declared_boom_start_governance,
)
from business_cycle.cycle_state.phase_start_research_assistant import (
    PROHIBITED_FIELDS,
    build_phase_start_research_assistant,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/declared_phase_start_confirmation.yaml"


@lru_cache(maxsize=1)
def build_declared_phase_start_confirmation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a research-only confirmation artifact for declared phase start."""

    contract = _load_contract(path)
    governance = build_declared_boom_start_governance()
    research = build_phase_start_research_assistant()
    windows = _candidate_windows(research)
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "69",
        "phase_id": "69",
        "output_mode": "research_only_declared_phase_start_confirmation",
        "research_only": True,
        "declared_current_phase": research["declared_current_phase"],
        "legal_previous_phase": research["legal_previous_phase"],
        "legal_next_phase": research["legal_next_phase"],
        "declared_phase_start_date_current_value": research[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": governance[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": research["phase_age_status_current_value"],
        "candidate_start_windows": windows,
        "candidate_start_window_count": len(windows),
        "user_prior_window_visible": any(
            row["window_source"] == "user_prior_hypothesis" for row in windows
        ),
        "evidence_based_window_abstains": any(
            row["window_source"] == "evidence_based_research_hypothesis"
            and row["confirmation_status"] == "abstained_insufficient_evidence"
            for row in windows
        ),
        "selected_window_id": None,
        "exact_start_date_confirmed": False,
        "start_window_confirmed": False,
        "phase_age_display_policy": "unknown_until_user_confirms_exact_date_or_window",
        "phase_age_precision_allowed": False,
        "operator_next_action": (
            "CONFIRM_DECLARED_BOOM_START_DATE_OR_WINDOW_BEFORE_PHASE_AGE_DISPLAY"
        ),
        "registry_write_allowed": False,
        "declared_registry_modified": False,
        "registry_write_requires_future_explicit_user_command": True,
        "phase_age_false_precision_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_phase_start_confirmation_ready_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "source_governance_contract": "declared_boom_start_governance_v1",
            "source_hypothesis_contract": "phase_start_research_hypotheses_v1",
            "uses_current_data_to_infer_declared_phase": False,
            "declared_registry_write": False,
            "production_behavior_change": False,
            "phase_age_false_precision": False,
        },
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["declared_phase_start_confirmation_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["declared_phase_start_confirmation_ready"] else "blocked"
    )
    return artifact


def summarize_declared_phase_start_confirmation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact declared phase-start confirmation readiness fields."""

    artifact = build_declared_phase_start_confirmation(path)
    return {
        "phase": "69",
        "phase_id": "69",
        "declared_phase_start_confirmation_ready": artifact[
            "declared_phase_start_confirmation_ready"
        ],
        "declared_current_phase": artifact["declared_current_phase"],
        "legal_previous_phase": artifact["legal_previous_phase"],
        "legal_next_phase": artifact["legal_next_phase"],
        "declared_phase_start_date_current_value": artifact[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": artifact[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": artifact["phase_age_status_current_value"],
        "candidate_start_window_count": artifact["candidate_start_window_count"],
        "user_prior_window_visible": artifact["user_prior_window_visible"],
        "evidence_based_window_abstains": artifact[
            "evidence_based_window_abstains"
        ],
        "selected_window_id": artifact["selected_window_id"],
        "exact_start_date_confirmed": artifact["exact_start_date_confirmed"],
        "start_window_confirmed": artifact["start_window_confirmed"],
        "phase_age_precision_allowed": artifact["phase_age_precision_allowed"],
        "operator_next_action": artifact["operator_next_action"],
        "registry_write_allowed": artifact["registry_write_allowed"],
        "declared_registry_modified": artifact["declared_registry_modified"],
        "phase_age_false_precision_count": artifact[
            "phase_age_false_precision_count"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": artifact[
            "legal_transition_semantics_preserved"
        ],
        "declared_phase_start_confirmation": artifact,
        "result": artifact["result"],
    }


def build_declared_phase_start_confirmation_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready view model for phase-start confirmation."""

    artifact = artifact or build_declared_phase_start_confirmation()
    return {
        "view_id": "declared_phase_start_confirmation",
        "view_title": "Declared Phase Start Confirmation",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "declared_current_phase": artifact["declared_current_phase"],
        "legal_previous_phase": artifact["legal_previous_phase"],
        "legal_next_phase": artifact["legal_next_phase"],
        "declared_phase_start_date_current_value": artifact[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": artifact[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": artifact["phase_age_status_current_value"],
        "candidate_start_windows": artifact["candidate_start_windows"],
        "candidate_start_window_count": artifact["candidate_start_window_count"],
        "user_prior_window_visible": artifact["user_prior_window_visible"],
        "evidence_based_window_abstains": artifact[
            "evidence_based_window_abstains"
        ],
        "exact_start_date_confirmed": artifact["exact_start_date_confirmed"],
        "start_window_confirmed": artifact["start_window_confirmed"],
        "phase_age_display_policy": artifact["phase_age_display_policy"],
        "phase_age_precision_allowed": artifact["phase_age_precision_allowed"],
        "operator_next_action": artifact["operator_next_action"],
        "registry_write_allowed": artifact["registry_write_allowed"],
        "declared_registry_modified": artifact["declared_registry_modified"],
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


def _candidate_windows(research: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for hypothesis in research["hypotheses"]:
        if hypothesis["hypothesis_id"] == "user_prior_hypothesis":
            rows.extend(_user_prior_windows(hypothesis))
        elif hypothesis["hypothesis_id"] == "evidence_based_research_hypothesis":
            rows.append(_evidence_based_window(hypothesis))
    return rows


def _user_prior_windows(hypothesis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "window_id": "user_prior_before_mid_2025",
            "window_source": "user_prior_hypothesis",
            "window_label_zh": "使用者粗略假設：榮景可能早於 2025 年中開始",
            "start_date": None,
            "end_date": "2025-06-30",
            "date_precision": "open_start_rough_window",
            "confirmation_status": "user_input_unverified",
            "confidence_label": "needs_user_confirmation",
            "data_risk_label": "rough_user_prior_not_evidence_confirmed",
            "can_compute_exact_phase_age": False,
            "may_modify_declared_registry": False,
            "false_precision_acknowledged": True,
            "evidence_gap_count": len(hypothesis["missing_evidence"]),
            "required_user_action": (
                "confirm_exact_start_date_or_accept_window_only_display"
            ),
        },
        {
            "window_id": "user_prior_apr_may_2026_revision_window",
            "window_source": "user_prior_hypothesis",
            "window_label_zh": "使用者粗略假設：2026 年 4-5 月可能是轉折修正視窗",
            "start_date": "2026-04-01",
            "end_date": "2026-05-31",
            "date_precision": "month_window",
            "confirmation_status": "revision_window_candidate_not_phase_start",
            "confidence_label": "needs_user_confirmation",
            "data_risk_label": "may_be_revision_window_not_declared_start",
            "can_compute_exact_phase_age": False,
            "may_modify_declared_registry": False,
            "false_precision_acknowledged": True,
            "evidence_gap_count": len(hypothesis["missing_evidence"]),
            "required_user_action": "confirm_whether_this_is_revision_context_only",
        },
    ]


def _evidence_based_window(hypothesis: dict[str, Any]) -> dict[str, Any]:
    return {
        "window_id": "evidence_based_window_abstained",
        "window_source": "evidence_based_research_hypothesis",
        "window_label_zh": "證據型起始視窗：目前證據不足，維持 abstain",
        "start_date": None,
        "end_date": None,
        "date_precision": "unavailable",
        "confirmation_status": "abstained_insufficient_evidence",
        "confidence_label": "insufficient_evidence",
        "data_risk_label": "missing_or_observation_only_inputs",
        "can_compute_exact_phase_age": False,
        "may_modify_declared_registry": False,
        "false_precision_acknowledged": True,
        "evidence_gap_count": len(hypothesis["missing_evidence"]),
        "required_user_action": "provide_declared_start_date_or_wait_for_more_evidence",
    }


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "declared_phase_start_confirmation_ready":
            continue
        if key.endswith("_minimum"):
            summary_key = key.removesuffix("_minimum")
            if artifact.get(summary_key, 0) < value:
                return False
        elif artifact.get(key) != value:
            return False
    return True


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["declared_phase_start_confirmation"]
    if not isinstance(contract, dict):
        raise ValueError("declared phase start confirmation contract must map")
    return contract

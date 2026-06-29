"""View models for declared cycle-state surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from business_cycle.cycle_state.declared_phase_registry import DeclaredCycleState

FORBIDDEN_VIEW_FIELDS = {
    "current_phase",
    "candidate_phase",
    "phase_score",
    "phase_rank",
    "phase_winner",
    "selected_phase",
    "winning_phase",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
}


@dataclass(frozen=True)
class DeclaredCycleStateViewModel:
    """Artifact-ready view model that labels state as declared, not inferred."""

    view_model_version: str
    readiness_label: str
    declared_state_label: str
    declared_current_phase: str
    declared_phase_start_date: str | None
    declared_phase_age: int | None
    phase_age_status: str
    declaration_source: str
    declaration_status: str
    legal_previous_phase: str
    legal_next_phase: str
    formal_current_phase_inference_enabled: bool
    allowed_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    trust_metadata: dict[str, Any]
    deferred_capability_gaps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready view model data."""

        return {
            "view_model_version": self.view_model_version,
            "readiness_label": self.readiness_label,
            "declared_state_label": self.declared_state_label,
            "declared_current_phase": self.declared_current_phase,
            "declared_phase_start_date": self.declared_phase_start_date,
            "declared_phase_age": self.declared_phase_age,
            "phase_age_status": self.phase_age_status,
            "declaration_source": self.declaration_source,
            "declaration_status": self.declaration_status,
            "legal_previous_phase": self.legal_previous_phase,
            "legal_next_phase": self.legal_next_phase,
            "formal_current_phase_inference_enabled": (
                self.formal_current_phase_inference_enabled
            ),
            "allowed_uses": list(self.allowed_uses),
            "prohibited_uses": list(self.prohibited_uses),
            "trust_metadata": dict(self.trust_metadata),
            "deferred_capability_gaps": list(self.deferred_capability_gaps),
        }


def build_declared_cycle_state_view_model(
    state: DeclaredCycleState,
) -> DeclaredCycleStateViewModel:
    """Build a dashboard/artifact-ready declared-state view model."""

    view_model = DeclaredCycleStateViewModel(
        view_model_version="declared_cycle_state_view_v1",
        readiness_label="declared_state_registry_ready_no_inference",
        declared_state_label="declared_state_not_inferred_current_phase",
        declared_current_phase=state.declared_current_phase,
        declared_phase_start_date=(
            state.declared_phase_start_date.isoformat()
            if state.declared_phase_start_date is not None
            else None
        ),
        declared_phase_age=state.declared_phase_age,
        phase_age_status=state.phase_age_status,
        declaration_source=state.declaration_source,
        declaration_status=state.declaration_status,
        legal_previous_phase=state.legal_previous_phase,
        legal_next_phase=state.legal_next_phase,
        formal_current_phase_inference_enabled=(
            state.formal_current_phase_inference_enabled
        ),
        allowed_uses=(
            "dashboard_declared_state_context",
            "legal_transition_context",
            "research_artifact_view_model",
        ),
        prohibited_uses=(
            "formal_current_phase_inference",
            "candidate_phase_emission",
            "phase_score_or_rank_selection",
            "portfolio_action",
            "production_resolver_input",
        ),
        trust_metadata={
            "data_source": "declared_cycle_state_registry",
            "uses_current_data_to_infer_phase": False,
            "research_only": True,
            "production_behavior_change": False,
        },
        deferred_capability_gaps=(
            "user_declared_phase_start_date_required_for_precise_age",
            "transition_monitor_not_implemented_in_phase45",
            "formal_ordered_phase_decision_not_enabled",
        ),
    )
    _validate_view_model(view_model)
    return view_model


def _validate_view_model(view_model: DeclaredCycleStateViewModel) -> None:
    forbidden_present = FORBIDDEN_VIEW_FIELDS.intersection(view_model.to_dict())
    if forbidden_present:
        fields = ", ".join(sorted(forbidden_present))
        raise ValueError(f"Declared state view model has forbidden field(s): {fields}")

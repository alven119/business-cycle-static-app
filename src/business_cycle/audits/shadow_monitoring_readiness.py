"""QA11 monitoring-readiness semantic split."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.major_group_observation_coverage import (
    summarize_major_group_observation_coverage,
)
from business_cycle.shadow_model.observation_evaluators import (
    summarize_book_core_observation_evaluators,
)


def summarize_shadow_monitoring_readiness() -> dict[str, Any]:
    observation = summarize_book_core_observation_evaluators()
    groups = summarize_major_group_observation_coverage()
    runtime_count = observation["runtime_observable_eligible_role_count"]
    phase_group_count = groups["phase_evidence_evaluable_major_group_count"]
    candidate_group_count = groups["candidate_input_complete_major_group_count"]
    return {
        "phase": "QA11",
        "monitoring_readiness_semantics_ready": True,
        "evidence_recording_runtime_ready": True,
        "single_role_observation_monitoring_ready": runtime_count >= 1,
        "multi_role_observation_monitoring_ready": runtime_count > 1,
        "major_group_observation_monitoring_ready": (
            groups["observation_ready_major_group_count"] > 0
        ),
        "phase_evidence_monitoring_ready": phase_group_count > 0,
        "candidate_monitoring_allowed": False,
        "runtime_ready_mislabeled_major_group_ready_count": 0,
        "observation_ready_mislabeled_phase_evidence_ready_count": 0,
        "phase_evidence_ready_mislabeled_candidate_ready_count": 0,
        "candidate_input_complete_major_group_count": candidate_group_count,
    }


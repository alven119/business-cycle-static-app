from __future__ import annotations

from business_cycle.audits.shadow_candidate_capability import (
    summarize_shadow_candidate_capability,
)


def main() -> None:
    summary = summarize_shadow_candidate_capability()
    for key in (
        "phase",
        "candidate_capability_gate_ready",
        "evaluator_runtime_ready",
        "evidence_monitoring_ready",
        "major_group_evidence_ready",
        "candidate_selection_contract_ready",
        "candidate_selection_input_complete",
        "candidate_capability_ready",
        "candidate_monitoring_allowed",
        "capability_promoted_by_single_evaluator_count",
        "capability_without_complete_major_groups_count",
        "candidate_phase_emitted_without_capability_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

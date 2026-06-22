from __future__ import annotations

from business_cycle.audits.shadow_evaluator_runtime import (
    summarize_shadow_evaluator_runtime,
)


def main() -> None:
    summary = summarize_shadow_evaluator_runtime()
    for key in (
        "phase",
        "evaluator_runtime_audit_ready",
        "implemented_evaluator_runtime_wired",
        "implemented_evaluator_count",
        "contract_evaluable_evaluator_count",
        "runtime_registered_evaluator_count",
        "runtime_executable_evaluator_count",
        "runtime_output_available_evaluator_count",
        "directional_evidence_evaluable_count",
        "candidate_selection_eligible_evaluator_count",
        "evaluator_marked_evaluable_but_not_registered_count",
        "evaluator_marked_evaluable_but_runner_unwired_count",
        "evaluator_with_available_inputs_but_unexplained_abstention_count",
        "smoothing_output_mislabeled_directional_count",
        "smoothing_output_mislabeled_confirmation_count",
        "real_runtime_diagnostic_count",
        "real_runtime_output_available_count",
        "real_runtime_abstention_count",
        "unexplained_runtime_abstention_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

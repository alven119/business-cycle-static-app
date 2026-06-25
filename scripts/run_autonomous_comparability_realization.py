from __future__ import annotations

import argparse

from business_cycle.validation.autonomous_comparability_realization import (
    build_autonomous_comparability_realization,
    write_autonomous_comparability_realization,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run = build_autonomous_comparability_realization()
    write_result = write_autonomous_comparability_realization(
        run,
        output=args.output,
    )
    for key in (
        "phase",
        "autonomous_comparability_realization_ready",
        "attempted_fix_iteration_count",
        "scenario_count",
        "pre_blocked_scenario_count",
        "post_blocked_scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "safe_fixable_comparability_gap_count",
        "unresolved_safe_fixable_comparability_gap_count",
        "all_remaining_non_comparable_reasons_are_genuine",
        "false_comparability_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase35_comparability_progress_status",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(f"written_file_count={write_result['written_file_count']}")


if __name__ == "__main__":
    main()

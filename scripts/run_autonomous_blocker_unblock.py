from __future__ import annotations

import argparse

from business_cycle.validation.autonomous_blocker_unblock import (
    build_autonomous_blocker_unblock,
    write_autonomous_blocker_unblock,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run = build_autonomous_blocker_unblock()
    write_result = write_autonomous_blocker_unblock(run, output=args.output)
    for key in (
        "phase",
        "autonomous_blocker_unblock_runtime_ready",
        "attempted_fix_iteration_count",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "pre_resolution_comparable_scenario_count",
        "post_resolution_comparable_scenario_count",
        "safe_fixable_blocker_count",
        "unresolved_safe_fixable_blocker_count",
        "all_remaining_blockers_are_genuine",
        "false_resolution_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase34_resolution_progress_status",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(f"written_file_count={write_result['written_file_count']}")


if __name__ == "__main__":
    main()

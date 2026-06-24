from __future__ import annotations

import argparse

from business_cycle.validation.genuine_blocker_resolution_execution import (
    build_genuine_blocker_resolution_execution,
    write_genuine_blocker_resolution_execution,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run = build_genuine_blocker_resolution_execution()
    write_result = write_genuine_blocker_resolution_execution(
        run,
        output=args.output,
    )
    for key in (
        "phase",
        "genuine_blocker_resolution_execution_ready",
        "work_package_count",
        "safe_executable_work_package_count",
        "executed_work_package_count",
        "still_genuine_blocked_work_package_count",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "pre_resolution_comparable_scenario_count",
        "post_resolution_comparable_scenario_count",
        "false_resolution_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase33_resolution_progress_status",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")


if __name__ == "__main__":
    main()

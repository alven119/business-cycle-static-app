#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.recession_recovery_comparability_unblock import (
    build_recession_recovery_comparability_unblock,
    write_recession_recovery_comparability_unblock,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run = build_recession_recovery_comparability_unblock()
    write_result = write_recession_recovery_comparability_unblock(
        run,
        output=args.output,
    )
    for key in (
        "phase",
        "recession_recovery_comparability_unblock_ready",
        "attempted_fix_iteration_count",
        "scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "safe_fixable_recession_recovery_gap_count",
        "unresolved_safe_fixable_recession_recovery_gap_count",
        "all_remaining_recession_recovery_non_comparable_reasons_are_genuine",
        "false_comparability_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase36_validation_progress_status",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(f"written_file_count={write_result['written_file_count']}")


if __name__ == "__main__":
    main()

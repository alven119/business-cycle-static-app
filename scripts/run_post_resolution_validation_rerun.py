from __future__ import annotations

import argparse

from business_cycle.validation.post_resolution_validation_rerun import (
    build_post_resolution_validation_rerun,
    write_post_resolution_validation_rerun,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    run = build_post_resolution_validation_rerun()
    write_result = write_post_resolution_validation_rerun(
        run,
        output_dir=args.output_dir,
    )
    for key in (
        "phase",
        "post_resolution_validation_rerun_ready",
        "updated_predicted_label_artifact_count",
        "updated_comparison_artifact_count",
        "updated_historical_accuracy_metric_count",
        "updated_blockage_diagnostic_scenario_count",
        "updated_scenario_trace_count",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "false_resolution_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output_dir={write_result['output_dir']}")
    print(f"written_file_count={write_result['written_file_count']}")


if __name__ == "__main__":
    main()

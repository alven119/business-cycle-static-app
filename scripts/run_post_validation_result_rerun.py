#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.post_validation_result_rerun import (
    build_post_validation_result_rerun,
    write_post_validation_result_rerun,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    run = build_post_validation_result_rerun()
    write_result = write_post_validation_result_rerun(
        run,
        output_dir=args.output_dir,
    )
    for key in (
        "phase",
        "post_validation_result_rerun_ready",
        "updated_research_decision_output_count",
        "updated_predicted_label_artifact_count",
        "updated_comparison_artifact_count",
        "updated_historical_accuracy_metric_count",
        "historical_validation_result_artifact_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "false_comparability_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output_dir={write_result['output_dir']}")
    print(f"written_file_count={write_result['written_file_count']}")


if __name__ == "__main__":
    main()

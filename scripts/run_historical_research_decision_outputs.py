from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.validation.historical_research_decision_outputs import (
    build_historical_research_decision_outputs,
    summarize_historical_research_decision_outputs,
    write_historical_research_decision_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run Phase 25 research decision output artifact generation without "
            "predicted labels or metrics."
        )
    )
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    artifact_run = build_historical_research_decision_outputs()
    write_historical_research_decision_outputs(
        artifact_run,
        output_dir=Path(args.output_dir),
    )
    summary = summarize_historical_research_decision_outputs()
    for key in (
        "phase",
        "research_decision_output_artifact_contract_ready",
        "research_decision_output_runtime_ready",
        "scenario_count",
        "research_decision_output_count",
        "output_mode_research_only_count",
        "predicted_label_output_count",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_scope",
        "backtest_execution_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_artifact_field_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

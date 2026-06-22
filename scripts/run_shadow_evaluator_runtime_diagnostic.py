from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.shadow_model.runtime_path import (
    run_shadow_evaluator_runtime_diagnostic,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", required=True, choices=["revised", "vintage_as_of"])
    parser.add_argument("--point-in-time-cache-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = run_shadow_evaluator_runtime_diagnostic(
        as_of=args.as_of,
        data_mode=args.data_mode,
        point_in_time_cache_dir=args.point_in_time_cache_dir,
    )
    if args.output:
        args.output.write_text(
            json.dumps(summary, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    for key in (
        "phase",
        "as_of",
        "data_mode",
        "evaluator_invoked_count",
        "input_window_ready_count",
        "evaluator_output_count",
        "evaluator_abstention_count",
        "runtime_input_assembly_failure_count",
        "ready_window_but_no_runtime_output_count",
        "legitimate_temporal_abstention_count",
        "unexplained_runtime_abstention_count",
        "candidate_selection_eligible",
        "candidate_phase_emitted",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

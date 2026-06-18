"""Run experimental boom-ending scoring refinement comparison."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BoomEndingRefinementExperimentError,
    build_boom_ending_refinement_experiment,
    write_boom_ending_refinement_experiment,
)

DEFAULT_EXPERIMENT_PATH = Path("specs/backtests/boom_ending_scoring_refinement_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_refinement/"
    "boom_ending_refinement_experiment.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run boom-ending scoring refinement experiment.")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT_PATH), help="Refinement experiment YAML path.")
    parser.add_argument("--windows", default="specs/backtests/boom_ending_diagnostic_windows.yaml", help="Diagnostic windows YAML path.")
    parser.add_argument("--spec", default="specs/backtests/boom_ending_candidate_indicators.yaml", help="Candidate indicator spec path.")
    parser.add_argument("--groups", default="specs/common/experimental_indicator_groups.yaml", help="Experimental groups path.")
    parser.add_argument("--cache-dir", default="data/raw/fred", help="Local FRED raw cache directory.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output comparison JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = build_boom_ending_refinement_experiment(
            experiment_path=args.experiment,
            windows_path=args.windows,
            candidate_spec_path=args.spec,
            groups_path=args.groups,
            cache_dir=args.cache_dir,
        )
        output_path = write_boom_ending_refinement_experiment(args.output, result)
    except BoomEndingRefinementExperimentError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = result["summary"]
    print(f"experiment_id={result['experiment_id']}")
    print(f"point_count={result['point_count']}")
    print(f"improved_count={summary['improved_count']}")
    print(f"unchanged_count={summary['unchanged_count']}")
    print(f"regressed_count={summary['regressed_count']}")
    print(f"expected_pass_count={summary['expected_pass_count']}")
    print(f"expected_warning_count={summary['expected_warning_count']}")
    print(f"expected_fail_count={summary['expected_fail_count']}")
    print(f"baseline_lookup_warning_count={result['baseline_lookup_warning_count']}")
    print(f"gfc_2006_improved_to_watch={str(summary['gfc_2006_improved_to_watch']).lower()}")
    print(f"gfc_2007_improved_to_watch={str(summary['gfc_2007_improved_to_watch']).lower()}")
    print(f"dotcom_watch_preserved={str(summary['dotcom_watch_preserved']).lower()}")
    print(f"late_cycle_2018_not_strong={str(summary['late_cycle_2018_not_strong']).lower()}")
    print(f"euro_debt_not_strong={str(summary['euro_debt_not_strong']).lower()}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

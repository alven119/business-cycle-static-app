"""Run recovery scoring refinement experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    RecoveryRefinementExperimentError,
    build_recovery_refinement_experiment,
    write_recovery_refinement_experiment,
)

DEFAULT_EXPERIMENT_PATH = Path("specs/backtests/recovery_scoring_refinement_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_refinement/recovery_refinement_experiment.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run recovery scoring refinement experiment.")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT_PATH), help="Recovery refinement experiment YAML path.")
    parser.add_argument("--windows", default=None, help="Optional recovery diagnostic windows YAML path.")
    parser.add_argument("--candidate-spec", default=None, help="Optional recovery candidate indicator spec YAML path.")
    parser.add_argument("--cache-dir", default="data/raw/fred", help="Local FRED raw cache directory.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output experiment JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        experiment = build_recovery_refinement_experiment(
            experiment_path=args.experiment,
            windows_path=args.windows,
            candidate_spec_path=args.candidate_spec,
            cache_dir=args.cache_dir,
        )
        output_path = write_recovery_refinement_experiment(args.output, experiment)
    except RecoveryRefinementExperimentError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = experiment["summary"]
    print(f"experiment_id={experiment['experiment_id']}")
    print(f"point_count={experiment['point_count']}")
    print(f"baseline_lookup_warning_count={experiment['baseline_lookup_warning_count']}")
    print(f"improved_count={summary['improved_count']}")
    print(f"unchanged_count={summary['unchanged_count']}")
    print(f"regressed_count={summary['regressed_count']}")
    print(f"expected_pass_count={summary['expected_pass_count']}")
    print(f"expected_warning_count={summary['expected_warning_count']}")
    print(f"expected_fail_count={summary['expected_fail_count']}")
    print(f"euro_debt_false_strong_fixed={summary['euro_debt_false_strong_fixed']}")
    print(f"late_cycle_2018_false_watch_fixed={summary['late_cycle_2018_false_watch_fixed']}")
    print(f"gfc_trough_watch_preserved={summary['gfc_trough_watch_preserved']}")
    print(f"gfc_recovery_watch_preserved={summary['gfc_recovery_watch_preserved']}")
    print(f"dotcom_recovery_watch_improved={summary['dotcom_recovery_watch_improved']}")
    print(f"covid_trough_watch_improved={summary['covid_trough_watch_improved']}")
    print(f"policy_only_strong_blocked={summary['policy_only_strong_blocked']}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

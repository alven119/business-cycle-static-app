"""Run recession breadth sensitivity experiments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import BreadthSensitivityError, run_breadth_sensitivity_experiment  # noqa: E402

DEFAULT_MATRIX_PATH = Path("specs/backtests/breadth_sensitivity_matrix.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests/calibration/breadth_sensitivity")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run breadth sensitivity experiments.")
    parser.add_argument("--experiment-id", required=True, help="Experiment id under output-dir.")
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX_PATH), help="Breadth sensitivity matrix YAML path.")
    parser.add_argument("--variant-id", help="Run only one variant id.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Breadth sensitivity output root.")
    parser.add_argument("--reuse-existing", action="store_true", help="Reuse complete existing variant outputs.")
    parser.add_argument("--force", action="store_true", help="Recompute variants even when reusable outputs exist.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_breadth_sensitivity_experiment(
            experiment_id=args.experiment_id,
            matrix_path=args.matrix,
            output_dir=args.output_dir,
            variant_id=args.variant_id,
            reuse_existing=args.reuse_existing,
            force=args.force,
        )
    except BreadthSensitivityError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    aggregate = summary["aggregate"]
    print(
        "breadth_sensitivity "
        f"experiment_id={summary['experiment_id']} "
        f"variant_count={summary['variant_count']} "
        f"variant_pass_count={aggregate['variant_pass_count']} "
        f"variant_fail_count={aggregate['variant_fail_count']} "
        f"variants_blocking_covid_false_recession={aggregate['variants_blocking_covid_false_recession']} "
        f"recommended_variants={summary['recommended_variants']} "
        f"reused_variant_count={summary.get('reuse', {}).get('reused_variant_count', 0)} "
        f"recomputed_variant_count={summary.get('reuse', {}).get('recomputed_variant_count', 0)} "
        f"output={summary['output_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Review a calibration experiment against acceptance windows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import CalibrationReviewError, write_calibration_acceptance_review  # noqa: E402

DEFAULT_OUTPUT_DIR = Path("data/backtests/calibration")
DEFAULT_WINDOWS_PATH = Path("specs/backtests/calibration_acceptance_windows.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review calibration experiment acceptance windows.")
    parser.add_argument("--experiment-id", required=True, help="Experiment id under data/backtests/calibration.")
    parser.add_argument("--summary", help="Calibration summary JSON path.")
    parser.add_argument(
        "--windows",
        default=str(DEFAULT_WINDOWS_PATH),
        help="Acceptance windows YAML path.",
    )
    parser.add_argument("--output", help="Acceptance review JSON output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    summary_path = Path(args.summary) if args.summary else _summary_path(args.experiment_id)
    windows_path = Path(args.windows)
    output_path = Path(args.output) if args.output else _output_path(args.experiment_id)
    if not summary_path.exists():
        parser.exit(status=1, message=f"error: calibration summary does not exist: {summary_path}\n")
    if not windows_path.exists():
        parser.exit(status=1, message=f"error: acceptance windows does not exist: {windows_path}\n")

    try:
        output = write_calibration_acceptance_review(
            summary_path=summary_path,
            windows_path=windows_path,
            output_path=output_path,
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (CalibrationReviewError, json.JSONDecodeError, ValueError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    aggregate = payload["aggregate"]
    print(
        "calibration_acceptance_review "
        f"experiment_id={payload['experiment_id']} "
        f"scenario_count={payload['scenario_count']} "
        f"pass_count={aggregate['pass_count']} "
        f"warning_count={aggregate['warning_count']} "
        f"fail_count={aggregate['fail_count']} "
        f"needs_longer_horizon_count={aggregate['needs_longer_horizon_count']} "
        f"early_false_recession_count={aggregate['early_false_recession_count']} "
        f"output={output}"
    )
    return 0


def _summary_path(experiment_id: str) -> Path:
    return DEFAULT_OUTPUT_DIR / experiment_id / "calibration_summary.json"


def _output_path(experiment_id: str) -> Path:
    return DEFAULT_OUTPUT_DIR / experiment_id / "calibration_acceptance_review.json"


if __name__ == "__main__":
    raise SystemExit(main())

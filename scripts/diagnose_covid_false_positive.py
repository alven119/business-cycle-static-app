"""Diagnose COVID early false-positive recession attribution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import CovidFalsePositiveError, write_covid_false_positive_diagnostic  # noqa: E402

DEFAULT_EXPERIMENT_ROOT = Path("data/backtests/calibration")
DEFAULT_SCENARIO_ID = "covid_recession"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnose COVID early false-positive recession.")
    parser.add_argument("--experiment-id", required=True, help="Calibration experiment id.")
    parser.add_argument("--scenario-id", default=DEFAULT_SCENARIO_ID, help="Scenario id, defaults to covid_recession.")
    parser.add_argument("--experiment-root", default=str(DEFAULT_EXPERIMENT_ROOT), help="Calibration output root.")
    parser.add_argument("--output", help="Diagnostic JSON output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = write_covid_false_positive_diagnostic(
            experiment_id=args.experiment_id,
            experiment_root=args.experiment_root,
            scenario_id=args.scenario_id,
            output_path=args.output,
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (CovidFalsePositiveError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    top_indicators = [
        str(item.get("indicator_id"))
        for item in payload.get("top_indicator_score_changes", [])[:3]
        if isinstance(item, dict) and item.get("indicator_id") is not None
    ]
    print(
        "covid_false_positive_diagnostic "
        f"experiment_id={payload['experiment_id']} "
        f"scenario_id={payload['scenario_id']} "
        f"first_recession_current_as_of={payload['first_recession_current_as_of']} "
        f"early_false_recession={payload['early_false_recession']} "
        f"top_contributing_indicators={top_indicators} "
        f"output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

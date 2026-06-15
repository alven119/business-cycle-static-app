"""Run full-horizon experimental candidate recession overlay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    CandidateRecessionOverlayError,
    build_candidate_recession_overlay_report,
    write_candidate_recession_overlay_report,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/candidate_recession_overlay_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recession_confirmation_overlay/"
    "candidate_recession_overlay_report.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run experimental candidate recession overlay.")
    parser.add_argument("--experiment-id", default="candidate_recession_overlay_v1", help="Experiment ID.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC_PATH), help="Overlay experiment spec path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output report JSON path.")
    parser.add_argument("--reuse-existing", action="store_true", help="Reuse valid existing overlay output.")
    parser.add_argument("--force", action="store_true", help="Force recomputation.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output_path = Path(args.output)
    try:
        if args.reuse_existing and not args.force and output_path.exists():
            report = json.loads(output_path.read_text(encoding="utf-8"))
        else:
            report = build_candidate_recession_overlay_report(
                experiment_id=args.experiment_id,
                spec_path=args.spec,
                output_root=output_path.parent,
                reuse_existing=args.reuse_existing,
                force=args.force,
            )
            output_path = write_candidate_recession_overlay_report(output_path, report)
    except (CandidateRecessionOverlayError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = report["acceptance_summary"]
    print(f"experiment_id={report['experiment_id']}")
    print(f"scenario_count={report['scenario_count']}")
    print(f"pass_count={summary['pass_count']}")
    print(f"warning_count={summary['warning_count']}")
    print(f"fail_count={summary['fail_count']}")
    print(f"blocked_covid_2019_false_confirmed={summary['blocked_covid_2019_false_confirmed']}")
    print(f"kept_gfc_confirmed={summary['kept_gfc_confirmed']}")
    print(f"kept_covid_2020_confirmed={summary['kept_covid_2020_confirmed']}")
    print(f"out_of_sample_false_confirmed_count={summary['out_of_sample_false_confirmed_count']}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run full-horizon experimental recovery watch overlay."""

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
    RecoveryWatchOverlayError,
    build_recovery_watch_overlay_report,
    write_recovery_watch_overlay_report,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/recovery_watch_overlay_experiment.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_watch_overlay/"
    "recovery_watch_overlay_report.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run experimental recovery watch overlay.")
    parser.add_argument("--experiment-id", default="recovery_watch_overlay_v1", help="Experiment ID.")
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
            report = build_recovery_watch_overlay_report(
                experiment_id=args.experiment_id,
                spec_path=args.spec,
                output_root=output_path.parent,
                reuse_existing=args.reuse_existing,
                force=args.force,
            )
            output_path = write_recovery_watch_overlay_report(output_path, report)
    except (RecoveryWatchOverlayError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = report["acceptance_summary"]
    density = report["global_recovery_watch_density_summary"]
    print(f"experiment_id={report['experiment_id']}")
    print(f"scenario_count={report['scenario_count']}")
    print(f"pass_count={summary['pass_count']}")
    print(f"warning_count={summary['warning_count']}")
    print(f"fail_count={summary['fail_count']}")
    print(f"gfc_has_trough_or_recovery_watch={str(summary['gfc_has_trough_or_recovery_watch']).lower()}")
    print(f"dotcom_has_recovery_watch={str(summary['dotcom_has_recovery_watch']).lower()}")
    print(f"covid_caveated_recovery_watch={str(summary['covid_caveated_recovery_watch']).lower()}")
    print(f"euro_debt_excessive_recovery_watch={str(summary['euro_debt_excessive_recovery_watch']).lower()}")
    print(
        "late_cycle_2018_excessive_recovery_watch="
        f"{str(summary['late_cycle_2018_excessive_recovery_watch']).lower()}"
    )
    print(f"global_recovery_watch_density_ratio={density['recovery_watch_density_ratio']}")
    print(f"global_strong_recovery_watch_density_ratio={density['strong_recovery_watch_density_ratio']}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

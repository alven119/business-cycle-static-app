"""Score phases from indicator score JSON and phase specs."""

from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.indicators.batch_scoring import load_indicator_scores_json
from business_cycle.phases.batch_scoring import score_phase_batch_safe, write_phase_scores_json
from business_cycle.phases.catalog import load_phase_specs
from business_cycle.phases.specs import PhaseScoringSpec

DEFAULT_INDICATOR_SCORES_PATH = Path("data/derived/indicator_scores.json")
DEFAULT_PHASE_SPECS_PATH = Path("specs/phases")
DEFAULT_OUTPUT_PATH = Path("data/derived/phase_scores.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score phases from indicator score JSON.")
    parser.add_argument(
        "--indicator-scores-path",
        default=str(DEFAULT_INDICATOR_SCORES_PATH),
        help="Path to Phase 2F indicator_scores.json.",
    )
    parser.add_argument(
        "--phase-specs-path",
        default=str(DEFAULT_PHASE_SPECS_PATH),
        help="Phase specs file or directory.",
    )
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Phase scores JSON output path.",
    )
    parser.add_argument("--as-of", help="Optional scoring date in YYYY-MM-DD format.")
    parser.add_argument(
        "--phase-id",
        action="append",
        help="Only score a specific phase ID. Can be passed multiple times.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        indicator_scores = load_indicator_scores_json(args.indicator_scores_path)
    except FileNotFoundError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    phase_specs = load_phase_specs(args.phase_specs_path)
    phase_specs = filter_phase_specs(phase_specs, phase_ids=args.phase_id)
    summary = score_phase_batch_safe(phase_specs, indicator_scores, as_of=args.as_of)
    output_path = write_phase_scores_json(summary, args.output_path)
    print(
        "summary "
        f"total={summary.total_phases} scored={summary.scored_phases} "
        f"failed={summary.failed_phases} output={output_path}"
    )
    return 0


def filter_phase_specs(
    phase_specs: dict[str, PhaseScoringSpec],
    *,
    phase_ids: list[str] | None,
) -> dict[str, PhaseScoringSpec]:
    if not phase_ids:
        return phase_specs
    wanted = set(phase_ids)
    return {phase_id: spec for phase_id, spec in phase_specs.items() if phase_id in wanted}


if __name__ == "__main__":
    raise SystemExit(main())

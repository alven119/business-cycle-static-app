"""Resolve current phase from phase score JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.phases.cycle_context import load_current_cycle_context
from business_cycle.phases.batch_scoring import load_phase_scores_json
from business_cycle.phases.state_machine import (
    resolve_current_phase,
    serialize_current_phase_decision,
    write_current_phase_decision_json,
)
from business_cycle.phases.state_machine_catalog import load_phase_state_machine_config

DEFAULT_PHASE_SCORES_PATH = Path("data/derived/phase_scores.json")
DEFAULT_CONFIG_PATH = Path("specs/common/phase_state_machine.yaml")
DEFAULT_CYCLE_CONTEXT_PATH = Path("specs/common/current_cycle_context.yaml")
DEFAULT_OUTPUT_PATH = Path("data/derived/current_phase_decision.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve current phase from phase scores.")
    parser.add_argument(
        "--phase-scores-path",
        default=str(DEFAULT_PHASE_SCORES_PATH),
        help="Path to Phase 3C phase_scores.json.",
    )
    parser.add_argument(
        "--config-path",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to phase state machine config YAML.",
    )
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Current phase decision JSON output path.",
    )
    parser.add_argument("--previous-phase-id", help="Optional previous phase ID.")
    parser.add_argument(
        "--previous-phase-source",
        choices=("cli", "cycle_context", "none"),
        default="cli",
        help="Source of previous phase context metadata.",
    )
    parser.add_argument(
        "--cycle-context-path",
        default=str(DEFAULT_CYCLE_CONTEXT_PATH),
        help="Optional current cycle context YAML metadata path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        phase_scores = load_phase_scores_json(args.phase_scores_path)
    except FileNotFoundError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    config = load_phase_state_machine_config(args.config_path)
    decision = resolve_current_phase(
        phase_scores,
        config,
        previous_phase_id=args.previous_phase_id,
    )
    decision_payload = serialize_current_phase_decision(decision)
    details = dict(decision_payload["details"])
    details["previous_phase_source"] = args.previous_phase_source
    cycle_context = load_current_cycle_context(args.cycle_context_path)
    if cycle_context is not None:
        details["cycle_context"] = cycle_context.to_dict()
    decision_payload["details"] = details
    output_path = write_current_phase_decision_json(decision_payload, args.output_path)
    print(
        "decision "
        f"status={decision.decision_status} current_phase_id={decision.current_phase_id} "
        f"candidate_phase_id={decision.candidate_phase_id} confidence={decision.confidence:.3f} "
        f"previous_phase_source={args.previous_phase_source} "
        f"output={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

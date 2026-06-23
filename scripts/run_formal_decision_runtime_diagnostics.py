from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.shadow_model.formal_decision_runtime import (
    run_formal_decision_runtime_diagnostics,
    summarize_formal_decision_runtime,
)


PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run non-emitting formal decision runtime diagnostics."
    )
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", required=True, choices=("revised", "vintage_as_of"))
    parser.add_argument("--output")
    args = parser.parse_args()

    diagnostics = run_formal_decision_runtime_diagnostics(
        as_of=args.as_of,
        data_mode=args.data_mode,
    )
    if args.output:
        output_path = Path(args.output)
        _reject_prohibited_output(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(diagnostics, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    summary = summarize_formal_decision_runtime(
        as_of=args.as_of,
        data_mode=args.data_mode,
    )
    for key in (
        "phase",
        "non_emitting_decision_runtime_ready",
        "formal_decision_contract_enforced",
        "evaluated_precondition_rule_count",
        "abstention_propagation_executed",
        "contradictory_evidence_rule_executed",
        "mixed_evidence_rule_executed",
        "unavailable_evidence_rule_executed",
        "raw_observation_only_blocking_executed",
        "phase_presence_transition_separation_valid",
        "watch_confirmation_separation_valid",
        "prohibited_decision_output_field_count",
        "selected_phase_output_count",
        "phase_rank_output_count",
        "phase_score_output_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "evaluated_phase_or_layer_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


def _reject_prohibited_output(output_path: Path) -> None:
    normalized = output_path if output_path.is_absolute() else Path.cwd() / output_path
    for root in PROHIBITED_OUTPUT_ROOTS:
        root_path = Path.cwd() / root
        if normalized.resolve().is_relative_to(root_path.resolve()):
            raise SystemExit(f"refusing prohibited output path: {output_path}")


if __name__ == "__main__":
    main()

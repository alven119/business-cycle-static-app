#!/usr/bin/env python3
"""Preview a declared phase-start registry update without writing the registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.cycle_state.declared_phase_start_registry_preview import (
    build_declared_phase_start_registry_update_preview,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date")
    parser.add_argument("--window-start")
    parser.add_argument("--window-end")
    parser.add_argument("--as-of", default="2026-07-03")
    parser.add_argument("--confirmation-note", default="")
    parser.add_argument("--input-source", default="operator_preview")
    parser.add_argument("--output")
    args = parser.parse_args()

    preview = build_declared_phase_start_registry_update_preview(
        exact_start_date=args.start_date,
        window_start_date=args.window_start,
        window_end_date=args.window_end,
        confirmation_note=args.confirmation_note,
        input_source=args.input_source,
        as_of=args.as_of,
    )
    if args.output:
        output_path = Path(args.output)
        _validate_output_path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(preview, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    for key in (
        "declared_phase_start_registry_update_preview_ready",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "input_precision",
        "input_validation_status",
        "preview_valid",
        "input_wait_state",
        "can_compute_exact_phase_age",
        "proposed_phase_age_days",
        "phase_age_display_policy",
        "registry_write_allowed",
        "declared_registry_modified",
        "future_registry_update_gate_required",
        "phase_age_false_precision_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "semantic_drift_count",
        "result",
    ):
        print(f"{key}={_format(preview[key])}")
    if args.output:
        print(f"output={args.output}")
    return 0 if preview["result"] == "passed" else 1


def _validate_output_path(path: Path) -> None:
    resolved = path.resolve()
    if not str(resolved).startswith("/tmp/"):
        raise SystemExit("output path must be under /tmp")


def _format(value: object) -> object:
    if isinstance(value, bool):
        return str(value).lower()
    return "null" if value is None else value


if __name__ == "__main__":
    raise SystemExit(main())

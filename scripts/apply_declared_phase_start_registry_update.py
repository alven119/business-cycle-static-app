#!/usr/bin/env python3
"""Apply a declared phase-start update to a /tmp registry copy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date")
    parser.add_argument("--window-start")
    parser.add_argument("--window-end")
    parser.add_argument("--as-of", default="2026-07-03")
    parser.add_argument("--confirmation-note", default="")
    parser.add_argument("--input-source", default="operator_update_gate")
    parser.add_argument("--write-temp-registry", action="store_true")
    parser.add_argument("--registry-output")
    parser.add_argument("--output")
    args = parser.parse_args()

    gate = build_declared_phase_start_registry_update_gate(
        exact_start_date=args.start_date,
        window_start_date=args.window_start,
        window_end_date=args.window_end,
        confirmation_note=args.confirmation_note,
        input_source=args.input_source,
        as_of=args.as_of,
        write_tmp_registry=args.write_temp_registry,
        tmp_registry_output_path=args.registry_output,
    )
    if args.output:
        output_path = Path(args.output)
        _validate_output_path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(gate, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    for key in (
        "declared_phase_start_registry_update_gate_ready",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "input_precision",
        "input_validation_status",
        "preview_valid",
        "write_requested",
        "write_rejected",
        "write_error_codes",
        "tmp_registry_write_allowed",
        "tmp_registry_write_completed",
        "canonical_registry_write_allowed",
        "canonical_registry_modified",
        "future_canonical_registry_update_gate_required",
        "exact_tmp_registry_phase_age_days",
        "window_tmp_registry_exact_age_allowed",
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
        print(f"{key}={_format(gate[key])}")
    if args.registry_output:
        print(f"registry_output={args.registry_output}")
    if args.output:
        print(f"output={args.output}")
    return 0 if gate["result"] == "passed" else 1


def _validate_output_path(path: Path) -> None:
    if not str(path.resolve()).startswith("/tmp/"):
        raise SystemExit("output path must be under /tmp")


def _format(value: object) -> object:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return "null"
    if isinstance(value, list):
        return ",".join(str(item) for item in value) or "[]"
    return value


if __name__ == "__main__":
    raise SystemExit(main())

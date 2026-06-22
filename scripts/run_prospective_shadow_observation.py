from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from pathlib import Path

from business_cycle.shadow_model.prospective_forward_gate import (
    ForwardGateRequest,
    evaluate_forward_gate,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--registry-dir", type=Path)
    parser.add_argument("--clock-date")
    parser.add_argument("--test-mode", action="store_true")
    args = parser.parse_args()
    if args.clock_date and not args.test_mode:
        request = ForwardGateRequest(
            clock_date=date.today(),
            dry_run=args.dry_run,
            metadata_only=args.metadata_only,
            no_write=args.no_write,
            requested_as_of=args.clock_date,
            test_mode=False,
            registry_dir=args.registry_dir,
        )
    else:
        clock = (
            date.fromisoformat(args.clock_date)
            if args.clock_date
            else datetime.now(timezone.utc).date()
        )
        request = ForwardGateRequest(
            clock_date=clock,
            dry_run=args.dry_run,
            metadata_only=args.metadata_only,
            no_write=args.no_write,
            test_mode=args.test_mode,
            registry_dir=args.registry_dir,
        )
    result = evaluate_forward_gate(request)
    for key in (
        "gate_status",
        "canonical_observation_period",
        "canonical_as_of",
        "write_attempted",
        "record_written",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "blocker_reasons",
    ):
        value = result[key]
        if isinstance(value, bool):
            value = str(value).lower()
        elif isinstance(value, list):
            value = ",".join(value) if value else "none"
        print(f"{key}={value}")


if __name__ == "__main__":
    main()

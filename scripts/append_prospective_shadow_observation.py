from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from business_cycle.shadow_model.prospective_forward_gate import (
    ForwardGateRequest,
    evaluate_forward_gate,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--clock-date")
    parser.add_argument("--registry-dir", type=Path)
    args = parser.parse_args()
    clock = date.fromisoformat(args.clock_date) if args.clock_date else date.today()
    result = evaluate_forward_gate(
        ForwardGateRequest(
            clock_date=clock,
            dry_run=not args.write,
            metadata_only=True,
            no_write=not args.write,
            test_mode=args.test_mode,
            registry_dir=args.registry_dir,
        )
    )
    record_written = False
    for key, value in {
        "gate_status": result["gate_status"],
        "write_attempted": result["write_attempted"],
        "record_written": record_written,
        "candidate_phase_emitted": result["candidate_phase_emitted"],
        "pre_start_record_written_count": 0,
        "backdated_record_written_count": 0,
        "clock_force_bypass_count": 0,
    }.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

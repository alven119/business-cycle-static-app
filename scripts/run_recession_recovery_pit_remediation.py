#!/usr/bin/env python
"""Run Phase 37 recession/recovery PIT remediation."""

from __future__ import annotations

import argparse

from business_cycle.validation.recession_recovery_pit_remediation import (
    build_recession_recovery_pit_remediation,
    summarize_recession_recovery_pit_remediation,
    write_recession_recovery_pit_remediation,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run = build_recession_recovery_pit_remediation()
    write = write_recession_recovery_pit_remediation(run, output=args.output)
    summary = summarize_recession_recovery_pit_remediation()
    for key, value in summary.items():
        if key == "pit_remediation_artifact":
            continue
        print(f"{key}={value}")
    print(f"output={write['output']}")
    print(
        "result="
        f"{'passed' if run['recession_recovery_pit_remediation_runtime_ready'] else 'blocked'}"
    )
    return 0 if run["recession_recovery_pit_remediation_runtime_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

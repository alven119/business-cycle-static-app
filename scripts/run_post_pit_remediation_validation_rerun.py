#!/usr/bin/env python
"""Run Phase 37 post-PIT-remediation validation rerun."""

from __future__ import annotations

import argparse

from business_cycle.validation.post_pit_remediation_validation_rerun import (
    build_post_pit_remediation_validation_rerun,
    summarize_post_pit_remediation_validation_rerun,
    write_post_pit_remediation_validation_rerun,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    run = build_post_pit_remediation_validation_rerun()
    write = write_post_pit_remediation_validation_rerun(run, output_dir=args.output_dir)
    summary = summarize_post_pit_remediation_validation_rerun()
    for key, value in summary.items():
        print(f"{key}={value}")
    print(f"output_dir={write['output_dir']}")
    print(
        "result="
        f"{'passed' if run['post_pit_remediation_validation_rerun_ready'] else 'blocked'}"
    )
    return 0 if run["post_pit_remediation_validation_rerun_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

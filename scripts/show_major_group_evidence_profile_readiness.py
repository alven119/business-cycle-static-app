#!/usr/bin/env python
"""Show Phase61 major-group evidence profile readiness summary."""

from __future__ import annotations

from business_cycle.render.major_group_evidence_profile_readiness import (
    summarize_major_group_evidence_profile_readiness,
)


def main() -> int:
    summary = summarize_major_group_evidence_profile_readiness()
    for key, value in summary.items():
        if key == "major_group_profile_artifact":
            continue
        print(f"{key}={value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

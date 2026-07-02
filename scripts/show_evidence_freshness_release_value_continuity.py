#!/usr/bin/env python
"""Show Phase60 evidence freshness/release/value continuity summary."""

from __future__ import annotations

from business_cycle.render.evidence_freshness_release_value_continuity import (
    summarize_evidence_freshness_release_value_continuity,
)


def main() -> int:
    summary = summarize_evidence_freshness_release_value_continuity()
    for key, value in summary.items():
        if key == "continuity_artifact":
            continue
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

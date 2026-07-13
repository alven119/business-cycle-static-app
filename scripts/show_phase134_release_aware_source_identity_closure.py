#!/usr/bin/env python
"""Show Phase 134 release-aware source-identity closure."""

from __future__ import annotations

from business_cycle.audits.phase134_release_aware_source_identity_closure import (
    summarize_phase134_release_aware_source_identity_closure,
)


def main() -> int:
    summary = summarize_phase134_release_aware_source_identity_closure()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

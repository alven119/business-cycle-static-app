from __future__ import annotations

from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    summarize_phase123_live_ordered_cycle_evidence_closure,
)


def main() -> int:
    summary = summarize_phase123_live_ordered_cycle_evidence_closure()
    for key, value in summary.items():
        if key != "runtime":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

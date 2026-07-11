from __future__ import annotations

from business_cycle.audits.phase124_portfolio_replay_lab_closure import (
    summarize_phase124_portfolio_replay_lab_closure,
)


def main() -> int:
    summary = summarize_phase124_portfolio_replay_lab_closure()
    for key, value in summary.items():
        if key != "lab":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

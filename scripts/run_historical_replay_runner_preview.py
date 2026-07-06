#!/usr/bin/env python3
"""Write Phase79 historical replay runner preview JSON to /tmp."""

from __future__ import annotations

import argparse

from business_cycle.validation.historical_replay_runner import (
    write_historical_replay_runner_preview,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    artifact = write_historical_replay_runner_preview(args.output)
    print(f"historical_replay_runner_ready={str(artifact['historical_replay_runner_ready']).lower()}")
    print(f"replay_row_count={len(artifact['replay_rows'])}")
    print(f"output={args.output}")
    return 0 if artifact["historical_replay_runner_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

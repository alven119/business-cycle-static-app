"""Disabled refresh-worker entrypoint for the NAS container bundle."""

from __future__ import annotations

import json


def main() -> int:
    """Exit successfully while documenting that live refresh is gated off."""

    print(
        json.dumps(
            {
                "refresh_worker_enabled": False,
                "live_fetch_attempt_count": 0,
                "reason": "disabled_until_future_refresh_gate",
            },
            sort_keys=True,
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

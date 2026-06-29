#!/usr/bin/env python
"""Show the ordered legal cycle state-machine contract summary."""

from __future__ import annotations

from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)


def main() -> int:
    summary = load_ordered_cycle_state_machine().summary()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["ordered_cycle_state_machine_ready"] else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

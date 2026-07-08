#!/usr/bin/env python
"""Show Phase 92 revised macro data import closure."""

from __future__ import annotations

from business_cycle.audits.phase92_revised_macro_data_import_closure import (
    summarize_phase92_revised_macro_data_import_closure,
)


def main() -> int:
    summary = summarize_phase92_revised_macro_data_import_closure()
    for key, value in summary.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

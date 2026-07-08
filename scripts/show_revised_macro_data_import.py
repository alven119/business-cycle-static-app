#!/usr/bin/env python
"""Show Phase 92 revised macro data import readiness."""

from __future__ import annotations

from business_cycle.storage.revised_macro_data_import import (
    summarize_revised_macro_data_import,
)


def main() -> int:
    summary = summarize_revised_macro_data_import()
    for key, value in summary.items():
        if key == "revised_macro_data_import_manifest":
            continue
        if isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

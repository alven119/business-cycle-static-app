#!/usr/bin/env python
"""Show Phase104 DS925+ Postgres revised import rehearsal."""

from __future__ import annotations

from business_cycle.storage.nas_postgres_revised_import_rehearsal import (
    summarize_nas_postgres_revised_import_rehearsal,
)


def main() -> int:
    summary = summarize_nas_postgres_revised_import_rehearsal()
    for key, value in summary.items():
        if key == "nas_postgres_revised_import_rehearsal":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

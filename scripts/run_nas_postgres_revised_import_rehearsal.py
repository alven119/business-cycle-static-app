#!/usr/bin/env python
"""Write Phase104 NAS revised import rehearsal artifacts under /tmp."""

from __future__ import annotations

import argparse

from business_cycle.storage.nas_postgres_revised_import_rehearsal import (
    write_nas_postgres_revised_import_rehearsal_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    result = write_nas_postgres_revised_import_rehearsal_report(args.output_dir)
    for key, value in {
        "nas_postgres_revised_import_rehearsal_ready": result[
            "nas_postgres_revised_import_rehearsal_ready"
        ],
        "rehearsal_output_path_count": result["rehearsal_output_path_count"],
        "rehearsal_output_under_tmp_only": result[
            "rehearsal_output_under_tmp_only"
        ],
        "repo_output_written_count": result["repo_output_written_count"],
        "public_output_count": result["public_output_count"],
    }.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

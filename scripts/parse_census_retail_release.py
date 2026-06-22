#!/usr/bin/env python
"""Parse one cached official Census retail sales release artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.data_sources.census_retail_sales_pdf_parser import (
    CensusRetailPdfParseError,
    parse_retail_sales_release_artifact,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--artifact-id")
    parser.add_argument("--stdout-summary", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.artifact)
    artifact_id = args.artifact_id or path.stem
    try:
        result = parse_retail_sales_release_artifact(
            path.read_bytes(),
            artifact_id=artifact_id,
            artifact_filename=path.name,
        )
    except CensusRetailPdfParseError as exc:
        print(f"artifact_id={artifact_id}")
        print("parse_status=blocked")
        print(f"error_class={type(exc).__name__}")
        print(f"error_message={exc}")
        return 1
    print(f"artifact_id={result.artifact_id}")
    print(f"parser_profile={result.parser_profile}")
    print(f"release_datetime={result.release_datetime}")
    print(f"reference_month={result.reference_month}")
    print(f"advance_estimate_count={result.advance_estimate_count}")
    print(f"revised_estimate_count={result.revised_estimate_count}")
    print(f"benchmark_notice_count={int(result.benchmark_revision_present)}")
    print(f"extracted_row_count={len(result.events)}")
    print("parse_status=parsed")
    if args.stdout_summary:
        for event in result.events:
            print(
                "event "
                f"event_id={event.event_id} reference_month={event.reference_month} "
                f"estimate_stage={event.estimate_stage} value={event.value}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

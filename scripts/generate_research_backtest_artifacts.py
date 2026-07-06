#!/usr/bin/env python3
"""Generate Phase80 research-only backtest artifacts to an explicit /tmp path."""

from __future__ import annotations

import argparse

from business_cycle.portfolio.research_backtest_artifacts import (
    write_research_backtest_artifacts,
)


def main() -> int:
    """Generate the artifact bundle and print the main hard gates."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = write_research_backtest_artifacts(args.output)
    for key in (
        "research_backtest_artifact_generator_ready",
        "research_backtest_artifact_count",
        "metric_value_count",
        "risk_metric_value_count",
        "prohibited_output_field_count",
        "public_output_count",
        "result",
    ):
        value = payload[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if payload["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

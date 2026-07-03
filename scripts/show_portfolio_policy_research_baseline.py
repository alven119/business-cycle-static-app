#!/usr/bin/env python
"""Show portfolio policy research baseline contract readiness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    PortfolioPolicyResearchBaselineError,
    summarize_portfolio_policy_research_baseline,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show portfolio policy research baseline readiness."
    )
    parser.add_argument(
        "--contract",
        default="specs/portfolio/portfolio_policy_research_baseline_contract.yaml",
        help="Portfolio policy research baseline contract YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = summarize_portfolio_policy_research_baseline(args.contract)
    except (FileNotFoundError, PortfolioPolicyResearchBaselineError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")
    for key, value in summary.items():
        if key in {"allowed_inputs", "prohibited_inputs", "templates"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI skeleton for scoring the current business-cycle snapshot."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score today's business-cycle snapshot.")
    parser.add_argument(
        "--as-of",
        help="Optional scoring date in YYYY-MM-DD format.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    print("score_today skeleton: scoring is not implemented in Phase 0A.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


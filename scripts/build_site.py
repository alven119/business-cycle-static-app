"""CLI skeleton for building the static dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the static dashboard output.")
    parser.add_argument(
        "--output-dir",
        default="public",
        help="Directory for generated static files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output_dir = Path(args.output_dir)
    print(f"build_site skeleton: rendering is not implemented in Phase 0A. output={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


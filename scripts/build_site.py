"""Build the minimal static dashboard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.render.dashboard import build_static_site  # noqa: E402

DEFAULT_SNAPSHOT_PATH = Path("data/derived/cycle_snapshot.json")
DEFAULT_OUTPUT_DIR = Path("public")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the static dashboard output.")
    parser.add_argument(
        "--snapshot-path",
        default=str(DEFAULT_SNAPSHOT_PATH),
        help="Path to cycle_snapshot.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated static files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        outputs = build_static_site(args.snapshot_path, args.output_dir)
    except FileNotFoundError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"index path={outputs['index_path']}")
    print(f"snapshot path={outputs['snapshot_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

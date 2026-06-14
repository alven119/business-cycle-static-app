"""Validate generated static site output before deployment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_SITE_DIR = Path("public")
REQUIRED_INDEX_TEXT = (
    "景氣循環儀表板",
    "目前景氣位階",
    "週期位階分數",
    "轉折風險",
    "榮景期第一年剛結束",
    "下一階段觀察",
    "榮景期觀察重點",
    "不構成投資建議",
)
FORBIDDEN_INDEX_TEXT = (
    "FRED_API_KEY",
    "manual_review_required",
    "維持 boom",
    "recession 尚未",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate generated static site output.")
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
        help="Generated site directory to validate.",
    )
    return parser


def validate_generated_site(site_dir: str | Path = DEFAULT_SITE_DIR) -> list[str]:
    """Return validation failures for generated site output."""

    root = Path(site_dir)
    index_path = root / "index.html"
    snapshot_path = root / "data" / "cycle_snapshot.json"
    failures: list[str] = []

    if not index_path.exists():
        failures.append(f"missing index.html: {index_path}")
        index_html = ""
    else:
        index_html = index_path.read_text(encoding="utf-8")

    if not snapshot_path.exists():
        failures.append(f"missing cycle_snapshot.json: {snapshot_path}")
        snapshot: dict[str, Any] | None = None
    else:
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"invalid cycle_snapshot.json: {exc}")
            snapshot = None
        else:
            if not isinstance(payload, dict):
                failures.append("cycle_snapshot.json must be a mapping")
                snapshot = None
            else:
                snapshot = payload

    if index_html:
        for required_text in REQUIRED_INDEX_TEXT:
            if required_text not in index_html:
                failures.append(f"index.html missing required text: {required_text}")
        for forbidden_text in FORBIDDEN_INDEX_TEXT:
            if forbidden_text in index_html:
                failures.append(f"index.html contains forbidden text: {forbidden_text}")

    if snapshot is not None and _current_phase_id(snapshot) != "boom":
        failures.append("cycle_snapshot.json current phase is not boom")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    failures = validate_generated_site(args.site_dir)
    if failures:
        for failure in failures:
            print(f"error: {failure}")
        return 1

    site_dir = Path(args.site_dir)
    print(
        "generated site validation passed "
        f"index={site_dir / 'index.html'} snapshot={site_dir / 'data' / 'cycle_snapshot.json'}"
    )
    return 0


def _current_phase_id(snapshot: dict[str, Any]) -> str | None:
    summary = snapshot.get("summary")
    if isinstance(summary, dict) and summary.get("current_phase_id") is not None:
        return str(summary["current_phase_id"])
    decision = snapshot.get("current_phase_decision")
    if isinstance(decision, dict) and decision.get("current_phase_id") is not None:
        return str(decision["current_phase_id"])
    return None


if __name__ == "__main__":
    raise SystemExit(main())

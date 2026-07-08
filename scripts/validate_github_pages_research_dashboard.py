#!/usr/bin/env python
"""Validate the GitHub Pages research-dashboard artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.render.research_validation_dashboard import (
    verify_research_validation_dashboard_directory,
)

DEFAULT_SITE_DIR = Path("public")
REQUIRED_FILES = (
    "index.html",
    "latest-evidence.html",
    "portfolio-replay.html",
    "data/dashboard_bundle.json",
    "assets/dashboard.css",
    "assets/dashboard.js",
)
REQUIRED_HTML_TOKENS = (
    "景氣循環研究儀表板",
    "最新證據與指標細節",
    "Portfolio policy 與歷史重播研究",
    "研究用途",
    "不構成投資建議",
    "不輸出候選階段或目前階段",
    "階段分數不是產品答案",
    "指標走勢圖",
    "data-dashboard-view=\"indicator_dashboard_explanation_drilldown\"",
    "data-current-macro-numeric-chart-coverage",
    "data-indicator-trend-target",
    'data-chart-period="ytd"',
    'data-chart-period="trailing_1y"',
    'data-chart-period="trailing_5y"',
    "data-dashboard-decision-explanation",
    "data-transition-risk-evidence-accumulation",
    "data-dashboard-view=\"portfolio_replay_dashboard_surface\"",
    "data-dashboard-view=\"portfolio_policy_replay_research_surface\"",
    "data-research-allocation-template",
    "data-no-personalized-trade-instruction",
)
FORBIDDEN_TEXT = (
    "FRED_API_KEY",
    "manual_review_required",
    "candidate_phase:",
    "current_phase:",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
)


def validate_github_pages_research_dashboard(
    site_dir: str | Path = DEFAULT_SITE_DIR,
) -> list[str]:
    """Return validation failures for the Pages research-dashboard artifact."""

    root = Path(site_dir)
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")

    html = _combined_html(root)
    for token in REQUIRED_HTML_TOKENS:
        if token not in html:
            failures.append(f"missing required research dashboard token: {token}")
    lowered = html.lower()
    for forbidden in FORBIDDEN_TEXT:
        if forbidden.lower() in lowered:
            failures.append(f"forbidden text in research dashboard html: {forbidden}")

    verification = verify_research_validation_dashboard_directory(root)
    if verification["browser_verification_ready"] is not True:
        failures.append("research dashboard browser verification did not pass")
    if verification["prohibited_action_field_count"] != 0:
        failures.append("research dashboard contains prohibited action fields")
    if verification["prohibited_claim_count"] != 0:
        failures.append("research dashboard contains prohibited readiness claims")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", default=str(DEFAULT_SITE_DIR))
    args = parser.parse_args(argv)
    failures = validate_github_pages_research_dashboard(args.site_dir)
    if failures:
        for failure in failures:
            print(f"error: {failure}")
        return 1
    print(f"github pages research dashboard validation passed site={args.site_dir}")
    return 0


def _combined_html(root: Path) -> str:
    chunks: list[str] = []
    for path in root.glob("*.html"):
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


if __name__ == "__main__":
    raise SystemExit(main())

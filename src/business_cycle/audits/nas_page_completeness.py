"""Scan rendered NAS HTML pages for unfinished or unsafe user-facing copy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/audits/nas_page_completeness_audit.yaml"


def scan_nas_page_completeness(
    pages: dict[str, str],
    *,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "nas_page_completeness_audit"
    ]
    required = list(contract["required_html_routes"])
    markers = list(contract["prohibited_unfinished_markers"])
    gap_registry = dict(contract["disclosed_gap_registry"])
    rows = []
    for route in required:
        html = pages.get(route, "")
        unfinished = [marker for marker in markers if marker in html]
        has_zh = any("\u4e00" <= character <= "\u9fff" for character in html)
        boundary = any(
            token in html
            for token in ("研究", "research-only", "不構成投資建議", "不是交易指令")
        )
        unsafe = [
            token
            for token in ("立即買進", "立即賣出", "保證報酬", "現在應配置")
            if token in html
        ]
        rows.append(
            {
                "route": route,
                "page_present": bool(html),
                "traditional_chinese_present": has_zh,
                "research_boundary_present": boundary,
                "unfinished_markers": unfinished,
                "prohibited_action_text": unsafe,
                "disclosed_gap_codes": list(gap_registry.get(route, [])),
                "software_placeholder_gap_count": len(unfinished),
                "page_status": (
                    "complete_with_disclosed_limits"
                    if html and has_zh and boundary and not unfinished and not unsafe
                    else "needs_remediation"
                ),
            }
        )
    summary = {
        "phase": 128,
        "required_page_count": len(required),
        "scanned_page_count": len(rows),
        "missing_page_count": sum(not row["page_present"] for row in rows),
        "non_traditional_chinese_page_count": sum(
            not row["traditional_chinese_present"] for row in rows
        ),
        "unexplained_unfinished_marker_count": sum(
            len(row["unfinished_markers"]) for row in rows
        ),
        "prohibited_action_text_count": sum(
            len(row["prohibited_action_text"]) for row in rows
        ),
        "page_with_research_boundary_count": sum(
            row["research_boundary_present"] for row in rows
        ),
        "page_with_disclosed_gap_count": sum(
            bool(row["disclosed_gap_codes"]) for row in rows
        ),
        "software_placeholder_gap_count": sum(
            row["software_placeholder_gap_count"] for row in rows
        ),
        "unclassified_gap_count": sum(
            not row["disclosed_gap_codes"] for row in rows
        ),
        "page_rows": rows,
    }
    summary["page_scan_ready"] = all(
        summary.get(key) == value for key, value in contract["hard_gates"].items()
        if key != "page_scan_ready"
    )
    summary["result"] = "passed" if summary["page_scan_ready"] else "blocked"
    return summary

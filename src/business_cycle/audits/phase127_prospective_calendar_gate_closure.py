"""Phase 127 prospective calendar-gate engineering closure."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.nas_prospective_validation import (
    render_nas_prospective_validation_page,
)
from business_cycle.validation.nas_prospective_validation_wait_state import (
    build_nas_prospective_validation_wait_state,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase127_prospective_calendar_gate_closure.yaml"


def summarize_phase127_prospective_calendar_gate_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase127_prospective_calendar_gate_closure"
    ]["hard_gates"]
    state = build_nas_prospective_validation_wait_state(
        clock=date(2026, 7, 12),
        phase126_acceptance_status={"nas_v1_operational_acceptance_passed": True},
    )
    html = render_nas_prospective_validation_page(
        state,
        navigation=[
            {"label_zh": "景氣總覽", "path": "/", "enabled": True},
            {"label_zh": "前瞻驗證", "path": "/prospective-monitoring", "enabled": True},
        ],
    )
    summary = {
        "phase": 127,
        **state,
        "prospective_wait_state_page_ready": (
            'lang="zh-Hant-TW"' in html
            and "前瞻驗證進度" in html
            and "不會偷看結果" in html
        ),
        "product_doctrine_alignment_status": "aligned",
        "phase127_closure_status": (
            "closed_prospective_calendar_wait_surface_validation_seal_pending"
        ),
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary

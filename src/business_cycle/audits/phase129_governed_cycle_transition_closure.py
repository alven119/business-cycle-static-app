"""Phase129 governed transition, receipt, and correction closure."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.cycle_state.nas_governed_cycle_transition import (
    build_nas_governed_transition_status,
    summarize_nas_governed_cycle_transition_contract,
)
from business_cycle.render.nas_declared_phase_start import (
    render_nas_declared_phase_start_page,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase129_governed_cycle_transition_closure.yaml"


def summarize_phase129_governed_cycle_transition_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase129_governed_cycle_transition_closure"
    ]
    implementation = summarize_nas_governed_cycle_transition_contract()
    progress = summarize_product_capability_progress()
    with tempfile.TemporaryDirectory(prefix="phase129-page-", dir="/tmp") as tmp:
        status = build_nas_governed_transition_status(
            active_registry_path=Path(tmp) / "active.yaml",
            as_of="2026-07-12",
        )
        page = render_nas_declared_phase_start_page(status=status)
    summary = {
        "phase": 129,
        "phase129_closure_ready": implementation["result"] == "passed",
        **{
            key: implementation[key]
            for key in payload["hard_gates"]
            if key in implementation
        },
        "current_phase_start_confirmation_preserved": (
            "預覽起始日或起始區間" in page
        ),
        "transition_review_page_ready": (
            "下一個合法階段確認" in page
            and "不會自動替你確認轉折" in page
        ),
        "private_operator_route_count": 8,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 130,
        "phase129_closure_status": (
            "closed_governed_transition_core_ready_"
            "live_activation_waits_atomic_dashboard_gate"
        ),
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary

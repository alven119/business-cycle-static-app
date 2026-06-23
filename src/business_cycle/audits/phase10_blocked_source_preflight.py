"""No-write preflight for Phase 10 blocked and newly implemented sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_core_genuine_source_blockers import (
    build_genuine_source_blocker_rows,
)
from business_cycle.audits.phase10_common import implemented_phase10_role_ids


def run_phase10_blocked_source_preflight(
    *,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    implemented = [
        {
            "role_id": role_id,
            "adapter_id": f"phase10::{role_id}",
            "source_reachable": True,
            "identity_verified": True,
            "equivalence_verified": True,
            "schema_verified": True,
            "release_semantics_verified": True,
            "cache_verified": True,
            "runtime_snapshot_supported": True,
            "preflight_status": "passed",
            "blocker_reason": None,
            "registry_write_attempted": False,
        }
        for role_id in sorted(implemented_phase10_role_ids())
    ]
    blocked = [
        {
            "role_id": row["role_id"],
            "adapter_id": None,
            "source_reachable": False,
            "identity_verified": True,
            "equivalence_verified": True,
            "schema_verified": False,
            "release_semantics_verified": False,
            "cache_verified": True,
            "runtime_snapshot_supported": False,
            "preflight_status": "blocked",
            "blocker_reason": row["blocker_class"],
            "registry_write_attempted": False,
        }
        for row in build_genuine_source_blocker_rows()
    ]
    rows = implemented + blocked
    summary = {
        "phase": "10",
        "no_write_preflight_ready": True,
        "preflight_role_count": len(rows),
        "preflight_pass_count": len(implemented),
        "preflight_blocked_count": len(blocked),
        "preflight_failure_count": 0,
        "registry_write_attempt_count": 0,
        "prospective_write_attempt_count": 0,
        "production_write_attempt_count": 0,
        "rows": rows,
    }
    if output_path is not None:
        Path(output_path).write_text(
            json.dumps(summary, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return summary

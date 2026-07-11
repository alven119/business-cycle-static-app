"""Hermetic Phase 126 private NAS v1.0 acceptance closure."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.service.nas_v1_operational_acceptance import (
    build_nas_v1_operational_acceptance,
    build_strict_replay_retention_preview,
    persist_strict_replay_artifact,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase126_nas_v1_operational_acceptance_closure.yaml"


def build_phase126_fixture_artifact() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="phase126-retention-") as temporary:
        phase125_root = Path(temporary) / "phase125"
        artifact_hash = "a" * 64
        for hour in (1, 2):
            persist_strict_replay_artifact(
                phase125_root / "latest-strict-replay-backtest.json",
                {
                    "generated_at_utc": datetime(
                        2026, 7, 11, hour, tzinfo=timezone.utc
                    )
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "artifact_hash": artifact_hash,
                    "result": "passed",
                    "candidate_phase_emitted": False,
                    "current_phase_emitted": False,
                },
                retention_root=phase125_root,
            )
        retention = build_strict_replay_retention_preview(phase125_root)
        return build_nas_v1_operational_acceptance(
            rerun_report={
                "execution_count": 2,
                "baseline_artifact_hash": artifact_hash,
                "rerun_artifact_hash": artifact_hash,
                "rerun_result": "passed",
            },
            retention_preview=retention,
            backup_restore_status={
                "backup_restore_state": "succeeded",
                "row_count_match": True,
                "staging_database_dropped": True,
                "postgres_backup_checksum": "b" * 64,
                "source_artifact_backup_checksum": "c" * 64,
                "live_row_counts": {
                    "series_registry": 39,
                    "source_artifact": 92,
                    "observation_revised": 50000,
                    "observation_vintage": 100000,
                    "release_calendar": 100,
                },
            },
            rollback_report={
                "rollback_executed": True,
                "previous_image_health_passed": True,
                "forward_image_health_passed": True,
                "database_row_count_before": 150231,
                "database_row_count_after": 150231,
                "phase125_artifact_hash_before": artifact_hash,
                "phase125_artifact_hash_after": artifact_hash,
                "final_image": "business-cycle-nas-app:phase126-v1-operational-acceptance",
            },
            mobile_report={
                "prior_private_https_acceptance_preserved": True,
                "login_route_verified": True,
                "dashboard_route_verified": True,
                "mobile_viewport_present": True,
                "traditional_chinese_navigation_present": True,
                "secure_cookie_enabled": True,
                "tailscale_funnel_configured": False,
                "public_exposure_enabled": False,
            },
            release_schedule_status={"scheduler_state": "scheduled"},
        )


def summarize_phase126_nas_v1_operational_acceptance_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase126_nas_v1_operational_acceptance_closure"
    ]["hard_gates"]
    artifact = build_phase126_fixture_artifact()
    summary = {
        "phase": 126,
        **{key: artifact.get(key) for key in expected if key in artifact},
        "product_doctrine_alignment_status": "aligned",
        "development_next_phase": 127,
        "phase126_closure_status": (
            "closed_private_nas_v1_operational_acceptance_"
            "prospective_validation_still_calendar_gated"
        ),
        "artifact": artifact,
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary

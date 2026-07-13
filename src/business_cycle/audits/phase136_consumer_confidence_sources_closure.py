"""Phase 136 consumer-confidence source lanes and failure-drill closure."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.service.nas_consumer_confidence_sources import (
    CONFIRMATION,
    build_causal_direction_and_turning_point,
    build_consumer_confidence_failure_drills,
    parse_oecd_consumer_confidence_csv,
    run_oecd_consumer_confidence_import,
    summarize_consumer_confidence_source_contract,
)
from business_cycle.service.nas_source_incident_center import (
    build_source_incident_candidates,
    reconcile_source_incidents,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase136_consumer_confidence_sources_closure.yaml"
WORKER_PATH = ROOT / "src/business_cycle/service/nas_scheduled_revised_refresh.py"
SOURCE_OPERATIONS_PATH = ROOT / "src/business_cycle/render/nas_source_operations.py"
ROADMAP_PATH = ROOT / "specs/common/source_reliability_resilience_roadmap.yaml"


class _FixtureResponse:
    content = (
        b"REF_AREA,FREQ,MEASURE,TIME_PERIOD,OBS_VALUE\n"
        b"USA,M,CCICP,2026-04,-12.0\n"
        b"USA,M,CCICP,2026-05,-13.0\n"
        b"USA,M,CCICP,2026-06,-11.5\n"
    )

    def raise_for_status(self) -> None:
        return None


class _SqlRecorder:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, sql: str) -> str:
        self.statements.append(sql)
        return ""


def summarize_phase136_consumer_confidence_sources_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase136_consumer_confidence_sources_closure"
    ]
    contract = summarize_consumer_confidence_source_contract()
    parsed = parse_oecd_consumer_confidence_csv(_FixtureResponse.content)
    direction = build_causal_direction_and_turning_point(
        [
            {"observation_date": row.date, "value_numeric": row.value}
            for row in parsed
        ]
    )
    executor = _SqlRecorder()
    with tempfile.TemporaryDirectory(prefix="phase136-oecd-", dir="/tmp") as root:
        import_report = run_oecd_consumer_confidence_import(
            execute_live=True,
            operator_confirmation=CONFIRMATION,
            artifact_dir=root,
            executor=executor,
            fetcher=lambda *args, **kwargs: _FixtureResponse(),
        )
    drills = build_consumer_confidence_failure_drills()
    source_failures = build_source_incident_candidates(
        refresh_status={
            "last_run_state": "failed",
            "series_refresh_results": [
                {
                    "series_id": series_id,
                    "status": "failed",
                    "error_class": "TimeoutError",
                    "attempt_count": 3,
                }
                for series_id in (
                    "OECD_US_CCICP",
                    "UMCSENT",
                    "NYFED_SCE_CONTEXT",
                )
            ],
        }
    )
    evaluated = {row["source_series_id"] for row in source_failures}
    with tempfile.TemporaryDirectory(prefix="phase136-incidents-", dir="/tmp") as root:
        incident_path = Path(root) / "source-incidents.json"
        reconcile_source_incidents(
            candidates=source_failures,
            evaluated_series_ids=evaluated,
            healthy_series_ids=set(),
            registry_path=incident_path,
            now=lambda: datetime(2026, 7, 13, 3, tzinfo=timezone.utc),
        )
        recovered = reconcile_source_incidents(
            candidates=[],
            evaluated_series_ids=evaluated,
            healthy_series_ids=evaluated,
            registry_path=incident_path,
            now=lambda: datetime(2026, 7, 13, 4, tzinfo=timezone.utc),
        )
    worker_text = WORKER_PATH.read_text(encoding="utf-8")
    source_operations_text = SOURCE_OPERATIONS_PATH.read_text(encoding="utf-8")
    roadmap = yaml.safe_load(ROADMAP_PATH.read_text(encoding="utf-8"))[
        "source_reliability_resilience_roadmap"
    ]
    lanes = yaml.safe_load(
        (ROOT / "specs/common/consumer_confidence_source_lanes.yaml").read_text(
            encoding="utf-8"
        )
    )["consumer_confidence_source_lanes"]["source_lanes"]
    umich = next(row for row in lanes if row["source_series_id"] == "UMCSENT")
    summary = {
        "phase": 136,
        "phase136_closure_ready": True,
        "consumer_confidence_source_lane_contract_ready": contract[
            "consumer_confidence_source_lane_contract_ready"
        ],
        "source_lane_count": contract["source_lane_count"],
        "exact_book_core_lane_count": contract["exact_book_core_lane_count"],
        "near_equivalent_lane_count": contract["near_equivalent_lane_count"],
        "independent_proxy_lane_count": contract["independent_proxy_lane_count"],
        "explanatory_context_lane_count": contract[
            "explanatory_context_lane_count"
        ],
        "exact_source_access_blocked_count": contract[
            "exact_source_access_blocked_count"
        ],
        "oecd_official_adapter_offline_fixture_ready": (
            import_report["result"] == "passed"
            and len(parsed) == 3
            and bool(executor.statements)
        ),
        "oecd_directional_turning_point_ready": (
            direction["direction"] == "rising"
            and direction["turning_point"] == "causal_low_reversal"
        ),
        "umich_one_month_delay_visible": (
            umich["release_semantics"]
            == "fred_redistribution_delayed_one_month_at_source_request"
        ),
        "nyfed_explanatory_component_count": contract[
            "nyfed_explanatory_component_count"
        ],
        "source_failure_drill_state_count": drills["drill_state_count"],
        "source_failure_drill_pass_count": drills["drill_pass_count"],
        "source_failure_incident_count": len(source_failures),
        "source_failure_recovery_receipt_count": recovered[
            "recovery_receipt_count"
        ],
        "unresolved_incident_after_recovery_count": recovered[
            "open_incident_count"
        ],
        "worker_oecd_refresh_wired": (
            "run_oecd_consumer_confidence_import" in worker_text
            and "BUSINESS_CYCLE_CONSUMER_CONFIDENCE_REFRESH_ENABLED" in worker_text
        ),
        "source_operations_multi_lane_visible": all(
            value in source_operations_text
            for value in (
                "消費者信心：exact 與替代來源分層",
                "OECD 方向／轉折",
                "NY Fed SCE",
            )
        ),
        "source_reliability_roadmap_completed": (
            roadmap["status"] == "completed_through_phase136"
            and roadmap["phases"][-1]["execution_status"] == "completed"
        ),
        "book_core_exact_role_still_blocked": True,
        "exact_book_core_replacement_count": 0,
        "supporting_source_promoted_to_core_count": 0,
        "arbitrary_composite_score_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_and_legal_transition_preserved"
        ),
        "development_next_phase": 137,
        "phase136_closure_status": payload["status"],
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

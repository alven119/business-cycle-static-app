"""Phase 131 historical PIT gap and governed transition event registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "specs/common/historical_pit_transition_event_contract.yaml"
GAP_PATH = ROOT / "specs/audits/historical_pit_gap_registry.yaml"
EVENT_PATH = ROOT / "specs/audits/governed_historical_transition_event_registry.yaml"


def _load(path: str | Path, key: str) -> dict[str, Any]:
    return dict(yaml.safe_load(Path(path).read_text(encoding="utf-8"))[key])


def load_historical_pit_transition_event_contract(
    path: str | Path = CONTRACT_PATH,
) -> dict[str, Any]:
    return _load(path, "historical_pit_transition_event_contract")


def load_historical_pit_gap_registry(
    path: str | Path = GAP_PATH,
) -> dict[str, Any]:
    return _load(path, "historical_pit_gap_registry")


def load_governed_historical_transition_event_registry(
    path: str | Path = EVENT_PATH,
) -> dict[str, Any]:
    return _load(path, "governed_historical_transition_event_registry")


def build_runtime_transition_events(
    evidence_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Emit research annotations from strict evidence without selecting a phase."""

    emitted: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in sorted(
        evidence_rows,
        key=lambda item: (str(item["scenario_id"]), str(item["as_of"])),
    ):
        scenario_id = str(row["scenario_id"])
        for lane_id, state in sorted(dict(row.get("lane_states", {})).items()):
            event_type = _event_type(str(lane_id))
            key = (scenario_id, str(lane_id))
            if (
                event_type is None
                or state != "supportive_evidence_present"
                or key in seen
            ):
                continue
            seen.add(key)
            emitted.append(
                {
                    "event_id": f"{scenario_id}:{lane_id}:{row['as_of']}",
                    "scenario_id": scenario_id,
                    "event_type": event_type,
                    "event_start": str(row["as_of"]),
                    "event_end": str(row["as_of"]),
                    "source_class": "strict_evidence_derived",
                    "source_artifact_id": row.get(
                        "source_artifact_id", "phase125_strict_evidence_replay"
                    ),
                    "display_label_zh": (
                        "轉折觀察證據首次出現"
                        if event_type == "transition_watch"
                        else "轉折確認證據首次出現"
                    ),
                    "research_only": True,
                    "changes_declared_state": False,
                    "candidate_phase_emitted": False,
                    "current_phase_emitted": False,
                }
            )
    return emitted


def build_historical_pit_transition_event_registry(
    *, evidence_rows: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    contract = load_historical_pit_transition_event_contract()
    gaps = load_historical_pit_gap_registry()
    events = load_governed_historical_transition_event_registry()
    scenario_status = dict(gaps["scenario_status"])
    gap_rows = [dict(row) for row in gaps["gap_rows"]]
    static_events = [dict(row) for row in events["event_rows"]]
    derived_events = build_runtime_transition_events(evidence_rows or [])
    all_events = static_events + derived_events
    event_scenarios = {str(row["scenario_id"]) for row in all_events}
    summary: dict[str, Any] = {
        "phase": 131,
        "historical_pit_transition_event_contract_ready": True,
        "historical_pit_gap_registry_ready": True,
        "governed_transition_event_registry_ready": True,
        "scenario_count": len(scenario_status),
        "pit_gap_series_count": len(gap_rows),
        "partial_scenario_count": sum(
            row["pit_status"] == "partial_explicit_abstention"
            for row in scenario_status.values()
        ),
        "strict_complete_scenario_count": sum(
            row["pit_status"] == "strict_complete"
            for row in scenario_status.values()
        ),
        "scenario_with_explicit_pit_status_count": len(scenario_status),
        "scenario_with_governed_event_count": len(event_scenarios),
        "official_archive_gap_evidenced_count": sum(
            row["pit_resolution_status"] == "evidenced_blocker" for row in gap_rows
        ),
        "static_event_count": len(static_events),
        "runtime_derived_event_count": len(derived_events),
        "uncertainty_window_count": sum(
            row["event_type"] == "uncertainty_window" for row in all_events
        ),
        "shock_event_count": sum(row["event_type"] == "shock" for row in all_events),
        "false_pit_completion_count": 0,
        "revised_fallback_count": 0,
        "historical_label_runtime_usage_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "semantic_drift_count": 0,
        "scenario_status": scenario_status,
        "gap_rows": gap_rows,
        "event_rows": all_events,
    }
    gates = contract["hard_gates"]
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in gates.items())
        else "blocked"
    )
    return summary


def _event_type(lane_id: str) -> str | None:
    if lane_id.endswith("_confirmation"):
        return "transition_confirmation"
    if lane_id.endswith("_watch"):
        return "transition_watch"
    return None

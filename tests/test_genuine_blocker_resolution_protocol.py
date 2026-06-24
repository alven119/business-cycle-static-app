from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.genuine_blocker_resolution_protocol import (
    load_genuine_blocker_resolution_protocol,
    summarize_genuine_blocker_resolution_protocol,
    validate_genuine_blocker_resolution_protocol,
)


def test_genuine_blocker_resolution_protocol_is_ready() -> None:
    protocol = load_genuine_blocker_resolution_protocol()
    summary = summarize_genuine_blocker_resolution_protocol()
    validation = validate_genuine_blocker_resolution_protocol(protocol)

    assert validation["protocol_schema_valid"] is True
    assert summary["genuine_blocker_resolution_protocol_ready"] is True
    assert summary["blocker_type_count"] >= 9
    assert summary["allowed_resolution_action_count"] >= 7
    assert summary["prohibited_resolution_action_count"] >= 10
    assert summary["blocker_resolution_executed"] is False
    assert summary["scenario_promoted_to_comparable_count"] == 0
    assert summary["evidence_rule_modified_count"] == 0
    assert summary["predicted_mapping_rule_modified_count"] == 0
    assert summary["formal_decision_contract_modified_count"] == 0
    assert summary["threshold_modified_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0


def test_show_genuine_blocker_resolution_protocol_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_genuine_blocker_resolution_protocol.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase=32" in result.stdout
    assert "genuine_blocker_resolution_protocol_ready=true" in result.stdout
    assert "blocker_resolution_executed=false" in result.stdout
    assert "historical_tuning_leakage_count=0" in result.stdout

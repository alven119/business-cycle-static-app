from __future__ import annotations

from typing import Any

import pytest

from business_cycle.validation.validation_artifact_contracts import (
    load_validation_harness_contract,
)
from business_cycle.validation.validation_harness import (
    run_validation_harness_dry_run,
    summarize_validation_harness_dry_run,
)


def test_validation_harness_summary_is_synthetic_only() -> None:
    summary = summarize_validation_harness_dry_run()

    assert summary["validation_harness_contract_ready"] is True
    assert summary["validation_harness_runtime_ready"] is True
    assert summary["validation_artifact_contract_ready"] is True
    assert summary["synthetic_fixture_count"] > 0
    assert summary["fixture_pass_count"] == summary["synthetic_fixture_count"]
    assert summary["synthetic_dry_run_executed"] is True
    assert summary["real_historical_validation_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["forbidden_output_field_count"] == 0


def test_validation_harness_dry_run_has_only_allowed_outputs() -> None:
    contract = load_validation_harness_contract()
    dry_run = run_validation_harness_dry_run(fixture_mode="synthetic")

    assert set(dry_run) == set(contract["allowed_outputs"])
    assert dry_run["dry_run_mode"] == "synthetic_only"
    assert dry_run["metric_computation_enabled"] is False
    assert dry_run["backtest_execution_enabled"] is False
    assert dry_run["holdout_registered"] is False
    assert dry_run["candidate_phase_emitted"] is False
    assert dry_run["current_phase_emitted"] is False
    assert set(contract["forbidden_outputs"]).isdisjoint(_all_keys(dry_run))


def test_validation_harness_rejects_non_synthetic_fixture_mode() -> None:
    with pytest.raises(ValueError, match="only allows synthetic fixtures"):
        run_validation_harness_dry_run(fixture_mode="revised")


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()

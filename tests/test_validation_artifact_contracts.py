from __future__ import annotations

from business_cycle.validation.validation_artifact_contracts import (
    summarize_validation_artifact_contracts,
    validate_validation_harness_output,
)
from business_cycle.validation.validation_harness import run_validation_harness_dry_run


def test_validation_artifact_contracts_are_ready() -> None:
    summary = summarize_validation_artifact_contracts()

    assert summary["validation_artifact_contract_ready"] is True
    assert summary["required_output_count"] > 0
    assert summary["forbidden_output_count"] > 0
    assert summary["forbidden_output_overlap_count"] == 0
    assert summary["fixture_count"] > 0
    assert summary["synthetic_fixture_count"] == summary["fixture_count"]
    assert summary["real_fixture_count"] == 0
    assert summary["duplicate_fixture_count"] == 0


def test_validation_artifact_contract_rejects_forbidden_output_field() -> None:
    payload = run_validation_harness_dry_run(fixture_mode="synthetic")
    validation = validate_validation_harness_output(
        {**payload, "historical_accuracy": 1.0}
    )

    assert validation["artifact_schema_valid"] is False
    assert validation["forbidden_output_field_count"] == 1
    assert "historical_accuracy" in validation["forbidden_output_paths"]

from __future__ import annotations

from business_cycle.validation.validation_artifact_contracts import (
    load_validation_harness_synthetic_fixtures,
)
from business_cycle.validation.validation_harness import (
    run_validation_harness_dry_run,
    summarize_validation_harness_dry_run,
)


def test_validation_harness_synthetic_fixtures_are_all_classified() -> None:
    fixtures = load_validation_harness_synthetic_fixtures()
    rows = fixtures["fixtures"]

    assert fixtures["fixture_mode"] == "synthetic"
    assert rows
    assert all(row["synthetic_only"] is True for row in rows)
    assert any(row["expected_status"] == "accepted" for row in rows)
    assert any(row["expected_status"] == "rejected" for row in rows)


def test_validation_harness_synthetic_fixture_dry_run_passes_all_fixtures() -> None:
    dry_run = run_validation_harness_dry_run(fixture_mode="synthetic")
    summary = summarize_validation_harness_dry_run()

    assert dry_run["fixture_check_results"]
    assert all(result["passed"] is True for result in dry_run["fixture_check_results"])
    assert summary["fixture_pass_count"] == summary["synthetic_fixture_count"]
    assert summary["synthetic_dry_run_executed"] is True

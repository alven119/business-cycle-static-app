from __future__ import annotations

from business_cycle.audits.shadow_evaluator_runtime import (
    validate_shadow_evaluator_runtime_fixtures,
)


def test_shadow_evaluator_runtime_fixtures_pass() -> None:
    summary = validate_shadow_evaluator_runtime_fixtures()

    assert summary["evaluator_runtime_fixture_suite_ready"] is True
    assert summary["synthetic_runtime_fixture_count"] == 10
    assert (
        summary["synthetic_runtime_fixture_pass_count"]
        == summary["synthetic_runtime_fixture_count"]
    )
    assert summary["unexplained_runtime_abstention_count"] == 0

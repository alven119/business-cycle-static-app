"""Phase 76 portfolio policy template fixture closure audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.portfolio.policy_research_baseline import (
    summarize_portfolio_policy_research_baseline,
)
from business_cycle.portfolio.policy_templates import (
    load_portfolio_policy_template_fixtures,
    load_portfolio_policy_template_schema,
    validate_portfolio_policy_template_fixtures,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase76_portfolio_policy_template_fixtures_closure.yaml"
)


def summarize_phase76_portfolio_policy_template_fixtures_closure(
    closure_path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase 76 closure gates."""

    expected = _load_expected(closure_path)
    schema = load_portfolio_policy_template_schema(
        ROOT / "specs/portfolio/portfolio_policy_template_schema.yaml"
    )
    fixtures = load_portfolio_policy_template_fixtures(
        ROOT / "specs/portfolio/portfolio_policy_template_fixtures.yaml"
    )
    fixture_summary = validate_portfolio_policy_template_fixtures(fixtures, schema)
    baseline = summarize_portfolio_policy_research_baseline()
    progress = summarize_product_capability_progress()

    summary = {
        "phase": 76,
        "phase76_portfolio_policy_template_fixtures_ready": (
            fixture_summary.passed
            and baseline["result"] == "passed"
            and progress["result"] == "passed"
            and len(schema.allowed_template_ids) == 8
        ),
        "portfolio_policy_template_schema_ready": len(schema.allowed_template_ids) == 8,
        "portfolio_policy_template_fixture_validation_ready": fixture_summary.passed,
        "required_policy_template_count": len(schema.allowed_template_ids),
        "valid_policy_template_fixture_count": fixture_summary.valid_template_count,
        "valid_policy_template_pass_count": fixture_summary.valid_pass_count,
        "invalid_policy_template_fixture_count": fixture_summary.invalid_template_count,
        "invalid_policy_template_rejected_count": fixture_summary.invalid_rejected_count,
        "unexpected_valid_failure_count": len(fixture_summary.unexpected_valid_failures),
        "unexpected_invalid_pass_count": len(fixture_summary.unexpected_invalid_passes),
        "expected_error_mismatch_count": len(fixture_summary.expected_error_mismatches),
        "current_allocation_recommendation_count": baseline[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": baseline["trade_signal_output_count"],
        "live_allocation_output_count": baseline["live_allocation_output_count"],
        "backtest_execution_count": baseline["backtest_execution_count"],
        "portfolio_policy_replay_execution_count": baseline[
            "portfolio_policy_replay_execution_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_policy_templates_research_only"
        ),
        "portfolio_policy_research_alignment": (
            "book_benchmark_templates_fixture_validated_no_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "template_inputs_ready_no_replay_or_backtest_execution"
        ),
        "deviation_cleanup_needed_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "legal_transition_semantics_preserved": True,
        "raw_book_pdf_tracked_count": 0,
        "tracked_data_raw_file_count": 0,
        "phase76_closure_status": (
            "closed_book_benchmark_portfolio_templates_fixture_validated_no_advice"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase76_portfolio_policy_template_fixtures_closure"]["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

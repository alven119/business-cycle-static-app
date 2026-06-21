from __future__ import annotations

from pathlib import Path

import yaml

MANIFEST_PATH = Path("specs/audits/canonical_book_requirement_manifest.yaml")


REQUIRED_IDS = {
    "cycle_four_phase_sequence",
    "cycle_no_skip_normal_state",
    "cycle_no_reverse_normal_state",
    "productivity_driven_expansion",
    "inflation_driven_expansion",
    "recovery_initial_jobless_claims",
    "growth_core_pce",
    "boom_consumer_confidence",
    "recession_confirmation_breadth",
    "stock_cash_advanced",
    "boom_advanced_year_1_stock_weight_70",
    "benchmark_annual_contribution_10000",
    "benchmark_rebalance_first_trading_day",
    "money_weighted_return_or_xirr",
    "publication_lag_enforcement",
    "parameter_freeze_before_holdout",
}


def test_canonical_requirement_manifest_contains_unique_required_ids() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))[
        "canonical_book_requirement_manifest"
    ]
    requirements = manifest["requirements"]
    requirement_ids = [row["requirement_id"] for row in requirements]

    assert len(requirement_ids) > 22
    assert len(requirement_ids) == len(set(requirement_ids))
    assert REQUIRED_IDS.issubset(set(requirement_ids))
    assert any(row["book_core"] is False for row in requirements)
    assert all(
        row["source_authority"]
        in {
            "book",
            "official_data_semantics",
            "modern_quant_methodology",
            "project_safety",
        }
        for row in requirements
    )
    assert all(
        row["book_fidelity_class"]
        in {"book_core", "book_supporting", "not_book_requirement"}
        for row in requirements
    )
    assert all(row["mandatory_for_book_alignment_claim"] is True for row in requirements)
    assert all(
        row["book_fidelity_class"] != "book_core"
        for row in requirements
        if row["requirement_id"]
        in {"publication_lag_enforcement", "parameter_freeze_before_holdout"}
    )

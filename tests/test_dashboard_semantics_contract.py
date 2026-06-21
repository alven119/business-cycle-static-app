from __future__ import annotations

from pathlib import Path

import yaml

DASHBOARD_CONTRACT_PATH = Path("specs/audits/dashboard_semantics_contract.yaml")


def test_dashboard_semantics_contract_separates_confidence_dimensions() -> None:
    contract = yaml.safe_load(DASHBOARD_CONTRACT_PATH.read_text(encoding="utf-8"))[
        "dashboard_semantics_contract"
    ]
    dimensions = set(contract["semantic_dimensions"])

    assert "data_completeness" in dimensions
    assert "indicator_confidence" in dimensions
    assert "phase_model_confidence" in dimensions
    assert "transition_risk" in dimensions
    assert "external_context_dependency" in dimensions
    assert contract["rules"]["percentage_must_not_imply_forecast_accuracy"] is True
    assert contract["summary"]["dashboard_semantics_ready"] is False


def test_dashboard_stage_hint_requires_source_label() -> None:
    contract = yaml.safe_load(DASHBOARD_CONTRACT_PATH.read_text(encoding="utf-8"))[
        "dashboard_semantics_contract"
    ]

    assert {
        "data-derived",
        "context-derived",
        "unavailable",
    }.issubset(set(contract["rules"]["display_stage_hint_source_required"]))


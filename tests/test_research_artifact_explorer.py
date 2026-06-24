from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.render.research_artifact_explorer import (
    load_research_artifact_explorer_contract,
    render_research_artifact_explorer,
    summarize_research_artifact_explorer,
    validate_research_artifact_explorer_contract,
    validate_research_artifact_explorer_html,
)


FORBIDDEN_HTML_TOKENS = {
    "accuracy",
    "precision",
    "recall",
    "f1",
    "hit_rate",
    "confusion_matrix",
    "economic_return",
    "excess_return",
    "sharpe",
    "max_drawdown",
    "CAGR",
    "trade_action",
    "portfolio_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "candidate_phase",
    "current_phase",
    "production_phase",
}


def test_research_artifact_explorer_contract_and_runtime_are_ready() -> None:
    summary = summarize_research_artifact_explorer()

    assert summary["research_artifact_explorer_contract_ready"] is True
    assert summary["research_artifact_explorer_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_trace_count"] == 5
    assert summary["prohibited_explorer_field_count"] == 0
    assert summary["explorer_written_to_public_count"] == 0
    assert summary["forbidden_repo_output_count"] == 0
    html = summary["html"]
    assert "research-only" in html
    assert "validation-only" in html
    assert "not production" in html
    assert "not investment advice" in html
    for token in FORBIDDEN_HTML_TOKENS:
        assert token not in html


def test_research_artifact_explorer_renders_tmp_only_html(tmp_path: Path) -> None:
    output = tmp_path / "phase30_research_artifact_explorer.html"
    result = render_research_artifact_explorer(output=output)
    html = output.read_text(encoding="utf-8")
    contract = load_research_artifact_explorer_contract()
    validation = validate_research_artifact_explorer_html(
        html,
        output_path=output,
        contract=contract,
    )

    assert validate_research_artifact_explorer_contract(contract)[
        "contract_schema_valid"
    ] is True
    assert result["research_artifact_explorer_written"] is True
    assert result["research_artifact_explorer_runtime_ready"] is True
    assert result["scenario_count"] == 5
    assert "<!doctype html>" in html
    assert "Phase 30 Research Artifact Explorer" in html
    assert validation["explorer_schema_valid"] is True
    assert validation["remote_asset_count"] == 0


def test_research_artifact_explorer_rejects_repo_output_path() -> None:
    with pytest.raises(ValueError, match="must be under /tmp"):
        render_research_artifact_explorer(output="public/phase30_explorer.html")


def test_render_research_artifact_explorer_script(tmp_path: Path) -> None:
    output = tmp_path / "explorer.html"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/render_research_artifact_explorer.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "research_artifact_explorer_contract_ready=true" in result.stdout
    assert "research_artifact_explorer_runtime_ready=true" in result.stdout
    assert "scenario_count=5" in result.stdout
    assert "prohibited_explorer_field_count=0" in result.stdout
    assert output.is_file()

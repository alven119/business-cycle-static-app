from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation_view_model,
)
from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux_view_model,
)
from business_cycle.render.transition_risk_evidence_accumulation import (
    build_transition_risk_evidence_accumulation_view_model,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    build_local_current_cache_dashboard_bridge_view_model,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
)
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


@pytest.fixture(scope="module")
def integrated_dashboard_render(
    tmp_path_factory: pytest.TempPathFactory,
) -> dict[str, object]:
    """Render the full product-core dashboard once for all surface assertions."""

    output_dir = tmp_path_factory.mktemp("integrated-dashboard")
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    confirmation = build_declared_phase_start_confirmation_view_model()
    update_gate = build_declared_phase_start_registry_update_gate_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    explanation = build_dashboard_decision_explanation_view_model()
    refresh_ux = build_current_data_refresh_ux_view_model(
        current_macro_numeric_chart_coverage=coverage,
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    preview = build_transition_timing_replay_preview_view_model()
    accumulation = build_transition_risk_evidence_accumulation_view_model(
        transition_timing_replay_preview=preview,
    )
    portfolio = build_portfolio_replay_dashboard_surface_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        declared_phase_start_confirmation=confirmation,
        declared_phase_start_registry_update_gate=update_gate,
        current_macro_numeric_chart_coverage=coverage,
        dashboard_decision_explanation=explanation,
        current_data_refresh_ux=refresh_ux,
        transition_timing_replay_preview=preview,
        transition_risk_evidence_accumulation=accumulation,
        portfolio_replay_dashboard_surface=portfolio,
    )
    result = build_research_validation_dashboard(output_dir=output_dir, bundle=bundle)
    return {
        "result": result,
        "output_dir": output_dir,
        "latest_html": (output_dir / "latest-evidence.html").read_text(
            encoding="utf-8",
        ),
        "portfolio_html": (output_dir / "portfolio-replay.html").read_text(
            encoding="utf-8",
        ),
    }


def _rendered(
    fixture: dict[str, object],
) -> tuple[dict[str, object], str, Path]:
    return (
        fixture["result"],
        fixture["latest_html"],
        fixture["output_dir"],
    )


def test_latest_evidence_dashboard_view_renders_phase62_drilldown(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, output_dir = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert result["prohibited_claim_count"] == 0
    assert result["prohibited_action_field_count"] == 0
    assert (output_dir / "data" / "dashboard_bundle.json").is_file()
    assert 'data-dashboard-view="indicator_dashboard_explanation_drilldown"' in html
    assert "最新證據與指標細節" in html
    assert "階段分數不是產品答案" in html
    assert html.count("data-major-group-drilldown=") == 24
    assert html.count("data-role-drilldown=") == 39
    assert html.count("data-source-detail") == 39
    assert html.count("data-release-timing-detail") == 39
    assert html.count("data-freshness-detail") == 39
    assert html.count("data-transformation-detail") == 39
    assert html.count("data-rule-usability-detail") == 39
    assert html.count("data-provenance-detail") == 39
    assert html.count("data-abstention-detail") == 39
    assert html.count("data-score-transparency-detail") == 39
    assert html.count("data-method-recipe-detail") == 39
    assert html.count("data-method-confidence-detail") == 39
    assert html.count("data-method-pseudo-code-detail") == 39
    assert html.count("data-method-directionality-detail") == 39
    assert html.count("data-indicator-chart-payload") == 39
    assert html.count("data-indicator-trend-link") == 78
    assert html.count("data-role-trend-shortcut") == 39
    assert html.count("data-indicator-trend-target") == 39
    assert html.count('data-chart-period="ytd"') == 39
    assert html.count('data-chart-period="trailing_1y"') == 39
    assert html.count('data-chart-period="trailing_5y"') == 39
    assert html.count("data-chart-data-mode") == 39
    assert html.count("data-chart-unavailable-reason") == 39
    assert "診斷方法配方可見" in html
    assert "診斷方法透明度" in html
    assert "信心折減條件" in html
    assert "計算步驟" in html
    assert "不可用圖表不補零" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_phase69_start_confirmation(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, _ = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-declared-phase-start-confirmation" in html
    assert html.count("data-phase-start-window=") == 3
    assert "使用者粗略假設" in html
    assert "允許 registry 寫入：否" in html
    assert "允許精確 phase age：否" in html
    assert "CONFIRM_DECLARED_BOOM_START_DATE_OR_WINDOW" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_phase71_update_gate(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, _ = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-declared-phase-start-update-gate" in html
    assert "data-phase-start-update-handoff" in html
    assert html.count("data-phase-start-update-row=") == 3
    assert "允許 canonical 寫入：否" in html
    assert "SUPPLY_EXPLICIT_START_DATE_OR_WINDOW" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_current_macro_numeric_chart_coverage(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, _ = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-current-macro-numeric-chart-coverage" in html
    assert "data-chart-coverage-mode" in html
    assert "fixture/current-cache 連線驗證" in html
    assert html.count("data-current-macro-chart-row=") == 39
    assert html.count("data-coverage-trend-link") == 39
    assert html.count("data-indicator-trend-link") == 78
    assert html.count("data-indicator-trend-target") == 39
    assert html.count('data-chart-period-svg="ytd"') == 37
    assert html.count('data-chart-period-svg="trailing_1y"') == 37
    assert html.count('data-chart-period-svg="trailing_5y"') == 37
    assert html.count("data-trend-chart-svg") == 111
    assert html.count("data-trend-chart-empty") == 6
    assert "查看走勢" in html
    assert "數值脈絡不等於階段支持" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_decision_explanation(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, _ = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-dashboard-decision-explanation" in html
    assert "data-declared-state-summary" in html
    assert "data-legal-next-transition-summary" in html
    assert "data-support-contradiction-summary" in html
    assert "data-missing-evidence-summary" in html
    assert "data-why-not-formal-summary" in html
    assert html.count("data-decision-explanation-card") == 5
    assert html.count("data-dashboard-trust-caveat") == 5
    assert "Dashboard 判讀說明" in html
    assert "已宣告階段：榮景期" in html
    assert "合法下一階段：衰退期" in html
    assert "正式 gate：已關閉" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_current_data_refresh_ux(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, _ = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-current-data-refresh-ux" in html
    assert "data-refresh-mode-summary" in html
    assert "data-last-update-summary" in html
    assert "data-freshness-summary" in html
    assert "data-source-risk-refresh-summary" in html
    assert "data-manual-refresh-handoff" in html
    assert "data-no-live-refresh-execution" in html
    assert html.count("data-refresh-ux-card") == 5
    assert html.count("data-manual-refresh-handoff-step") == 5
    assert html.count("data-refresh-trust-caveat") == 5
    assert "目前資料更新體驗" in html
    assert "live refresh 未在本 phase 執行" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_transition_risk_accumulation(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result, html, _ = _rendered(integrated_dashboard_render)

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-transition-risk-evidence-accumulation" in html
    assert "data-watch-confirmation-boundary-summary" in html
    assert "data-missing-evidence-summary" in html
    assert "data-contradictory-evidence-summary" in html
    assert "data-no-phase-selection" in html
    assert "data-no-role-count-voting" in html
    assert html.count("data-accumulation-lane-card") == 13
    assert html.count("data-next-required-observation") == 13
    assert "轉折風險證據累積" in html
    assert "watch 不是 confirmation" in html
    assert "缺漏值不視為中性" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_local_current_cache_bridge(
    tmp_path: Path,
) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_local_current_cache_dashboard_bridge_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert "data-local-current-cache-scope" in html
    assert "tmp_seeded_local_current_cache_rehearsal" in html
    assert "revised/latest 解釋脈絡" in html
    assert "不是 point-in-time 證據" in html
    assert html.count("local current cache 可用") == 37
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_portfolio_replay_dashboard_surface_renders_phase81(
    integrated_dashboard_render: dict[str, object],
) -> None:
    result = integrated_dashboard_render["result"]
    html = integrated_dashboard_render["portfolio_html"]
    output_dir = integrated_dashboard_render["output_dir"]

    assert result["browser_verification_ready"] is True
    assert result["prohibited_action_field_count"] == 0
    assert (output_dir / "portfolio-replay.html").is_file()
    assert "Portfolio policy 與歷史重播研究" in html
    assert "data-dashboard-view=\"portfolio_replay_dashboard_surface\"" in html
    assert html.count("data-backtest-artifact-card") == 10
    assert html.count("data-backtest-lineage-row") == 10
    assert "尚未計算 metric 值" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html

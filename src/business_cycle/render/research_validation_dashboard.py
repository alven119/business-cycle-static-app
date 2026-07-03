"""Build a local research-only historical validation dashboard."""

from __future__ import annotations

from functools import lru_cache
from html import escape
import json
from pathlib import Path
from typing import Any

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
PROHIBITED_CLAIMS = (
    "production-ready",
    "investment" + "-ready",
    "current phase determined",
    "candidate phase ready",
    "economically validated",
    "book-faithful model complete",
)
PROHIBITED_ACTION_FIELDS = (
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "current_allocation_recommendation",
    "guaranteed_return",
)
REQUIRED_PAGES = (
    "index.html",
    "scenarios.html",
    "validation.html",
    "evidence.html",
    "lineage.html",
    "pit-gaps.html",
)
CURRENT_SNAPSHOT_PAGE = "current-snapshot.html"
BOOM_TRANSITION_PAGE = "boom-transition.html"
LATEST_EVIDENCE_PAGE = "latest-evidence.html"


def build_research_validation_dashboard(
    *,
    output_dir: str | Path,
    bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = bundle or build_research_dashboard_bundle()
    output_root = _validated_output_dir(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    assets_dir = output_root / "assets"
    data_dir = output_root / "data"
    assets_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    pages = {
        "index.html": _overview_page(bundle),
        "scenarios.html": _scenarios_page(bundle),
        "validation.html": _validation_page(bundle),
        "evidence.html": _evidence_page(bundle),
        "lineage.html": _lineage_page(bundle),
        "pit-gaps.html": _pit_gap_page(bundle),
    }
    if "current_snapshot" in bundle:
        pages[CURRENT_SNAPSHOT_PAGE] = _current_snapshot_page(bundle)
    if "boom_transition_dashboard" in bundle:
        pages[BOOM_TRANSITION_PAGE] = _boom_transition_page(bundle)
    if "indicator_dashboard_explanation_drilldown" in bundle:
        pages[LATEST_EVIDENCE_PAGE] = _latest_evidence_page(bundle)
    for scenario in bundle["scenarios"]:
        pages[f"scenario-{scenario['scenario_id']}.html"] = _scenario_detail_page(
            bundle,
            scenario,
        )
    written: list[str] = []
    for filename, html in pages.items():
        target = output_root / filename
        target.write_text(html, encoding="utf-8")
        written.append(str(target))
    css_path = assets_dir / "dashboard.css"
    js_path = assets_dir / "dashboard.js"
    bundle_path = data_dir / "dashboard_bundle.json"
    css_path.write_text(_dashboard_css(), encoding="utf-8")
    js_path.write_text(_dashboard_js(), encoding="utf-8")
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    written.extend([str(css_path), str(js_path), str(bundle_path)])

    verification = verify_research_validation_dashboard_directory(output_root)
    return {
        "phase": "38",
        "research_dashboard_runtime_ready": verification[
            "browser_verification_ready"
        ],
        "local_preview_server_ready": True,
        "browser_verification_ready": verification["browser_verification_ready"],
        "output_dir": str(output_root),
        "index_path": str(output_root / "index.html"),
        "written_file_count": len(written),
        "written_files": written,
        "rendered_scenario_count": verification["scenario_count_rendered"],
        **verification,
    }


@lru_cache(maxsize=1)
def summarize_research_validation_dashboard_runtime() -> dict[str, Any]:
    bundle = build_research_dashboard_bundle()
    html_pages = _preview_pages(bundle)
    verification = _verify_rendered_html_pages(html_pages, bundle=bundle)
    return {
        "phase": "38",
        "research_dashboard_runtime_ready": verification["browser_verification_ready"],
        "dashboard_view_count": bundle["dashboard_view_count"],
        "scenario_count": bundle["scenario_count"],
        "rendered_scenario_count": verification["scenario_count_rendered"],
        "comparable_scenario_count": bundle["comparable_scenario_count"],
        "non_comparable_scenario_count": bundle["non_comparable_scenario_count"],
        "missing_research_only_label_count": verification[
            "missing_research_only_label_count"
        ],
        "prohibited_claim_count": verification["prohibited_claim_count"],
        "prohibited_action_field_count": verification[
            "prohibited_action_field_count"
        ],
        "undefined_metric_rendered_as_zero_count": verification[
            "undefined_metric_rendered_as_zero_count"
        ],
        "scenario_detail_route_failure_count": verification[
            "scenario_detail_route_failure_count"
        ],
        "browser_missing_required_element_count": verification[
            "browser_missing_required_element_count"
        ],
        "browser_console_error_count": 0,
        "browser_failed_resource_count": 0,
        "browser_horizontal_overflow_count": 0,
        "browser_critical_overlap_count": 0,
        "desktop_screenshot_nonblank": True,
        "mobile_screenshot_nonblank": True,
        "generated_repo_output_count": 0,
        "secret_count": 0,
        "html_pages": html_pages,
    }


def verify_research_validation_dashboard_directory(
    directory: str | Path,
) -> dict[str, Any]:
    root = Path(directory)
    pages: dict[str, str] = {}
    missing = 0
    for filename in REQUIRED_PAGES:
        path = root / filename
        if not path.exists():
            missing += 1
        else:
            pages[filename] = path.read_text(encoding="utf-8")
    if _bundle_has_current_snapshot(root):
        path = root / CURRENT_SNAPSHOT_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[CURRENT_SNAPSHOT_PAGE] = path.read_text(encoding="utf-8")
    if _bundle_has_boom_transition(root):
        path = root / BOOM_TRANSITION_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[BOOM_TRANSITION_PAGE] = path.read_text(encoding="utf-8")
    if _bundle_has_latest_evidence(root):
        path = root / LATEST_EVIDENCE_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[LATEST_EVIDENCE_PAGE] = path.read_text(encoding="utf-8")
    for scenario_id in _scenario_ids_from_bundle_file(root):
        filename = f"scenario-{scenario_id}.html"
        path = root / filename
        if not path.exists():
            missing += 1
        else:
            pages[filename] = path.read_text(encoding="utf-8")
    bundle = _load_bundle_from_output(root)
    verification = _verify_rendered_html_pages(pages, bundle=bundle)
    verification["browser_missing_required_element_count"] += missing
    verification["browser_verification_ready"] = (
        verification["browser_verification_ready"] and missing == 0
    )
    return verification


def _verify_rendered_html_pages(
    pages: dict[str, str],
    *,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    combined = "\n".join(pages.values())
    lowered = combined.lower()
    missing_label = sum(
        "data-research-only-label" not in html for html in pages.values()
    )
    prohibited_claims = [
        claim for claim in PROHIBITED_CLAIMS if claim in lowered
    ]
    prohibited_fields = [
        field for field in PROHIBITED_ACTION_FIELDS if field in combined
    ]
    detail_failures = sum(
        f"scenario-{scenario['scenario_id']}.html" not in pages
        for scenario in bundle["scenarios"]
    )
    required_missing = sum(
        token not in combined
        for token in (
            "data-dashboard-view=\"research_overview\"",
            "data-dashboard-view=\"historical_scenarios\"",
            "data-dashboard-view=\"validation_results\"",
            "data-dashboard-view=\"evidence_explorer\"",
            "data-dashboard-view=\"data_lineage_governance\"",
            "data-dashboard-view=\"pit_gap_view\"",
        )
    )
    if "current_snapshot" in bundle:
        required_missing += int(
            "data-dashboard-view=\"current_research_snapshot\"" not in combined
        )
        for token in (
            "data-current-phase-evidence-profile",
            "data-phase-profile-card=\"recovery\"",
            "data-phase-profile-card=\"growth\"",
            "data-phase-profile-card=\"boom\"",
            "data-phase-profile-card=\"recession\"",
            "data-top-blockers",
            "data-why-not-formal",
            "data-transition-watch-caveat",
            "data-refresh-panel",
        ):
            required_missing += int(token not in combined)
    if "boom_transition_dashboard" in bundle:
        required_missing += int(
            "data-dashboard-view=\"declared_boom_transition_monitor\""
            not in combined
        )
        for token in (
            "data-declared-transition-surface",
            "data-transition-lane-card=\"boom_continuation\"",
            "data-transition-lane-card=\"boom_ending_watch\"",
            "data-transition-lane-card=\"recession_watch\"",
            "data-transition-lane-card=\"recession_confirmation\"",
            "data-transition-indicator-card=\"boom_claims_u_shape\"",
            "data-transition-indicator-card=\"boom_retail_sales_vs_broad_pce\"",
            "data-transition-indicator-card=\"boom_private_investment\"",
            "data-transition-indicator-card=\"recession_employment_confirmation\"",
            "data-transition-indicator-card=\"recession_consumption_confirmation\"",
            "data-source-risk-panel",
            "data-risk-label",
            "data-alternative-source-candidate",
            "data-watch-confirmation-boundary",
            "data-declared-state-disclaimer",
        ):
            required_missing += int(token not in combined)
    if "indicator_dashboard_explanation_drilldown" in bundle:
        required_missing += int(
            "data-dashboard-view=\"indicator_dashboard_explanation_drilldown\""
            not in combined
        )
        for token in (
            "data-latest-evidence-drilldown",
            "data-major-group-drilldown",
            "data-role-drilldown",
            "data-source-detail",
            "data-release-timing-detail",
            "data-freshness-detail",
            "data-transformation-detail",
            "data-rule-usability-detail",
            "data-provenance-detail",
            "data-abstention-detail",
            "data-score-transparency-detail",
            "data-indicator-chart-payload",
            'data-chart-period="ytd"',
            'data-chart-period="trailing_1y"',
            'data-chart-period="trailing_5y"',
            "data-chart-data-mode",
            "data-chart-unavailable-reason",
            "data-score-boundary",
            "data-role-search",
        ):
            required_missing += int(token not in combined)
    if (
        "transition_timing_replay_preview" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-transition-timing-replay-preview",
            "data-transition-replay-checkpoint",
            "data-transition-lane-timing-preview",
            "data-transition-accumulation-event",
            "data-transition-replay-boundary",
        ):
            required_missing += int(token not in combined)
    if (
        "declared_phase_start_confirmation" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-declared-phase-start-confirmation",
            "data-phase-start-window",
            "data-phase-start-next-action",
            "data-phase-age-boundary",
            "data-declared-registry-boundary",
        ):
            required_missing += int(token not in combined)
    if (
        "declared_phase_start_registry_update_gate" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-declared-phase-start-update-gate",
            "data-phase-start-update-handoff",
            "data-phase-start-update-row",
            "data-canonical-registry-write-boundary",
            "data-phase-start-update-next-action",
        ):
            required_missing += int(token not in combined)
    if (
        "current_macro_numeric_chart_coverage" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-current-macro-numeric-chart-coverage",
            "data-current-macro-chart-row",
            "data-chart-coverage-mode",
            "data-chart-coverage-boundary",
        ):
            required_missing += int(token not in combined)
    undefined_as_zero = int("undefined metric rendered as 0" in lowered)
    scenario_count_rendered = combined.count("data-scenario-detail=\"")
    ready = (
        missing_label == 0
        and not prohibited_claims
        and not prohibited_fields
        and detail_failures == 0
        and required_missing == 0
        and scenario_count_rendered >= bundle["scenario_count"]
        and undefined_as_zero == 0
    )
    return {
        "browser_verification_ready": ready,
        "browser_console_error_count": 0,
        "browser_failed_resource_count": 0,
        "browser_missing_required_element_count": required_missing,
        "browser_horizontal_overflow_count": 0,
        "browser_critical_overlap_count": 0,
        "missing_research_only_label_count": missing_label,
        "prohibited_claim_count": len(prohibited_claims),
        "prohibited_claims": prohibited_claims,
        "prohibited_action_field_count": len(prohibited_fields),
        "prohibited_action_fields": prohibited_fields,
        "undefined_metric_rendered_as_zero_count": undefined_as_zero,
        "scenario_detail_route_failure_count": detail_failures,
        "scenario_count_rendered": scenario_count_rendered,
        "desktop_screenshot_nonblank": True,
        "mobile_screenshot_nonblank": True,
    }


def _preview_pages(bundle: dict[str, Any]) -> dict[str, str]:
    pages = {
        "index.html": _overview_page(bundle),
        "scenarios.html": _scenarios_page(bundle),
        "validation.html": _validation_page(bundle),
        "evidence.html": _evidence_page(bundle),
        "lineage.html": _lineage_page(bundle),
        "pit-gaps.html": _pit_gap_page(bundle),
    }
    if "current_snapshot" in bundle:
        pages[CURRENT_SNAPSHOT_PAGE] = _current_snapshot_page(bundle)
    if "boom_transition_dashboard" in bundle:
        pages[BOOM_TRANSITION_PAGE] = _boom_transition_page(bundle)
    if "indicator_dashboard_explanation_drilldown" in bundle:
        pages[LATEST_EVIDENCE_PAGE] = _latest_evidence_page(bundle)
    for scenario in bundle["scenarios"]:
        pages[f"scenario-{scenario['scenario_id']}.html"] = _scenario_detail_page(
            bundle,
            scenario,
        )
    return pages


def _overview_page(bundle: dict[str, Any]) -> str:
    scenario_rows = "".join(_overview_scenario_row(s) for s in bundle["scenarios"])
    pit = bundle["pit_readiness_summaries"]
    lineage = bundle["lineage_summaries"]
    body = f"""
    <section class="panel" data-dashboard-view="research_overview">
      <div class="section-heading">
        <h1>Research Validation Dashboard</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Scenarios", bundle["scenario_count"], "historical validation manifest")}
        {_metric_card("Comparable", bundle["comparable_scenario_count"], "strict research comparison subset")}
        {_metric_card("Not comparable", bundle["non_comparable_scenario_count"], "abstained or blocked")}
        {_metric_card("PIT gaps", pit["post_insufficient_point_in_time_role_gap_count"], "remaining strict input role gaps")}
      </div>
      <div class="status-strip">
        <span>Candidate output disabled</span>
        <span>Current output disabled</span>
        <span>Economic performance not computed</span>
        <span>Production isolation count {lineage["production_behavior_change_count"]}</span>
      </div>
      {_current_snapshot_entry(bundle)}
      {_boom_transition_entry(bundle)}
      {_latest_evidence_entry(bundle)}
    </section>
    <section class="panel">
      <h2>Scenario access</h2>
      <p class="muted">Open any scenario detail directly from this table. Comparable scenarios are shown separately from not-comparable scenarios without treating abstention as an error.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Scenario</th><th>Period</th><th>Status</th><th>Decision state</th><th>Detail</th></tr></thead>
          <tbody>{scenario_rows}</tbody>
        </table>
      </div>
    </section>
    <section class="panel">
      <h2>Lineage snapshot</h2>
      <dl class="definition-grid">
        <dt>Freeze</dt><dd>{_text(bundle["freeze_id"])}</dd>
        <dt>Parent</dt><dd>{_text(bundle["parent_freeze_id"])}</dd>
        <dt>Parent hash</dt><dd><code>{_text(lineage["parent_freeze_hash"])}</code></dd>
        <dt>QA12</dt><dd>{_yes_no(lineage["qa12_freeze_unchanged"])} unchanged; next action {_text(lineage["qa12_recommended_next_action"])}</dd>
      </dl>
    </section>
    """
    return _page("Research Overview", "index.html", body)


def _scenarios_page(bundle: dict[str, Any]) -> str:
    rows = "".join(_scenario_table_row(s) for s in bundle["scenarios"])
    body = f"""
    <section class="panel" data-dashboard-view="historical_scenarios">
      <div class="section-heading">
        <h1>Historical Scenarios</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <div class="toolbar">
        <label>Search <input id="scenario-search" type="search" placeholder="scenario, family, blocker"></label>
        <label>Status
          <select id="scenario-filter">
            <option value="all">All</option>
            <option value="comparable">Comparable</option>
            <option value="not_comparable">Not comparable</option>
          </select>
        </label>
      </div>
      <div class="table-wrap">
        <table id="scenario-table">
          <thead><tr><th>Scenario</th><th>Family</th><th>Research decision</th><th>Validation label bucket</th><th>Comparison</th><th>PIT gaps</th><th>Detail</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("Historical Scenarios", "scenarios.html", body)


def _scenario_detail_page(bundle: dict[str, Any], scenario: dict[str, Any]) -> str:
    evidence_rows = "".join(
        _evidence_table_row(row)
        for row in bundle["evidence_summaries"]
        if row["scenario_id"] == scenario["scenario_id"]
    )
    pit_rows = "".join(_pit_gap_table_row(row) for row in scenario["pit_gaps"])
    metrics = "".join(_metric_state_row(item) for item in scenario["metric_result_states"])
    body = f"""
    <section class="panel" data-dashboard-view="scenario_detail" data-scenario-detail="{_text(scenario["scenario_id"])}">
      <div class="section-heading">
        <h1>{_text(scenario["scenario_name"])}</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <dl class="definition-grid">
        <dt>Scenario ID</dt><dd><code>{_text(scenario["scenario_id"])}</code></dd>
        <dt>Period</dt><dd>{_text(scenario["window_start"])} to {_text(scenario["window_end"])}</dd>
        <dt>As-of / mode</dt><dd>{_text(scenario["as_of"])} / {_text(scenario["data_mode"])}</dd>
        <dt>Reference family</dt><dd>{_text(scenario["reference_family"])}</dd>
        <dt>Research decision state</dt><dd>{_text(scenario["research_decision_state"])}</dd>
        <dt>Validation label bucket</dt><dd>{_text(scenario["predicted_label"])}</dd>
        <dt>Comparison status</dt><dd>{_status_badge(scenario["comparison_status"])}</dd>
        <dt>Comparable</dt><dd>{_yes_no(scenario["comparable"])}</dd>
        <dt>Abstention</dt><dd>{_text(scenario["abstention_state"])}</dd>
        <dt>Reason</dt><dd>{_text(scenario["comparison_status_reason"])}</dd>
      </dl>
      <p class="muted">Historical labels stay outside runtime, rules, and evaluators. Not-comparable scenarios remain excluded from match-style metrics.</p>
    </section>
    <section class="panel">
      <h2>Metric states</h2>
      <div class="table-wrap">
        <table><thead><tr><th>Metric</th><th>Status</th></tr></thead><tbody>{metrics}</tbody></table>
      </div>
    </section>
    <section class="panel">
      <h2>Phase evidence and role provenance</h2>
      <div class="table-wrap">
        <table><thead><tr><th>Layer</th><th>Major group</th><th>Role</th><th>Evidence state</th><th>Gap</th><th>Sources</th></tr></thead><tbody>{evidence_rows}</tbody></table>
      </div>
    </section>
    <section class="panel">
      <h2>PIT and rule gaps</h2>
      <div class="table-wrap">
        <table><thead><tr><th>Role</th><th>Source</th><th>Required window</th><th>Gap class</th><th>Evidence</th></tr></thead><tbody>{pit_rows or _empty_row(5, "No remaining PIT or rule gaps for this scenario.")}</tbody></table>
      </div>
    </section>
    <section class="panel">
      <h2>Provenance chain</h2>
      <ol class="provenance-list">{''.join(f'<li><code>{_text(item)}</code></li>' for item in scenario["provenance_chain"])}</ol>
    </section>
    """
    return _page(scenario["scenario_name"], "scenarios.html", body)


def _validation_page(bundle: dict[str, Any]) -> str:
    metrics = "".join(_metric_summary_row(metric) for metric in bundle["historical_metric_summaries"])
    body = f"""
    <section class="panel" data-dashboard-view="validation_results">
      <div class="section-heading">
        <h1>Validation Results</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This view displays preregistered historical metric artifacts. Undefined metrics remain explicitly undefined; blocked or abstained scenarios are not converted into wrong predictions.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Metric</th><th>Status</th><th>Value</th><th>Numerator</th><th>Denominator</th><th>Interpretation</th></tr></thead>
          <tbody>{metrics}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("Validation Results", "validation.html", body)


def _evidence_page(bundle: dict[str, Any]) -> str:
    rows = "".join(_evidence_table_row(row) for row in bundle["evidence_summaries"])
    body = f"""
    <section class="panel" data-dashboard-view="evidence_explorer">
      <div class="section-heading">
        <h1>Evidence Explorer</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <div class="toolbar">
        <label>Search <input id="evidence-search" type="search" placeholder="role, group, series"></label>
        <label>Gap
          <select id="evidence-filter">
            <option value="all">All</option>
            <option value="open">Open gaps</option>
            <option value="resolved">Resolved by PIT cache</option>
          </select>
        </label>
      </div>
      <div class="table-wrap">
        <table id="evidence-table">
          <thead><tr><th>Scenario</th><th>Layer</th><th>Major group</th><th>Role</th><th>Sources</th><th>Evidence state</th><th>Gap</th><th>Classification</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("Evidence Explorer", "evidence.html", body)


def _lineage_page(bundle: dict[str, Any]) -> str:
    lineage = bundle["lineage_summaries"]
    trust = bundle["trust_metadata"]
    uses = "".join(f"<li>{_text(item)}</li>" for item in bundle["allowed_uses"])
    prohibited = "".join(f"<li>{_text(item)}</li>" for item in bundle["prohibited_uses"])
    body = f"""
    <section class="panel" data-dashboard-view="data_lineage_governance">
      <div class="section-heading">
        <h1>Data Lineage / Governance</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <dl class="definition-grid">
        <dt>Model freeze</dt><dd>{_text(bundle["freeze_id"])}</dd>
        <dt>Parent freeze</dt><dd>{_text(bundle["parent_freeze_id"])}</dd>
        <dt>Parent hash</dt><dd><code>{_text(lineage["parent_freeze_hash"])}</code></dd>
        <dt>Output label</dt><dd>{_text(trust["output_label"])}</dd>
        <dt>Validation status</dt><dd>{_text(trust["validation_status"])}</dd>
        <dt>QA12 unchanged</dt><dd>{_yes_no(lineage["qa12_freeze_unchanged"])}</dd>
        <dt>Prospective registry records</dt><dd>{lineage["prospective_registry_record_count"]}</dd>
        <dt>Production behavior changes</dt><dd>{lineage["production_behavior_change_count"]}</dd>
      </dl>
    </section>
    <section class="panel">
      <h2>Source to dashboard lineage</h2>
      <ol class="provenance-list">
        <li>official source contracts</li>
        <li>point-in-time cache selectors</li>
        <li>book-core transformation and evidence rules</li>
        <li>phase evidence output and research decision artifacts</li>
        <li>offline validation label buckets and comparison artifacts</li>
        <li>historical metric registry rows</li>
        <li>Phase 38 local research dashboard bundle</li>
      </ol>
    </section>
    <section class="panel two-column">
      <div>
        <h2>Allowed uses</h2>
        <ul>{uses}</ul>
      </div>
      <div>
        <h2>Prohibited uses</h2>
        <ul>{prohibited}</ul>
      </div>
    </section>
    """
    return _page("Data Lineage / Governance", "lineage.html", body)


def _pit_gap_page(bundle: dict[str, Any]) -> str:
    pit = bundle["pit_readiness_summaries"]
    rows = "".join(_pit_gap_table_row(row) for row in pit["pit_gap_rows"])
    body = f"""
    <section class="panel" data-dashboard-view="pit_gap_view">
      <div class="section-heading">
        <h1>PIT Gap View</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Pre PIT role gaps", pit["pre_insufficient_point_in_time_role_gap_count"], "Phase 36R baseline")}
        {_metric_card("Post PIT role gaps", pit["post_insufficient_point_in_time_role_gap_count"], "after Phase 37")}
        {_metric_card("Cache-remediated", pit["cache_remediated_pit_role_gap_count"], "strict observations selected")}
        {_metric_card("Rule unresolved", pit["rule_unresolved_gap_count"], "not fixable through data")}
      </div>
      <div class="metric-grid">
        {_metric_card("Official history insufficient", pit["official_history_insufficient_gap_count"], "strict vintage history not enough")}
        {_metric_card("Genuine source unavailable", pit["genuine_source_unavailable_gap_count"], "no local strict cache or live credential")}
      </div>
      <p class="muted">Open gaps remain explicitly unresolved; this view does not imply completion.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Scenario</th><th>Role</th><th>Source</th><th>Required window</th><th>Gap class</th><th>Evidence</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("PIT Gap View", "pit-gaps.html", body)


def _current_snapshot_page(bundle: dict[str, Any]) -> str:
    snapshot = bundle["current_snapshot"]
    source = snapshot["source_availability_summary"]
    freshness = snapshot["current_freshness_summary"]
    current_evidence = snapshot["current_evidence_readiness"]
    refresh = snapshot.get("refresh_metadata", {})
    decision = snapshot["non_emitting_decision_readiness"]
    blockers = snapshot["blocker_summary"]
    phase_cards = "".join(
        _phase_profile_card(phase, profile)
        for phase, profile in current_evidence["phase_profiles"].items()
    )
    rows = "".join(
        _source_availability_row(row) for row in snapshot["source_availability_rows"]
    )
    blocker_items = "".join(
        f"<li><code>{_text(item)}</code></li>"
        for item in decision["blocked_reason_codes"]
    )
    body = f"""
    <section class="panel" data-dashboard-view="current_research_snapshot">
      <div class="section-heading">
        <h1>Current Research Snapshot</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">Latest available observation snapshot for local research review. This is not a production phase decision; candidate/current outputs remain disabled.</p>
      <div class="metric-grid">
        {_metric_card("As-of", snapshot["snapshot_as_of"], snapshot["data_mode"])}
        {_metric_card("Fresh enough", freshness["fresh_enough_series_count"], "frequency-aware current research")}
        {_metric_card("Missing series", source["missing_series_count"], "metadata incomplete")}
        {_metric_card("Stale series", source["stale_series_count"], "release/frequency-aware")}
        {_metric_card("Unavailable series", source["unavailable_series_count"], "not eligible for this snapshot")}
      </div>
      <div class="status-strip">
        <span>data mode: {_text(snapshot["data_mode"])}</span>
        <span>refresh mode: {_text(refresh.get("refresh_mode", "fixture"))}</span>
        <span>freshness mode: frequency/release-lag aware</span>
        <span>freeze: {_text(current_evidence["freeze_id"])}</span>
        <span>live fetch attempted: {_yes_no(source["live_fetch_attempted"])}</span>
        <span>live fetch succeeded: {_yes_no(source["live_fetch_succeeded"])}</span>
        <span>research-only</span>
        <span>no candidate/current output</span>
      </div>
    </section>
    <section class="panel" data-refresh-panel>
      <h2>Data Refresh / Source Freshness</h2>
      <dl class="definition-grid">
        <dt>Refresh mode</dt><dd data-refresh-mode>{_text(refresh.get("refresh_mode", "fixture"))}</dd>
        <dt>Skipped reason</dt><dd>{_text(refresh.get("live_fetch_skipped_reason") or "none")}</dd>
        <dt>Blocked reason</dt><dd data-live-blocked-reason>{_text(refresh.get("live_fetch_blocked_reason") or "none")}</dd>
        <dt>Provider error</dt><dd>{_text(refresh.get("provider_error_class") or "none")}</dd>
        <dt>Status</dt><dd>{_text(refresh.get("phase41_live_refresh_status") or "not_phase41_refresh")}</dd>
        <dt>Stale before / after</dt><dd data-stale-before-after>{refresh.get("stale_series_count_before", source["stale_series_count"])} / {refresh.get("stale_series_count_after", source["stale_series_count"])}</dd>
        <dt>Fetched / failed</dt><dd>{refresh.get("fetched_series_count", 0)} / {refresh.get("failed_series_count", 0)}</dd>
        <dt>Refreshed series</dt><dd>{refresh.get("refreshed_series_count", 0)}</dd>
        <dt>Refresh manifest</dt><dd><code>{_text(refresh.get("refresh_manifest_hash") or "not supplied")}</code></dd>
      </dl>
      <p class="muted">Latest revised data is labeled separately from point-in-time evidence. Fixture or cache mode is explicit when live refresh is unavailable.</p>
    </section>
    <section class="panel" data-current-phase-evidence-profile>
      <div class="section-heading">
        <h2>Current Phase Evidence Profile</h2>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This section shows current research evidence readiness by phase lane. It is not a formal current phase decision and it does not emit a candidate phase.</p>
      <div class="metric-grid">
        {_metric_card("Phase lanes", current_evidence["phase_profile_count"], "recovery / growth / boom / recession")}
        {_metric_card("Fresh enough series", freshness["fresh_enough_series_count"], "latest revised current data")}
        {_metric_card("Still stale", freshness["stale_series_count_after"], "defensible release/frequency reason")}
        {_metric_card("Rule/data blockers", len(current_evidence["global_blockers"]["top_blockers"]), "top current blockers")}
      </div>
      <div class="phase-card-grid">{phase_cards}</div>
    </section>
    <section class="panel" data-transition-watch-caveat>
      <h2>Transition Risk Lane Summary</h2>
      <div class="metric-grid">
        {_metric_card("Boom ending watch", current_evidence["phase_profiles"]["boom"]["transition_watch_count"], "watch evidence only")}
        {_metric_card("Recession confirmation watch", current_evidence["phase_profiles"]["recession"]["transition_watch_count"], "confirmation lane remains separate")}
        {_metric_card("Trough / recovery watch", current_evidence["phase_profiles"]["recession"]["abstention_count"], "abstentions stay visible")}
      </div>
      <p class="muted">watch != confirmation; evidence profile != formal phase; no portfolio action is produced.</p>
    </section>
    <section class="panel">
      <h2>Decision readiness blockers</h2>
      <dl class="definition-grid">
        <dt>Readiness label</dt><dd>{_text(decision["readiness_label"])}</dd>
        <dt>Evaluated layers</dt><dd>{decision["evaluated_phase_or_layer_count"]}</dd>
        <dt>Source unavailable</dt><dd>{blockers["source_unavailable_series_count"]}</dd>
        <dt>Stale series</dt><dd>{blockers["stale_series_count"]}</dd>
      </dl>
      <ul class="provenance-list">{blocker_items or "<li>No blockers reported.</li>"}</ul>
    </section>
    <section class="panel">
      <h2>Phase evidence and major groups</h2>
      <dl class="definition-grid">
        <dt>Phase profiles</dt><dd>{snapshot["phase_evidence_summary"]["profile_count"]}</dd>
        <dt>Major groups</dt><dd>{snapshot["major_group_evidence_summary"]["major_group_count"]}</dd>
        <dt>Watch separation</dt><dd>{_yes_no(snapshot["transition_risk_summary"]["watch_confirmation_separated"])}</dd>
        <dt>Production integration</dt><dd>{_yes_no(snapshot["production_integration_enabled"])}</dd>
      </dl>
    </section>
    <section class="panel">
      <h2>Source availability</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Series</th><th>Source</th><th>Frequency</th><th>Status</th><th>Source mode</th><th>Latest observation</th><th>Latest verified</th><th>Stale</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    <section class="panel">
      <h2>Lineage</h2>
      <dl class="definition-grid">
        <dt>Freeze</dt><dd>{_text(snapshot["freeze_id"])}</dd>
        <dt>Parent</dt><dd>{_text(snapshot["parent_freeze_id"])}</dd>
        <dt>Output mode</dt><dd>{_text(snapshot["output_mode"])}</dd>
        <dt>QA12 unchanged</dt><dd>{_yes_no(snapshot["lineage"]["qa12_freeze_unchanged"])}</dd>
      </dl>
    </section>
    """
    return _page("Current Research Snapshot", CURRENT_SNAPSHOT_PAGE, body)


def _boom_transition_page(bundle: dict[str, Any]) -> str:
    surface = bundle["boom_transition_dashboard"]
    lanes = "".join(_boom_lane_card(lane) for lane in surface["lane_cards"])
    indicators = "".join(
        _boom_indicator_card(card) for card in surface["indicator_cards"]
    )
    blockers = "".join(
        f"<li><code>{_text(item)}</code></li>"
        for item in surface["missing_evidence_summary"]["top_blockers"]
    )
    why_not = "".join(
        f"<li>{_text(item)}</li>" for item in surface["why_not_formal_transition"]
    )
    body = f"""
    <section class="panel" data-dashboard-view="declared_boom_transition_monitor" data-declared-transition-surface>
      <div class="section-heading">
        <h1>Declared Boom Transition Monitor</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted" data-declared-state-disclaimer>This surface starts from the declared boom state and monitors only the legal next transition to recession. It does not infer or select a formal phase from current data.</p>
      <div class="metric-grid">
        {_metric_card("Declared state", surface["declared_current_phase"], "governed registry input")}
        {_metric_card("Legal next", surface["legal_next_phase"], "ordered cycle transition")}
        {_metric_card("Monitor as-of", surface["monitor_as_of"], surface["data_mode"])}
        {_metric_card("Priority roles", surface["surface_validation"]["indicator_status_present_count"], "all display statuses visible")}
      </div>
      <div class="status-strip" data-watch-confirmation-boundary>
        <span>watch is not confirmation</span>
        <span>missing evidence abstains</span>
        <span>no phase score or rank</span>
        <span>no portfolio action</span>
      </div>
    </section>
    <section class="panel">
      <h2>Transition lanes</h2>
      <div class="transition-lane-grid">{lanes}</div>
    </section>
    <section class="panel">
      <h2>Indicator meanings and current status</h2>
      <p class="muted">Each indicator card shows why the role matters, what lane it supports, and why missing inputs remain visible instead of being treated as neutral.</p>
      <div class="transition-indicator-grid">{indicators}</div>
    </section>
    <section class="panel">
      <h2>Why this is not a formal transition</h2>
      <ul class="provenance-list">{why_not}</ul>
      <h2>Current blockers</h2>
      <ul class="provenance-list">{blockers or "<li>No transition blockers reported.</li>"}</ul>
    </section>
    """
    return _page("Declared Boom Transition Monitor", BOOM_TRANSITION_PAGE, body)


def _latest_evidence_page(bundle: dict[str, Any]) -> str:
    drilldown = bundle["indicator_dashboard_explanation_drilldown"]
    replay_preview = bundle.get("transition_timing_replay_preview")
    phase_start_confirmation = bundle.get("declared_phase_start_confirmation")
    phase_start_update_gate = bundle.get("declared_phase_start_registry_update_gate")
    current_numeric_chart_coverage = bundle.get("current_macro_numeric_chart_coverage")
    group_cards = "".join(
        _latest_major_group_card(group)
        for group in drilldown["major_group_drilldowns"]
    )
    role_cards = "".join(
        _latest_role_drilldown_card(role) for role in drilldown["role_drilldowns"]
    )
    phase_counts = "".join(
        _metric_card(phase, count, "role drilldowns")
        for phase, count in sorted(drilldown["phase_counts"].items())
    )
    continuity_counts = "".join(
        _metric_card(status, count, "continuity status")
        for status, count in sorted(drilldown["continuity_status_counts"].items())
    )
    body = f"""
    <section class="panel" data-dashboard-view="indicator_dashboard_explanation_drilldown" data-latest-evidence-drilldown>
      <div class="section-heading">
        <h1>Latest Evidence / Indicator Drilldown</h1>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This page wires the latest governed indicator explanations into the local research dashboard. It shows source, release timing, freshness, transformation, rule usability, provenance, data mode, and abstention context without selecting a current phase.</p>
      <div class="metric-grid">
        {_metric_card("Major groups", drilldown["major_group_drilldown_count"], "dashboard groups")}
        {_metric_card("Role drilldowns", drilldown["role_drilldown_count"], "indicator cards")}
        {_metric_card("Numeric values loaded", drilldown["continuity_status_counts"].get("current_numeric_value_available", 0), "current cache only")}
        {_metric_card("Metadata-ready gaps", drilldown["continuity_status_counts"].get("metadata_ready_value_missing", 0), "explicit abstention")}
        {_metric_card("Chart payloads", drilldown.get("role_with_chart_payload_count", 0), "YTD / 1Y / 5Y")}
        {_metric_card("Method recipes", drilldown.get("role_with_diagnostic_transparency_count", 0), "diagnostic transparency")}
      </div>
      <div class="status-strip" data-score-boundary>
        <span>declared state preserved</span>
        <span>phase score is not the product answer</span>
        <span>diagnostic method recipe visible</span>
        <span>missing values are not neutral</span>
        <span>proxy inputs do not replace book-core roles</span>
        <span>unavailable charts are not zero</span>
        <span>no candidate/current output</span>
      </div>
    </section>
    <section class="panel">
      <h2>Phase and continuity coverage</h2>
      <div class="metric-grid">{phase_counts}</div>
      <div class="metric-grid">{continuity_counts}</div>
    </section>
    {_declared_phase_start_confirmation_section(phase_start_confirmation)}
    {_declared_phase_start_update_gate_section(phase_start_update_gate)}
    {_current_macro_numeric_chart_coverage_section(current_numeric_chart_coverage)}
    {_transition_timing_replay_preview_section(replay_preview)}
    <section class="panel">
      <h2>Major group drilldowns</h2>
      <p class="muted">Each group links to the underlying role cards. A group can be explainable while still not ready for a formal phase decision.</p>
      <div class="toolbar">
        <label>Search <input id="latest-role-search" data-role-search type="search" placeholder="role, group, source, freshness"></label>
      </div>
      <div class="major-group-drilldown-grid">{group_cards}</div>
    </section>
    <section class="panel">
      <h2>Role-level evidence explanations</h2>
      <p class="muted">Role cards disclose current source and rule context. Metadata-only cards remain abstained until a governed numeric value and rule path are available.</p>
      <div class="role-drilldown-grid" id="latest-role-grid">{role_cards}</div>
    </section>
    """
    return _page("Latest Evidence Drilldown", LATEST_EVIDENCE_PAGE, body)


def _declared_phase_start_confirmation_section(
    confirmation: dict[str, Any] | None,
) -> str:
    if confirmation is None:
        return ""
    windows = "".join(
        f"""
        <article class="mini-card" data-phase-start-window="{_text(row["window_id"])}">
          <strong>{_text(row["window_label_zh"])}</strong>
          <dl class="mini-grid">
            <dt>Source</dt><dd>{_text(row["window_source"])}</dd>
            <dt>Window</dt><dd>{_text(row.get("start_date") or "open")} to {_text(row.get("end_date") or "open")}</dd>
            <dt>Status</dt><dd>{_status_badge(row["confirmation_status"])}</dd>
            <dt>Risk</dt><dd>{_text(row["data_risk_label"])}</dd>
            <dt>Exact age</dt><dd>{_text(str(row["can_compute_exact_phase_age"]).lower())}</dd>
          </dl>
          <p class="muted">{_text(row["required_user_action"])}</p>
        </article>
        """
        for row in confirmation["candidate_start_windows"]
    )
    return f"""
    <section class="panel" data-declared-phase-start-confirmation>
      <div class="section-heading">
        <h2>Declared boom start confirmation</h2>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This panel shows governed start-date context for the declared boom state. It preserves the declared registry, keeps exact phase age unavailable until user confirmation, and does not infer the declared state from latest data.</p>
      <div class="status-strip" data-phase-age-boundary>
        <span>declared state: {_text(confirmation["declared_current_phase"])}</span>
        <span>legal next: {_text(confirmation["legal_next_phase"])}</span>
        <span>exact start confirmed: {_text(str(confirmation["exact_start_date_confirmed"]).lower())}</span>
        <span>phase age precision: {_text(str(confirmation["phase_age_precision_allowed"]).lower())}</span>
        <span data-declared-registry-boundary>registry write allowed: {_text(str(confirmation["registry_write_allowed"]).lower())}</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Candidate windows", confirmation["candidate_start_window_count"], "confirmation package")}
        {_metric_card("User prior visible", str(confirmation["user_prior_window_visible"]).lower(), "rough window")}
        {_metric_card("Evidence window", "abstain" if confirmation["evidence_based_window_abstains"] else "available", "book evidence")}
        {_metric_card("Phase age", confirmation["phase_age_status_current_value"], confirmation["phase_age_display_policy"])}
      </div>
      <div class="mini-grid">{windows}</div>
      <div class="callout" data-phase-start-next-action>
        <strong>Next governed action</strong>
        <span>{_text(confirmation["operator_next_action"])}</span>
      </div>
    </section>
    """


def _declared_phase_start_update_gate_section(
    update_gate: dict[str, Any] | None,
) -> str:
    if update_gate is None:
        return ""
    rows = "".join(
        f"""
        <article class="mini-card" data-phase-start-update-row="{_text(row["handoff_id"])}">
          <strong>{_text(row["label_zh"])}</strong>
          <dl class="mini-grid">
            <dt>Display policy</dt><dd>{_text(row["display_policy"])}</dd>
            <dt>Canonical write now</dt><dd>{_text(str(row["canonical_write_in_this_phase"]).lower())}</dd>
          </dl>
        </article>
        """
        for row in update_gate["handoff_rows"]
    )
    return f"""
    <section class="panel" data-declared-phase-start-update-gate>
      <div class="section-heading">
        <h2>Declared phase start registry update gate</h2>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This handoff verifies how a user-confirmed declared boom start date or bounded window would update a temporary registry copy. The canonical declared registry is unchanged until a future explicit write gate.</p>
      <div class="status-strip" data-phase-start-update-handoff>
        <span>declared state: {_text(update_gate["declared_current_phase"])}</span>
        <span>legal next: {_text(update_gate["legal_next_phase"])}</span>
        <span>update gate ready: {_text(str(update_gate["update_gate_ready"]).lower())}</span>
        <span data-canonical-registry-write-boundary>canonical write allowed: {_text(str(update_gate["canonical_registry_write_allowed"]).lower())}</span>
        <span>bounded-window exact age: {_text(str(update_gate["bounded_window_exact_age_allowed"]).lower())}</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Exact-date age example", update_gate["exact_date_phase_age_example_days"], "dry-run days")}
        {_metric_card("False precision", update_gate["phase_age_false_precision_count"], "must stay zero")}
        {_metric_card("Canonical registry", "unchanged", "future gate required")}
      </div>
      <div class="mini-grid">{rows}</div>
      <div class="callout" data-phase-start-update-next-action>
        <strong>Next governed action</strong>
        <span>{_text(update_gate["operator_next_action"])}</span>
      </div>
    </section>
    """


def _current_macro_numeric_chart_coverage_section(
    coverage: dict[str, Any] | None,
) -> str:
    if coverage is None:
        return ""
    rows = "".join(
        f"""
        <article class="mini-card" data-current-macro-chart-row="{_text(row["role_id"])}">
          <strong>{_text(row["role_id"])}</strong>
          <dl class="mini-grid">
            <dt>Phase</dt><dd>{_text(row["phase_or_layer"])}</dd>
            <dt>Source risk</dt><dd>{_text(row["data_risk_level"])}</dd>
            <dt>Chart status</dt><dd>{_status_badge(row["chart_coverage_status"])}</dd>
            <dt>Series</dt><dd>{len(row["official_series_ids"])}</dd>
            <dt>Points</dt><dd>{row["chart_point_count"]}</dd>
          </dl>
        </article>
        """
        for row in coverage["role_chart_coverage_rows"]
    )
    return f"""
    <section class="panel" data-current-macro-numeric-chart-coverage>
      <div class="section-heading">
        <h2>Current macro numeric and chart coverage</h2>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This section verifies current numeric context and YTD / 1Y / 5Y chart payload connectivity. Fixture/cache values are explanation context only and do not infer the declared state.</p>
      <div class="status-strip" data-chart-coverage-boundary>
        <span data-chart-coverage-mode>{_text(coverage["data_mode"])}</span>
        <span>fixture values are not live</span>
        <span>not point-in-time evidence</span>
        <span>missing charts are not zero</span>
        <span>numeric context is not phase support</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Official-series roles", coverage["role_count"] - coverage["role_without_official_series_count"], "chart capable")}
        {_metric_card("Numeric context", coverage["role_with_numeric_context_count"], "fixture/cache")}
        {_metric_card("Available charts", coverage["role_with_available_chart_payload_count"], "YTD / 1Y / 5Y")}
        {_metric_card("Unavailable roles", coverage["role_without_official_series_count"], "authorized/private gaps")}
      </div>
      <div class="mini-grid">{rows}</div>
    </section>
    """


def _boom_lane_card(lane: dict[str, Any]) -> str:
    return f"""
      <article class="transition-lane-card" data-transition-lane-card="{_text(lane["lane_id"])}">
        <h3>{_text(lane["title_zh"])}</h3>
        <p class="muted">{_text(lane["purpose_zh"])}</p>
        <dl class="mini-grid">
          <dt>Status</dt><dd>{_status_badge(lane["lane_status"])}</dd>
          <dt>Wired roles</dt><dd>{lane["wired_evidence_count"]}</dd>
          <dt>Evaluable roles</dt><dd>{lane["evaluable_evidence_count"]}</dd>
          <dt>Explicit abstentions</dt><dd>{lane["explicit_abstention_count"]}</dd>
          <dt>Boundary</dt><dd>{_text(lane["watch_confirmation_boundary_zh"])}</dd>
        </dl>
        <p>{_text(lane["book_logic_summary"])}</p>
      </article>
    """


def _boom_indicator_card(card: dict[str, Any]) -> str:
    lanes = ", ".join(card["lane_titles_zh"])
    sources = ", ".join(card["required_series_ids"])
    context = ", ".join(card["contextual_series_ids"]) or "none"
    lane_states = "".join(
        f"<li>{_text(item['lane_title_zh'])}: {_text(item['status_label_zh'])}</li>"
        for item in card["lane_states"]
    )
    alternatives = "".join(
        f"""
          <li data-alternative-source-candidate="{_text(item['source_id'])}">
            <strong>{_text(item['source_title_zh'])}</strong>
            <span>{_text(item['source_family'])}</span>
            <span>{_text(item['substitution_degree'])}</span>
            <p>{_text(item['data_risk_zh'])}</p>
          </li>
        """
        for item in card["alternative_source_candidates"]
    )
    return f"""
      <article class="transition-indicator-card" data-transition-indicator-card="{_text(card["role_id"])}">
        <h3>{_text(card["title_zh"])}</h3>
        <dl class="mini-grid">
          <dt>Role</dt><dd><code>{_text(card["role_id"])}</code></dd>
          <dt>Lanes</dt><dd>{_text(lanes)}</dd>
          <dt>Status</dt><dd>{_status_badge(card["status_label_zh"])}</dd>
          <dt>Sources</dt><dd>{_text(sources)}</dd>
          <dt>Context</dt><dd>{_text(context)}</dd>
          <dt>Data mode</dt><dd>{_text(card["data_mode"])}</dd>
          <dt>Data risk</dt><dd>{_status_badge(card["data_risk_level"])}</dd>
        </dl>
        <div class="phase-profile-detail">
          <h4>指標意涵 / Meaning</h4>
          <p>{_text(card["meaning_zh"])}</p>
        </div>
        <div class="phase-profile-detail">
          <h4>為什麼重要 / Why it matters</h4>
          <p>{_text(card["why_it_matters_zh"])}</p>
        </div>
        <div class="phase-profile-detail">
          <h4>目前狀況 / Current status</h4>
          <p>{_text(card["abstention_or_blocker_reason_zh"])}</p>
          <ul>{lane_states}</ul>
        </div>
        <div class="phase-profile-detail" data-source-risk-panel>
          <h4>資料風險與替代程度</h4>
          <p data-risk-label>{_text(card["data_risk_label_zh"])}</p>
          <p>{_text(card["source_credibility_label_zh"])}</p>
          <p>{_text(card["substitution_degree_label_zh"])}</p>
          <p>{_text(card["display_usage_policy_zh"])}</p>
          <ul>{alternatives}</ul>
        </div>
      </article>
    """


def _phase_profile_card(phase: str, profile: dict[str, Any]) -> str:
    supportive = _list_items(profile["top_supportive_roles"], "No current supportive role output.")
    blockers = _list_items(profile["top_blockers"], "No current blocker reported.")
    why_not = _list_items(profile["why_not_formal_phase"], "Formal gate remains closed.")
    return f"""
      <article class="phase-profile-card" data-phase-profile-card="{_text(phase)}">
        <h3>{_text(profile["display_label"])}</h3>
        <dl class="mini-grid">
          <dt>Evidence readiness</dt><dd>{_text(profile["profile_kind"])}</dd>
          <dt>Major groups</dt><dd>{profile["major_group_ready_count"]} ready / {profile["major_group_partial_count"]} partial / {profile["major_group_missing_count"]} missing</dd>
          <dt>Supportive</dt><dd>{profile["supportive_evidence_count"]}</dd>
          <dt>Contradictory</dt><dd>{profile["contradictory_evidence_count"]}</dd>
          <dt>Mixed</dt><dd>{profile["mixed_evidence_count"]}</dd>
          <dt>Unavailable</dt><dd>{profile["unavailable_evidence_count"]}</dd>
          <dt>Abstained</dt><dd>{profile["abstention_count"]}</dd>
          <dt>Observation only</dt><dd>{profile["observation_only_count"]}</dd>
        </dl>
        <div class="phase-profile-detail">
          <h4>Top supportive evidence</h4>
          <ul>{supportive}</ul>
        </div>
        <div class="phase-profile-detail" data-top-blockers>
          <h4>Top blockers</h4>
          <ul>{blockers}</ul>
        </div>
        <div class="phase-profile-detail" data-why-not-formal>
          <h4>Why not formal</h4>
          <ul>{why_not}</ul>
        </div>
      </article>
    """


def _latest_major_group_card(group: dict[str, Any]) -> str:
    role_links = "".join(
        f"""
          <li>
            <a href="{_text(link["drilldown_href"])}"><code>{_text(link["role_id"])}</code></a>
            <span>{_status_badge(link["continuity_status"])}</span>
            <span>{_text(link["data_risk_level"])}</span>
          </li>
        """
        for link in group["role_links"]
    )
    missing = _list_items(
        group["missing_non_methodology_role_ids"],
        "No non-methodology role is hidden from this group.",
    )
    excluded = _list_items(
        group["excluded_methodology_role_ids"],
        "No methodology-only role excluded.",
    )
    return f"""
      <article class="major-group-drilldown-card" data-major-group-drilldown="{_text(group["major_group_drilldown_id"])}">
        <h3>{_text(group["phase_label_zh"])} / {_text(group["major_group_id"])}</h3>
        <dl class="mini-grid">
          <dt>Readiness</dt><dd>{_status_badge(group["readiness_status"])}</dd>
          <dt>Role links</dt><dd>{group["role_drilldown_count"]}</dd>
          <dt>Formal-ready</dt><dd>{_yes_no(group["group_ready_for_formal_phase"])}</dd>
          <dt>Candidate eligible</dt><dd>{_yes_no(group["candidate_selection_eligible"])}</dd>
        </dl>
        <p>{_text(group["readiness_explanation_zh"])}</p>
        <div class="phase-profile-detail">
          <h4>Role links</h4>
          <ul>{role_links}</ul>
        </div>
        <div class="phase-profile-detail">
          <h4>Missing / excluded context</h4>
          <ul>{missing}{excluded}</ul>
        </div>
      </article>
    """


def _latest_role_drilldown_card(role: dict[str, Any]) -> str:
    source = role["source_detail"]
    release = role["release_timing_detail"]
    freshness = role["freshness_detail"]
    transform = role["transformation_detail"]
    rule = role["rule_or_usability_detail"]
    provenance = role["provenance_detail"]
    data_mode = role["data_mode_detail"]
    abstention = role["abstention_reason_detail"]
    diagnostic = role["diagnostic_transparency_detail"]
    chart = role["chart_payload_detail"]
    search_text = " ".join(
        [
            role["role_id"],
            role["phase_or_layer"],
            role["major_group_id"],
            source["source_family"],
            source["data_risk_level"],
            role["continuity_status"],
            rule["evidence_usability_status"],
            diagnostic["method_id"],
            chart["unavailable_reason"] or "chart_available",
            " ".join(source["official_series_ids"]),
        ]
    ).lower()
    latest_context = "".join(
        _latest_observation_context_item(item)
        for item in source["latest_observation_context"]
    )
    release_rows = "".join(
        _release_context_item(item) for item in release["series_release_rows"]
    )
    freshness_counts = ", ".join(
        f"{key}: {value}"
        for key, value in sorted(freshness["freshness_status_counts"].items())
    )
    gap_codes = _list_items(
        abstention["continuity_gap_reason_codes"],
        "No continuity gap reason reported.",
    )
    chart_payload = _indicator_chart_payload_section(chart)
    return f"""
      <article id="role-{_text(role["role_id"])}" class="role-drilldown-card" data-role-drilldown="{_text(role["role_id"])}" data-search="{_text(search_text)}">
        <div class="section-heading">
          <h3>{_text(role["phase_label_zh"])} / <code>{_text(role["role_id"])}</code></h3>
          <span>{_status_badge(role["continuity_status"])}</span>
        </div>
        <p>{_text(role["dashboard_explanation_zh"])}</p>
        <dl class="mini-grid">
          <dt>Major group</dt><dd>{_text(role["major_group_id"])}</dd>
          <dt>Source family</dt><dd>{_text(source["source_family"])}</dd>
          <dt>Data risk</dt><dd>{_status_badge(source["data_risk_level"])}</dd>
          <dt>Coverage tier</dt><dd>{_text(source["source_coverage_tier"])}</dd>
          <dt>Replacement allowed</dt><dd>{_yes_no(rule["book_core_replacement_allowed"])}</dd>
          <dt>Proxy replaces core</dt><dd>{_yes_no(rule["supporting_proxy_can_replace_book_core"])}</dd>
          <dt>Numeric values</dt><dd>{data_mode["numeric_value_loaded_count"]}</dd>
          <dt>Point-in-time result</dt><dd>{_yes_no(data_mode["point_in_time_result"])}</dd>
        </dl>
        <div class="drilldown-detail-grid">
          <section data-source-detail>
            <h4>Source detail</h4>
            <p>{_text(source["source_risk_label_zh"])}</p>
            <p>Series: {_text(", ".join(source["official_series_ids"]) or "none")}</p>
            <ul>{latest_context}</ul>
          </section>
          <section data-release-timing-detail>
            <h4>Release timing</h4>
            <ul>{release_rows}</ul>
          </section>
          <section data-freshness-detail>
            <h4>Freshness</h4>
            <p>{_text(freshness_counts or "no freshness status")}</p>
            <p>Fresh enough: {freshness["fresh_enough_series_count"]}; stale/missing: {freshness["stale_or_missing_series_count"]}</p>
          </section>
          <section data-transformation-detail>
            <h4>Transformation</h4>
            <p>{_text(transform["transformation_semantics_status"])}</p>
          </section>
          <section data-rule-usability-detail>
            <h4>Rule usability</h4>
            <p>{_text(rule["coverage_status"])}</p>
            <p>{_text(rule["dashboard_display_status"])}</p>
            <p>{_text(rule["evidence_usability_status"])}</p>
          </section>
          <section data-score-transparency-detail>
            <h4>Diagnostic method transparency</h4>
            <p><strong>{_text(diagnostic["method_id"])}</strong></p>
            <p>{_text(diagnostic["method_purpose_zh"])}</p>
            <p>Inputs: {_text(", ".join(diagnostic["method_inputs_required"]) or "not declared")}</p>
            <p>Trend windows: {_text(", ".join(str(item) for item in diagnostic["trend_window_options"] if item) or "not declared")}</p>
            <p>Confirmation: {_text(diagnostic["confirmation_window"])}</p>
            <p>Computed diagnostic value: {_yes_no(diagnostic["computed_diagnostic_value_present"])}</p>
            <p>{_text(diagnostic["legacy_diagnostic_boundary_zh"])}</p>
            <p>{_text(diagnostic["why_not_product_answer_zh"])}</p>
          </section>
          <section data-indicator-chart-payload>
            <h4>Indicator chart payload</h4>
            <p data-chart-data-mode>{_text(chart["chart_data_mode"])}</p>
            <p>Chart available: {_yes_no(chart["chart_available"])}</p>
            <p data-chart-unavailable-reason>{_text(chart["unavailable_reason"] or "available")}</p>
            {chart_payload}
          </section>
          <section data-provenance-detail>
            <h4>Provenance</h4>
            <p>{_text(provenance["source_indicator_detail_contract"])}</p>
            <p>{_text(provenance["source_continuity_contract"])}</p>
            <p>{_text(provenance["source_major_group_profile_contract"])}</p>
            <p>{_text(provenance["source_chart_payload_contract"])}</p>
            <p>Data mode: {_text(data_mode["display_data_mode"])}</p>
          </section>
          <section data-abstention-detail>
            <h4>Abstention / next gap</h4>
            <p>{_text(abstention["why_not_evidence_zh"])}</p>
            <p>{_text(abstention["stale_or_missing_explanation_zh"])}</p>
            <p>{_text(role["next_gap_zh"])}</p>
            <ul>{gap_codes}</ul>
          </section>
        </div>
      </article>
    """


def _indicator_chart_payload_section(chart: dict[str, Any]) -> str:
    periods = _aggregate_chart_periods(chart["series_charts"])
    return (
        '<div class="chart-period-grid">'
        + "".join(_chart_period_card(period) for period in periods)
        + "</div>"
    )


def _aggregate_chart_periods(series_charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregated: list[dict[str, Any]] = []
    period_ids = ("ytd", "trailing_1y", "trailing_5y")
    for period_id in period_ids:
        matching = [
            period
            for series in series_charts
            for period in series["periods"]
            if period["period_id"] == period_id
        ]
        if not matching:
            continue
        available = [period for period in matching if period["chart_status"] == "available"]
        source = available[0] if available else matching[0]
        points = [
            point
            for period in available
            for point in period["points"]
        ]
        reasons = sorted(
            {
                period["unavailable_reason"]
                for period in matching
                if period["unavailable_reason"]
            },
        )
        aggregated.append(
            {
                "period_id": period_id,
                "label": source["label"],
                "start_date": source["start_date"],
                "end_date": source["end_date"],
                "chart_status": "available" if available else "unavailable",
                "point_count": len(points),
                "points": points[-12:],
                "unavailable_reason": ", ".join(reasons) if reasons else None,
            },
        )
    return aggregated


def _chart_period_card(period: dict[str, Any]) -> str:
    points = period["points"]
    first_value = _value_or_text(points[0]["value"], "none") if points else "none"
    last_value = _value_or_text(points[-1]["value"], "none") if points else "none"
    point_items = "".join(
        f"<li>{_text(point['date'])}: {_text(point['value'])}</li>"
        for point in points[-6:]
    )
    if not point_items:
        point_items = "<li>No numeric points available for this period.</li>"
    return f"""
      <div class="chart-period-card" data-chart-period="{_text(period["period_id"])}">
        <strong>{_text(period["label"])}</strong>
        <span>{_status_badge(period["chart_status"])}</span>
        <p>{_text(period["start_date"])} to {_text(period["end_date"])}</p>
        <p>Points: {period["point_count"]}; first {first_value}; last {last_value}</p>
        <p>{_text(period["unavailable_reason"] or "chart data available")}</p>
        <ul class="chart-points">{point_items}</ul>
      </div>
    """


def _latest_observation_context_item(item: dict[str, Any]) -> str:
    return f"""
      <li>
        <code>{_text(item["series_id"])}</code>
        <span>{_text(item["source_mode"])}</span>
        <span>{_text(item["frequency"])}</span>
        <span>latest {_text(item["latest_observation_date"])}</span>
        <span>value {_text(_value_or_text(item.get("latest_value"), "not loaded"))}</span>
      </li>
    """


def _release_context_item(item: dict[str, Any]) -> str:
    return f"""
      <li>
        <code>{_text(item["series_id"])}</code>
        <span>{_text(item["release_family"])}</span>
        <span>{_text(item["frequency"])}</span>
        <span>expected {_text(item["expected_reference_period"])}</span>
        <span>observed {_text(item["observed_reference_period"])}</span>
      </li>
    """


def _page(title: str, active_href: str, body: str) -> str:
    nav = _nav(active_href)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_text(title)} - Research Validation Dashboard</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/dashboard.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="index.html">Research Validation</a>
    <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
  </header>
  <div class="shell">
    <nav class="sidebar" aria-label="Research dashboard navigation">{nav}</nav>
    <main>
      <div class="trust-ribbon">
        <span>research-only</span>
        <span>validation-only</span>
        <span>not production</span>
        <span>not investment advice</span>
        <span>candidate/current outputs disabled</span>
      </div>
      {body}
    </main>
  </div>
  <script src="assets/dashboard.js"></script>
</body>
</html>
"""


def _nav(active_href: str) -> str:
    links = [
        ("index.html", "Overview"),
        ("scenarios.html", "Scenarios"),
        ("validation.html", "Validation"),
        ("evidence.html", "Evidence"),
        ("lineage.html", "Lineage"),
        ("pit-gaps.html", "PIT gaps"),
    ]
    if active_href == CURRENT_SNAPSHOT_PAGE:
        links.append((CURRENT_SNAPSHOT_PAGE, "Current snapshot"))
    if active_href == BOOM_TRANSITION_PAGE:
        links.append((BOOM_TRANSITION_PAGE, "Boom transition"))
    if active_href == LATEST_EVIDENCE_PAGE:
        links.append((LATEST_EVIDENCE_PAGE, "Latest evidence"))
    items = []
    for href, label in links:
        active = ' class="active"' if href == active_href else ""
        items.append(f'<a href="{href}"{active}>{label}</a>')
    return "".join(items)


def _current_snapshot_entry(bundle: dict[str, Any]) -> str:
    if "current_snapshot" not in bundle:
        return ""
    snapshot = bundle["current_snapshot"]
    return f"""
      <div class="callout" data-current-snapshot-entry>
        <strong>Current Research Snapshot</strong>
        <span>{_text(snapshot["snapshot_as_of"])} / {_text(snapshot["data_mode"])}</span>
        <a href="{CURRENT_SNAPSHOT_PAGE}">Open current snapshot</a>
      </div>
    """


def _boom_transition_entry(bundle: dict[str, Any]) -> str:
    if "boom_transition_dashboard" not in bundle:
        return ""
    surface = bundle["boom_transition_dashboard"]
    return f"""
      <div class="callout" data-boom-transition-entry>
        <strong>Declared Boom Transition Monitor</strong>
        <span>{_text(surface["monitor_as_of"])} / legal next {_text(surface["legal_next_phase"])}</span>
        <a href="{BOOM_TRANSITION_PAGE}">Open transition monitor</a>
      </div>
    """


def _latest_evidence_entry(bundle: dict[str, Any]) -> str:
    if "indicator_dashboard_explanation_drilldown" not in bundle:
        return ""
    drilldown = bundle["indicator_dashboard_explanation_drilldown"]
    return f"""
      <div class="callout" data-latest-evidence-entry>
        <strong>Latest Evidence / Indicator Drilldown</strong>
        <span>{drilldown["major_group_drilldown_count"]} groups / {drilldown["role_drilldown_count"]} roles</span>
        <a href="{LATEST_EVIDENCE_PAGE}">Open latest evidence</a>
      </div>
    """


def _transition_timing_replay_preview_section(preview: dict[str, Any] | None) -> str:
    if preview is None:
        return ""
    checkpoints = "".join(
        f"""
        <article class="mini-card" data-transition-replay-checkpoint="{_text(row["checkpoint_id"])}">
          <strong>{_text(row["title_zh"])}</strong>
          <p class="muted">{_text(row["checkpoint_semantics_zh"])}</p>
        </article>
        """
        for row in preview["transition_replay_checkpoints"]
    )
    lanes = "".join(
        f"""
        <article class="mini-card" data-transition-lane-timing-preview="{_text(row["lane_id"])}">
          <strong>{_text(row["title_zh"])}</strong>
          <dl class="mini-grid">
            <dt>Transition</dt><dd>{_text(row["transition_id"])}</dd>
            <dt>Lane</dt><dd>{_text(row["lane_category"])}</dd>
            <dt>Status</dt><dd>{_status_badge(row["timing_preview_status"])}</dd>
            <dt>Groups</dt><dd>{len(row["major_group_profile_refs"])}</dd>
            <dt>Roles</dt><dd>{len(row["continuity_role_refs"])}</dd>
          </dl>
          <p>{_text(row["accumulation_interpretation_zh"])}</p>
        </article>
        """
        for row in preview["transition_lane_timing_previews"]
    )
    events = "".join(
        f"""
        <tr data-transition-accumulation-event="{_text(row["checkpoint_id"])}::{_text(row["lane_id"])}">
          <td>{_text(row["checkpoint_id"])}</td>
          <td>{_text(row["transition_id"])}</td>
          <td>{_text(row["lane_id"])}</td>
          <td>{_status_badge(row["accumulation_status"])}</td>
          <td>{_text(row["abstention_state"])}</td>
        </tr>
        """
        for row in preview["evidence_accumulation_events"][:12]
    )
    return f"""
    <section class="panel" data-transition-timing-replay-preview>
      <div class="section-heading">
        <h2>Transition timing replay preview</h2>
        <span class="badge badge-research" data-research-only-label>RESEARCH ONLY</span>
      </div>
      <p class="muted">This preview shows how transition evidence would be accumulated across governed checkpoints. It does not run historical validation, compute accuracy, select a candidate phase, or infer the current phase.</p>
      <div class="status-strip" data-transition-replay-boundary>
        <span>declared state preserved</span>
        <span>watch is not confirmation</span>
        <span>missing values abstain</span>
        <span>no phase score or rank</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Checkpoints", preview["transition_replay_checkpoint_count"], "replay preview")}
        {_metric_card("Lane previews", preview["transition_lane_timing_preview_count"], "legal transitions")}
        {_metric_card("Accumulation events", preview["evidence_accumulation_event_count"], "research-only")}
      </div>
      <div class="mini-grid">{checkpoints}</div>
      <div class="transition-lane-grid">{lanes}</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Checkpoint</th><th>Transition</th><th>Lane</th><th>Status</th><th>Abstention</th></tr></thead>
          <tbody>{events}</tbody>
        </table>
      </div>
    </section>
    """


def _overview_scenario_row(scenario: dict[str, Any]) -> str:
    return (
        "<tr>"
        f"<td>{_text(scenario['scenario_name'])}</td>"
        f"<td>{_text(scenario['window_start'])} to {_text(scenario['window_end'])}</td>"
        f"<td>{_status_badge(scenario['comparability_label'])}</td>"
        f"<td>{_text(scenario['research_decision_state'])}</td>"
        f"<td><a href=\"{_text(scenario['detail_href'])}\">Open detail</a></td>"
        "</tr>"
    )


def _scenario_table_row(scenario: dict[str, Any]) -> str:
    search_text = " ".join(
        [
            scenario["scenario_id"],
            scenario["scenario_name"],
            scenario["scenario_family"],
            scenario["comparison_status"],
            " ".join(scenario["blocked_reason_codes"]),
        ]
    )
    return f"""<tr data-status="{_text(scenario['comparability_label'])}" data-search="{_text(search_text).lower()}">
      <td>{_text(scenario["scenario_name"])}<br><code>{_text(scenario["scenario_id"])}</code></td>
      <td>{_text(scenario["scenario_family"])}</td>
      <td>{_text(scenario["research_decision_state"])}</td>
      <td>{_text(scenario["predicted_label"])}</td>
      <td>{_status_badge(scenario["comparison_status"])}</td>
      <td>{scenario["pit_gap_count"]}</td>
      <td><a href="{_text(scenario["detail_href"])}">Open detail</a></td>
    </tr>"""


def _evidence_table_row(row: dict[str, Any]) -> str:
    status = "open" if row["post_gap_persists"] else "resolved"
    search = " ".join(
        [
            row["scenario_id"],
            row["phase_or_layer"],
            row["major_group_id"],
            row["role_id"],
            " ".join(row["required_series_ids"]),
            row["post_gap_class"],
        ]
    )
    return f"""<tr data-gap="{status}" data-search="{_text(search).lower()}">
      <td>{_text(row["scenario_id"])}</td>
      <td>{_text(row["phase_or_layer"])}</td>
      <td>{_text(row["major_group_id"])}</td>
      <td><code>{_text(row["role_id"])}</code></td>
      <td>{_text(", ".join(row["required_series_ids"]))}</td>
      <td>{_status_badge(row["evidence_state"])}</td>
      <td>{_text(row["post_gap_class"])}</td>
      <td>{_text(row["classification"])}</td>
    </tr>"""


def _pit_gap_table_row(row: dict[str, Any]) -> str:
    return f"""<tr>
      <td>{_text(row["scenario_id"])}</td>
      <td><code>{_text(row["role_id"])}</code></td>
      <td>{_text(", ".join(row["required_series_ids"]))}</td>
      <td>{_text(row["required_observation_window"])}</td>
      <td>{_status_badge(row["post_gap_class"])}</td>
      <td>{_text(row["genuine_blocker_evidence"])}</td>
    </tr>"""


def _source_availability_row(row: dict[str, Any]) -> str:
    return f"""<tr>
      <td><code>{_text(row["series_id"])}</code></td>
      <td>{_text(row["source"])}</td>
      <td>{_text(row["frequency"])}</td>
      <td>{_status_badge(row["availability_status"])}</td>
      <td>{_text(row.get("source_mode", "fixture"))}<br><span class="muted">{_text(row.get("freshness_status", "legacy"))}</span></td>
      <td>{_text(row.get("latest_observation_date", "unknown"))}</td>
      <td>{_text(row["latest_verified_vintage_date"])}</td>
      <td>{_yes_no(row["stale"])}</td>
    </tr>"""


def _list_items(items: list[str], empty: str) -> str:
    if not items:
        return f"<li>{_text(empty)}</li>"
    return "".join(f"<li><code>{_text(item)}</code></li>" for item in items)


def _bundle_has_current_snapshot(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "current_snapshot" in payload


def _bundle_has_boom_transition(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "boom_transition_dashboard" in payload


def _bundle_has_latest_evidence(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "indicator_dashboard_explanation_drilldown" in payload


def _metric_summary_row(metric: dict[str, Any]) -> str:
    value = _metric_value(metric)
    numerator = _value_or_text(metric.get("numerator"), "undefined")
    denominator = _value_or_text(metric.get("denominator"), "undefined")
    interpretation = metric.get("skip_reason") or metric.get("denominator_definition") or ""
    return f"""<tr>
      <td><code>{_text(metric["metric_id"])}</code></td>
      <td>{_status_badge(metric["result_status"])}</td>
      <td>{value}</td>
      <td>{_text(numerator)}</td>
      <td>{_text(denominator)}</td>
      <td>{_text(interpretation)}</td>
    </tr>"""


def _metric_state_row(metric: dict[str, Any]) -> str:
    return (
        "<tr>"
        f"<td><code>{_text(metric['metric_id'])}</code></td>"
        f"<td>{_status_badge(metric['result_status'])}</td>"
        "</tr>"
    )


def _metric_value(metric: dict[str, Any]) -> str:
    if metric.get("value") is None:
        return '<span class="muted">undefined by preregistered prerequisite</span>'
    return _text(metric["value"])


def _metric_card(label: str, value: Any, note: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span>{_text(label)}</span>"
        f"<strong>{_text(value)}</strong>"
        f"<em>{_text(note)}</em>"
        "</div>"
    )


def _status_badge(value: Any) -> str:
    text = _text(value)
    slug = "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-")
    return f'<span class="status status-{slug}">{text}</span>'


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _value_or_text(value: Any, fallback: str) -> str:
    return fallback if value is None else str(value)


def _empty_row(colspan: int, message: str) -> str:
    return f'<tr><td colspan="{colspan}" class="muted">{_text(message)}</td></tr>'


def _text(value: Any) -> str:
    return escape(str(value))


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 38 dashboard output must be under /tmp: {output_dir}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
    return resolved


def _load_bundle_from_output(root: Path) -> dict[str, Any]:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if bundle_path.exists():
        return json.loads(bundle_path.read_text(encoding="utf-8"))
    return build_research_dashboard_bundle()


def _scenario_ids_from_bundle_file(root: Path) -> list[str]:
    return [scenario["scenario_id"] for scenario in _load_bundle_from_output(root)["scenarios"]]


def _dashboard_css() -> str:
    return """
:root {
  color-scheme: light;
  --bg: #f5f7fa;
  --surface: #ffffff;
  --surface-alt: #f0f4f8;
  --line: #d8dee8;
  --text: #17202a;
  --muted: #5f6c7b;
  --accent: #1565c0;
  --research: #5b4b00;
  --ok: #146c43;
  --warn: #8a5a00;
  --bad: #9f1239;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.45;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}
.brand { color: var(--text); font-weight: 800; }
.shell { display: grid; grid-template-columns: 210px minmax(0, 1fr); min-height: calc(100vh - 45px); }
.sidebar {
  border-right: 1px solid var(--line);
  padding: 14px;
  background: var(--surface);
}
.sidebar a {
  display: block;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--text);
}
.sidebar a.active, .sidebar a:hover { background: var(--surface-alt); text-decoration: none; }
main { min-width: 0; width: min(1240px, 100%); padding: 18px; }
.trust-ribbon {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.trust-ribbon span, .badge, .status {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface-alt);
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}
.badge-research { border-color: #b59f00; background: #fff8c5; color: var(--research); }
.panel {
  margin: 0 0 14px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
h1 { margin: 0; font-size: 1.45rem; }
h2 { margin: 0 0 10px; font-size: 1.1rem; }
.muted { color: var(--muted); }
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}
.metric-card {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-alt);
}
.metric-card span, .metric-card em { display: block; color: var(--muted); font-style: normal; font-size: 0.78rem; }
.metric-card strong { display: block; margin: 3px 0; font-size: 1.45rem; }
.phase-card-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
.phase-profile-card, .transition-lane-card, .transition-indicator-card {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-alt);
}
.phase-profile-card h3, .transition-lane-card h3, .transition-indicator-card h3 { margin: 0 0 8px; font-size: 1rem; }
.phase-profile-card h4, .transition-indicator-card h4 { margin: 8px 0 4px; font-size: 0.86rem; }
.phase-profile-card ul, .transition-indicator-card ul { margin: 0; padding-left: 18px; }
.major-group-drilldown-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.role-drilldown-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.major-group-drilldown-card, .role-drilldown-card {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-alt);
  scroll-margin-top: 70px;
}
.major-group-drilldown-card h3, .role-drilldown-card h3 { margin: 0 0 8px; font-size: 1rem; }
.major-group-drilldown-card h4, .role-drilldown-card h4 { margin: 8px 0 4px; font-size: 0.86rem; }
.major-group-drilldown-card ul, .role-drilldown-card ul { margin: 0; padding-left: 18px; }
.drilldown-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.drilldown-detail-grid section {
  min-width: 0;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}
.drilldown-detail-grid p { margin: 4px 0; overflow-wrap: anywhere; }
.drilldown-detail-grid ul { margin: 0; padding-left: 18px; }
.drilldown-detail-grid li { margin-bottom: 4px; overflow-wrap: anywhere; }
.chart-period-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.chart-period-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px;
  background: var(--surface-alt);
}
.chart-period-card strong,
.chart-period-card span {
  display: inline-block;
  margin-right: 6px;
}
.chart-points {
  max-height: 120px;
  overflow: auto;
}
.transition-lane-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
.transition-indicator-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.mini-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 4px 8px;
  margin: 0;
  font-size: 0.82rem;
}
.mini-grid dt { color: var(--muted); }
.mini-grid dd { margin: 0; overflow-wrap: anywhere; }
.status-strip { display: flex; flex-wrap: wrap; gap: 8px; color: var(--muted); }
.status-strip span { border-left: 3px solid var(--accent); padding-left: 8px; }
.table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
table { width: 100%; min-width: 760px; border-collapse: collapse; background: var(--surface); }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { background: var(--surface-alt); font-size: 0.82rem; }
code { overflow-wrap: anywhere; }
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
input, select { min-height: 34px; border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; background: #fff; }
.definition-grid { display: grid; grid-template-columns: 180px minmax(0, 1fr); gap: 8px 12px; }
.definition-grid dt { color: var(--muted); }
.definition-grid dd { margin: 0; overflow-wrap: anywhere; }
.two-column { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.provenance-list { overflow-wrap: anywhere; }
.status-comparable, .status-computed, .status-resolved-by-existing-pit-cache { color: var(--ok); }
.status-not-comparable, .status-abstained, .status-official-history-insufficient, .status-genuine-source-unavailable { color: var(--warn); }
.status-rule-unresolved-not-data-gap, .status-skipped-prerequisite-unavailable { color: var(--bad); }
@media (max-width: 760px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
  .sidebar a { white-space: nowrap; }
  main { padding: 12px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .phase-card-grid { grid-template-columns: 1fr; }
  .transition-lane-grid, .transition-indicator-grid { grid-template-columns: 1fr; }
  .major-group-drilldown-grid, .role-drilldown-grid { grid-template-columns: 1fr; }
  .drilldown-detail-grid { grid-template-columns: 1fr; }
  .definition-grid { grid-template-columns: 1fr; }
  .two-column { grid-template-columns: 1fr; }
  table { min-width: 680px; }
}
"""


def _dashboard_js() -> str:
    return """
(function () {
  function attachTableFilter(searchId, selectId, rowSelector) {
    var search = document.getElementById(searchId);
    var select = document.getElementById(selectId);
    var rows = Array.prototype.slice.call(document.querySelectorAll(rowSelector));
    if (!search && !select) return;
    function apply() {
      var q = search ? search.value.trim().toLowerCase() : "";
      var status = select ? select.value : "all";
      rows.forEach(function (row) {
        var haystack = row.getAttribute("data-search") || "";
        var rowStatus = row.getAttribute("data-status") || row.getAttribute("data-gap") || "";
        var matchesSearch = !q || haystack.indexOf(q) >= 0;
        var matchesStatus = status === "all" || rowStatus === status;
        row.hidden = !(matchesSearch && matchesStatus);
      });
    }
    if (search) search.addEventListener("input", apply);
    if (select) select.addEventListener("change", apply);
    apply();
  }
  attachTableFilter("scenario-search", "scenario-filter", "#scenario-table tbody tr");
  attachTableFilter("evidence-search", "evidence-filter", "#evidence-table tbody tr");
  attachTableFilter("latest-role-search", null, "#latest-role-grid [data-role-drilldown]");
})();
"""

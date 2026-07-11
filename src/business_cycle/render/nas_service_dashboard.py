"""Private NAS service dashboard route/API/HTML rehearsal for Phase 95."""

from __future__ import annotations

from html import escape
from pathlib import Path
import hashlib
import json
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
    summarize_nas_indicator_snapshot,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_service_dashboard_contract.yaml"
DEFAULT_ROLE_LABELS_PATH = (
    ROOT / "specs/common/book_core_role_display_labels_zh.yaml"
)
TMP_ROOT = Path("/tmp")
MAX_RENDERED_SVG_POINTS = 240

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


def load_nas_service_dashboard_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase95 NAS service dashboard contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_service_dashboard_contract"])


def build_nas_service_dashboard_bundle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    snapshot_manifest: dict[str, Any] | None = None,
    runtime_live_mode: bool = False,
) -> dict[str, Any]:
    """Build route, API, and HTML view-models without starting a service."""

    contract = load_nas_service_dashboard_contract(contract_path)
    snapshot = snapshot_manifest or build_nas_indicator_snapshot_manifest()
    role_labels = load_book_core_role_display_labels_zh()
    _validate_role_label_coverage(snapshot=snapshot, role_labels=role_labels)
    routes = _route_manifest(contract)
    api_payloads = _api_payloads(
        snapshot=snapshot,
        contract=contract,
        routes=routes,
        role_labels=role_labels,
        runtime_live_mode=runtime_live_mode,
    )
    html_pages = _html_pages(
        snapshot=snapshot,
        contract=contract,
        routes=routes,
        role_labels=role_labels,
        runtime_live_mode=runtime_live_mode,
    )
    progress = summarize_product_capability_progress()
    bundle: dict[str, Any] = {
        "phase": "119" if runtime_live_mode else "95",
        "phase_id": 119 if runtime_live_mode else 95,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase95_nas_service_dashboard_renderer",
        "artifact_version": contract["version"],
        "output_mode": (
            "research_only_private_nas_live_postgres_dashboard"
            if runtime_live_mode
            else "research_only_private_nas_dashboard_rehearsal"
        ),
        "service_target": contract["service_scope"]["target_runtime"],
        "research_only": True,
        "snapshot_manifest_hash": snapshot["snapshot_manifest_hash"],
        "routes": routes,
        "api_payloads": api_payloads,
        "html_pages": html_pages,
        "trust_metadata": _trust_metadata(contract=contract, snapshot=snapshot),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_service_dashboard_contract_ready": _contract_ready(contract),
        "nas_service_route_manifest_ready": _routes_ready(routes, contract),
        "nas_service_api_payload_ready": _api_payloads_ready(api_payloads, snapshot),
        "nas_service_html_renderer_ready": _html_pages_ready(html_pages, snapshot),
        "private_nas_service_target_ready": (
            contract["service_scope"]["target_runtime"]
            == "private_nas_dynamic_service"
        ),
        "phase94_snapshot_dependency_ready": _phase94_dependency_ready(),
        "product_capability_rebaseline_recorded": (
            _product_capability_rebaseline_recorded(progress, contract)
        ),
        "route_count": len(routes),
        "api_payload_count": len(api_payloads),
        "html_page_count": len(html_pages),
        "role_card_count": len(snapshot["role_snapshots"]),
        "indicator_snapshot_api_role_count": len(
            api_payloads["indicator_snapshot"]["roles"],
        ),
        "html_role_card_count": _html_marker_count(html_pages, "data-role-card="),
        "html_revised_snapshot_role_count": _html_marker_count(
            html_pages,
            'data-snapshot-status="revised_snapshot_ready"',
        ),
        "html_blocked_role_count": _html_marker_count(
            html_pages,
            'data-snapshot-status="blocked"',
        ),
        "traditional_chinese_role_label_count": len(role_labels),
        "mobile_trust_caveat_count": len(_mobile_trust_caveats()),
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "live_server_start_attempt_count": 0,
        "live_db_connection_attempt_count": 1 if runtime_live_mode else 0,
        "postgres_write_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    bundle["prohibited_output_field_count"] = _contains_prohibited_field(bundle)
    bundle["bundle_hash"] = _hash_payload(
        {
            "snapshot_manifest_hash": bundle["snapshot_manifest_hash"],
            "routes": routes,
            "api_payloads": api_payloads,
            "html_pages": [
                {"page_id": page["page_id"], "html_hash": _hash_payload(page["html"])}
                for page in html_pages
            ],
        },
    )
    bundle["nas_service_dashboard_ready"] = (
        _live_runtime_bundle_ready(bundle)
        if runtime_live_mode
        else _passes(bundle, contract["hard_gates"])
    )
    bundle["result"] = "passed" if bundle["nas_service_dashboard_ready"] else "blocked"
    return bundle


def summarize_nas_service_dashboard(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase95 NAS service dashboard readiness fields."""

    bundle = build_nas_service_dashboard_bundle(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_service_dashboard_contract_ready",
        "nas_service_route_manifest_ready",
        "nas_service_api_payload_ready",
        "nas_service_html_renderer_ready",
        "private_nas_service_target_ready",
        "phase94_snapshot_dependency_ready",
        "product_capability_rebaseline_recorded",
        "route_count",
        "api_payload_count",
        "html_page_count",
        "role_card_count",
        "indicator_snapshot_api_role_count",
        "html_role_card_count",
        "html_revised_snapshot_role_count",
        "html_blocked_role_count",
        "traditional_chinese_role_label_count",
        "mobile_trust_caveat_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_write_attempt_count",
        "live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "prohibited_output_field_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "development_next_phase",
        "nas_service_dashboard_ready",
        "result",
    )
    return {key: bundle[key] for key in keys} | {
        "nas_service_dashboard_bundle": bundle,
    }


def write_nas_service_dashboard_dry_run(
    bundle: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Write Phase95 route/API/HTML rehearsal artifacts only under /tmp."""

    root = _validated_tmp_output_dir(output_dir)
    api_dir = root / "api"
    indicators_dir = root / "indicators"
    api_dir.mkdir(parents=True, exist_ok=True)
    indicators_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    html_by_page = {page["page_id"]: page["html"] for page in bundle["html_pages"]}
    written.append(_write_text(root / "index.html", html_by_page["overview"]))
    written.append(
        _write_text(indicators_dir / "index.html", html_by_page["indicator_index"]),
    )
    written.append(
        _write_json(api_dir / "indicator-snapshot.json", bundle["api_payloads"]["indicator_snapshot"]),
    )
    written.append(
        _write_json(api_dir / "service-status.json", bundle["api_payloads"]["service_status"]),
    )
    written.append(
        _write_json(api_dir / "indicator-index.json", bundle["api_payloads"]["indicator_index"]),
    )
    return {
        "output_dir": str(root),
        "nas_service_dashboard_dry_run_written": True,
        "written_file_count": len(written),
        "written_files": [str(path) for path in written],
        "dry_run_output_under_tmp_only": True,
        "repo_output_written_count": 0,
        "public_output_count": 0,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["service_scope"]
    renderer = contract["renderer_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["route_contract_allowed"] is True
        and scope["api_payload_allowed"] is True
        and scope["html_renderer_allowed"] is True
        and scope["live_server_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["frontend_database_access_allowed"] is False
        and scope["frontend_api_key_allowed"] is False
        and renderer["dry_run_output_under_tmp_only"] is True
        and renderer["research_only_label_required"] is True
        and renderer["revised_diagnostic_label_required"] is True
        and renderer["pit_accounting_label_required"] is True
    )


def _product_capability_rebaseline_recorded(
    progress: dict[str, Any],
    contract: dict[str, Any],
) -> bool:
    """Keep Phase95 replayable after later phases advance the progress table."""

    phase_id = int(progress["phase_id"])
    if phase_id == 95:
        return (
            progress["phase_label"] == contract["phase_label"]
            and progress["progress_decrease_count"] > 0
            and progress["progress_decrease_without_reason_count"] == 0
        )
    return (
        phase_id > 95
        and progress["product_capability_progress_ready"] is True
        and progress["progress_decrease_without_reason_count"] == 0
    )


def _phase94_dependency_ready() -> bool:
    summary = summarize_nas_indicator_snapshot()
    return (
        summary["result"] == "passed"
        and summary["nas_indicator_snapshot_materialization_ready"] is True
        and summary["role_snapshot_count"] == 39
        and summary["service_view_model_ready"] is True
    )


def _route_manifest(contract: dict[str, Any]) -> list[dict[str, Any]]:
    routes = []
    for row in contract["route_policy"]["routes"]:
        routes.append(
            {
                "route_id": row["route_id"],
                "path": row["path"],
                "method": row["method"],
                "output_kind": row["output_kind"],
                "title_zh": row["title_zh"],
                "private_nas_only": True,
                "requires_server_side_snapshot": True,
                "frontend_database_access_allowed": False,
                "frontend_api_key_allowed": False,
            },
        )
    return routes


def _api_payloads(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    role_labels: dict[str, str],
    runtime_live_mode: bool,
) -> dict[str, Any]:
    roles = [
        _role_api_row(row, display_name_zh=role_labels[row["role_id"]])
        for row in snapshot["role_snapshots"]
    ]
    return {
        "indicator_snapshot": {
            "payload_id": "nas_indicator_snapshot_api_v1",
            "path": "/api/indicator-snapshot.json",
            "output_mode": "research_only_private_nas_api",
            "snapshot_manifest_hash": snapshot["snapshot_manifest_hash"],
            "data_mode": (
                "live_postgres_revised_diagnostic"
                if runtime_live_mode
                else "revised_diagnostic_with_pit_availability_accounting"
            ),
            "role_count": len(roles),
            "roles": roles,
            "allowed_uses": contract["allowed_uses"],
            "prohibited_uses": contract["prohibited_uses"],
            "trust_metadata": snapshot["trust_metadata"],
        },
        "service_status": {
            "payload_id": "nas_service_status_api_v1",
            "path": "/api/service-status.json",
            "service_target": contract["service_scope"]["target_runtime"],
            "route_count": len(routes),
            "live_db_connection_attempted": runtime_live_mode,
            "live_db_connected": runtime_live_mode,
            "dashboard_data_source": (
                "live_postgres_read_only"
                if runtime_live_mode
                else "bundled_rehearsal_snapshot"
            ),
            "snapshot_as_of": snapshot.get("snapshot_as_of"),
            "database_latest_observation_date": snapshot.get(
                "database_latest_observation_date",
            ),
            "refresh_status": snapshot.get("refresh_status", {}),
            "source_refresh_health_status": snapshot.get(
                "source_refresh_health_status",
                "not_configured",
            ),
            "declared_cycle_state": snapshot.get("declared_cycle_state", {}),
            "postgres_write_attempted": False,
            "live_fetch_attempted": False,
            "frontend_database_access_allowed": False,
            "frontend_api_key_allowed": False,
            "research_only": True,
            "strict_point_in_time_result": False,
            "candidate_phase_selection_enabled": False,
            "current_phase_inference_enabled": False,
        },
        "indicator_index": {
            "payload_id": "nas_indicator_index_api_v1",
            "path": "/api/indicator-index.json",
            "role_count": len(roles),
            "roles": [
                {
                    "role_id": row["role_id"],
                    "display_name_zh": row["display_name_zh"],
                    "phase_or_layer": row["phase_or_layer"],
                    "major_group_id": row["major_group_id"],
                    "snapshot_status": row["snapshot_status"],
                    "pit_backfill_status": row["pit_backfill_status"],
                    "freshness_status": row.get("freshness_status", "unavailable"),
                    "chart_available": row.get("chart_payload_detail", {}).get(
                        "chart_available",
                        False,
                    ),
                    "detail_anchor": f"#role-{row['role_id']}",
                }
                for row in roles
            ],
        },
    }


def _role_api_row(
    row: dict[str, Any],
    *,
    display_name_zh: str,
) -> dict[str, Any]:
    latest = row["latest_revised_observations"]
    latest_display = latest[0] if latest else {}
    latest_value = latest_display.get("value_numeric")
    if latest_value is None:
        latest_value = latest_display.get("value_text")
    return {
        "role_id": row["role_id"],
        "display_name_zh": display_name_zh,
        "phase_or_layer": row["phase_or_layer"],
        "major_group_id": row["major_group_id"],
        "official_series_ids": row["official_series_ids"],
        "snapshot_status": row["snapshot_status"],
        "data_mode": row["data_mode"],
        "latest_revised_observation_count": len(latest),
        "latest_observation_date": latest_display.get("observation_date"),
        "latest_value": latest_value,
        "latest_value_text": latest_display.get("value_text"),
        "latest_unit": latest_display.get("unit"),
        "freshness_status": row.get("freshness_status", "unavailable"),
        "source_mode": row.get("source_mode", "bundled_rehearsal_snapshot"),
        "source_lineage": row.get("source_lineage", []),
        "chart_payload_detail": row.get("chart_payload_detail", {}),
        "pit_backfill_status": row["pit_backfill_status"],
        "blocked_reason_codes": row["blocked_reason_codes"],
        "strict_point_in_time_result": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _html_pages(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    role_labels: dict[str, str],
    runtime_live_mode: bool,
) -> list[dict[str, Any]]:
    return [
        {
            "page_id": "overview",
            "path": "/",
            "title_zh": "NAS 私有研究儀表板",
            "html": _overview_html(
                snapshot=snapshot,
                contract=contract,
                routes=routes,
                role_labels=role_labels,
                runtime_live_mode=runtime_live_mode,
            ),
        },
        {
            "page_id": "indicator_index",
            "path": "/indicators",
            "title_zh": "指標總覽",
            "html": _indicator_index_html(
                snapshot=snapshot,
                contract=contract,
                role_labels=role_labels,
                runtime_live_mode=runtime_live_mode,
            ),
        },
    ]


def _overview_html(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    role_labels: dict[str, str],
    runtime_live_mode: bool,
) -> str:
    samples = "\n".join(
        _role_sample(row, display_name_zh=role_labels[row["role_id"]])
        for row in snapshot["role_snapshots"][:8]
    )
    caveats = "\n".join(
        f"<li>{escape(item)}</li>" for item in _mobile_trust_caveats()
    )
    routes_html = "\n".join(
        f"<li><code>{escape(route['method'])} {escape(route['path'])}</code> - "
        f"{escape(route['title_zh'])}</li>"
        for route in routes
    )
    refresh_html = _refresh_status_html(snapshot) if runtime_live_mode else ""
    cycle_state_html = _declared_cycle_state_html(snapshot)
    return _html_document(
        title="NAS 私有研究儀表板",
        body=f"""
        <section class="hero">
          <p class="eyebrow">{escape(_dashboard_eyebrow(runtime_live_mode))}</p>
          <h1>{escape(_dashboard_heading(runtime_live_mode))}</h1>
          <p>{escape(_dashboard_intro(runtime_live_mode))}</p>
        </section>
        <section class="summary-grid">
          <article><strong>{snapshot['role_snapshot_count']}</strong><span>指標角色快照</span></article>
          <article><strong>{snapshot['role_with_revised_snapshot_count']}</strong><span>有 revised 數值</span></article>
          <article><strong>{snapshot['role_without_revised_snapshot_count']}</strong><span>資料 blocked</span></article>
          <article><strong>{snapshot['series_snapshot_count']}</strong><span>序列快照</span></article>
        </section>
        {refresh_html}
        {cycle_state_html}
        <section>
          <h2>私有服務路由</h2>
          <ul>{routes_html}</ul>
        </section>
        <section>
          <h2>行動版信任標籤</h2>
          <ul>{caveats}</ul>
        </section>
        <section>
          <h2>指標樣本</h2>
          <ul>{samples}</ul>
          <p><a href="/indicators">查看全部指標</a></p>
        </section>
        """,
    )


def _indicator_index_html(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    role_labels: dict[str, str],
    runtime_live_mode: bool,
) -> str:
    cards = "\n".join(
        _role_card(row, display_name_zh=role_labels[row["role_id"]])
        for row in snapshot["role_snapshots"]
    )
    caveats = "\n".join(
        f"<li>{escape(item)}</li>" for item in _mobile_trust_caveats()
    )
    return _html_document(
        title="指標總覽",
        body=f"""
        <section class="hero">
          <p class="eyebrow">research-only / {escape(_dashboard_data_source_label(runtime_live_mode))}</p>
          <h1>總經指標快照</h1>
          <p>每個卡片顯示繁中名稱、最新 revised 數值、資料新鮮度、來源血緣、
          PIT 補齊狀態與資料缺口。可展開查看今年以來、過去 1 年與過去 5 年走勢；
          blocked 不會被當作 neutral，也不會被補零。</p>
        </section>
        <section>
          <h2>資料邊界</h2>
          <ul>{caveats}</ul>
        </section>
        <section class="role-grid">{cards}</section>
        """,
    )


def _role_card(row: dict[str, Any], *, display_name_zh: str) -> str:
    status = row["snapshot_status"]
    latest = row["latest_revised_observations"]
    latest_display = latest[0] if latest else {}
    observation_date = latest_display.get("observation_date") or "尚無數值"
    value_text = latest_display.get("value_numeric")
    if value_text is None:
        value_text = latest_display.get("value_text") or "unavailable"
    unit = latest_display.get("unit") or "未提供"
    blocked = ", ".join(row["blocked_reason_codes"]) or "none"
    freshness = _freshness_label_zh(row.get("freshness_status", "unavailable"))
    chart_html = _chart_details_html(row.get("chart_payload_detail", {}))
    return f"""
    <article id="role-{escape(row['role_id'])}" class="role-card"
      data-role-card="true" data-snapshot-status="{escape(status)}">
      <h3>{escape(display_name_zh)}</h3>
      <p class="technical-id">技術識別：<code>{escape(row['role_id'])}</code></p>
      <p class="meta">{escape(row['phase_or_layer'])} / {escape(row['major_group_id'])}</p>
      <dl>
        <dt>快照狀態</dt><dd>{escape(status)}</dd>
        <dt>最新 revised 日期</dt><dd>{escape(str(observation_date))}</dd>
        <dt>最新 revised 值</dt><dd>{escape(str(value_text))}</dd>
        <dt>單位</dt><dd>{escape(str(unit))}</dd>
        <dt>資料新鮮度</dt><dd>{escape(freshness)}</dd>
        <dt>PIT 補齊</dt><dd>{escape(row['pit_backfill_status'])}</dd>
        <dt>缺口</dt><dd>{escape(blocked)}</dd>
      </dl>
      {chart_html}
    </article>
    """


def _role_sample(row: dict[str, Any], *, display_name_zh: str) -> str:
    return (
        f"<li><a href=\"/indicators#role-{escape(row['role_id'])}\">"
        f"{escape(display_name_zh)}</a> - {escape(row['snapshot_status'])}</li>"
    )


def _dashboard_eyebrow(runtime_live_mode: bool) -> str:
    if runtime_live_mode:
        return "私人 NAS / PostgreSQL revised research data"
    return "Phase95 / private NAS dynamic service rehearsal"


def _dashboard_heading(runtime_live_mode: bool) -> str:
    if runtime_live_mode:
        return "景氣循環私人研究儀表板"
    return "NAS 私有研究儀表板資料路由"


def _dashboard_intro(runtime_live_mode: bool) -> str:
    if runtime_live_mode:
        return (
            "此頁由 NAS PostgreSQL 以唯讀模式提供最新 revised 歷史資料。"
            "它是研究用 diagnostic surface，不是正式目前景氣判斷，也不是投資建議。"
        )
    return (
        "此頁使用 Phase94 指標快照建立 server-side HTML 與 JSON API rehearsal。"
        "它是研究用 revised diagnostic surface，不是正式目前景氣判斷，也不是投資建議。"
    )


def _dashboard_data_source_label(runtime_live_mode: bool) -> str:
    return "PostgreSQL revised diagnostic" if runtime_live_mode else "revised diagnostic"


def _refresh_status_html(snapshot: dict[str, Any]) -> str:
    status = snapshot.get("refresh_status", {})
    release = snapshot.get("source_release_diagnostics", {})
    state_labels = {
        "not_started": "尚未開始定期更新",
        "scheduled": "已排程",
        "running": "更新執行中",
        "succeeded": "最近更新成功",
        "failed": "最近更新失敗",
    }
    health_labels = {
        "healthy": "正常",
        "degraded": "最近更新失敗，沿用既有資料",
        "baseline_loaded_waiting_for_scheduled_refresh": "已有基準資料，等待排程更新",
        "unavailable": "無可用來源資料",
    }
    state = str(status.get("refresh_state", "not_started"))
    health = str(snapshot.get("source_refresh_health_status", "unknown"))
    return f"""
    <section aria-labelledby="refresh-status-heading">
      <h2 id="refresh-status-heading">官方資料更新狀態</h2>
      <div class="summary-grid" data-source-refresh-status="{escape(state)}">
        <article><strong>{escape(state_labels.get(state, state))}</strong><span>排程狀態</span></article>
        <article><strong>{escape(str(status.get('last_completed_at_utc') or '尚無'))}</strong><span>上次完成</span></article>
        <article><strong>{escape(str(status.get('next_scheduled_at_utc') or '尚未排程'))}</strong><span>下次預定</span></article>
        <article><strong>{int(status.get('completed_series_count', 0))}/{int(status.get('requested_series_count', 0))}</strong><span>完成來源</span></article>
      </div>
      <p class="meta">來源健康：{escape(health_labels.get(health, health))}；此更新只代表 revised 資料同步，不代表景氣階段確認。</p>
      <p class="meta">官方發布家族：{int(release.get('release_family_count', 0))}；
      待更新或需查核：{int(release.get('family_due_or_missing_refresh_count', 0))}；
      有失敗原因的序列：{int(release.get('series_with_failure_reason_count', 0))}。</p>
      <p><a href="/source-operations">查看官方發布日曆與更新失敗明細</a></p>
    </section>
    """


def _declared_cycle_state_html(snapshot: dict[str, Any]) -> str:
    state = snapshot.get("declared_cycle_state", {})
    phase = str(state.get("declared_current_phase_label_zh", "榮景"))
    next_phase = str(state.get("legal_next_phase_label_zh", "衰退"))
    start = str(state.get("declared_phase_start_display_zh", "尚待使用者確認"))
    age = state.get("declared_phase_age_days")
    age_range = state.get("declared_phase_age_range_days")
    if age is not None:
        age_display = f"約 {age} 天"
    elif age_range:
        age_display = (
            f"約 {age_range['minimum_days']} 至 {age_range['maximum_days']} 天"
        )
    else:
        age_display = "未知，需使用者確認"
    return f"""
    <section aria-labelledby="declared-cycle-state-heading"
      data-declared-cycle-state="true">
      <h2 id="declared-cycle-state-heading">目前宣告景氣狀態</h2>
      <div class="summary-grid">
        <article><strong>{escape(phase)}</strong><span>宣告階段</span></article>
        <article><strong>{escape(next_phase)}</strong><span>合法下一階段</span></article>
        <article><strong>{escape(start)}</strong><span>榮景起始</span></article>
        <article><strong>{escape(age_display)}</strong><span>階段年齡</span></article>
      </div>
      <p class="meta">這是使用者／治理登錄的研究背景，不是由最新資料推論的目前階段。</p>
      <p><a href="/cycle-state">檢視或確認榮景起始資訊</a></p>
    </section>
    """


def _freshness_label_zh(status: str) -> str:
    return {
        "fresh": "在新鮮度期限內",
        "stale": "已超過新鮮度期限",
        "mixed": "部分序列已過期或頻率不同",
        "unknown_frequency": "頻率未識別，無法判定",
        "unavailable": "無可用資料",
    }.get(status, status)


def _chart_details_html(chart: dict[str, Any]) -> str:
    series_charts = list(chart.get("series_charts", []))
    if not chart.get("chart_available") or not series_charts:
        return "<p class=\"chart-meta\">目前沒有可繪製的 revised 歷史數值。</p>"
    panels = "".join(
        _chart_period_panel(series, period)
        for series in series_charts
        for period in series.get("periods", [])
    )
    return (
        "<details><summary>查看今年／過去 1 年／過去 5 年走勢</summary>"
        f"<div class=\"chart-grid\">{panels}</div></details>"
    )


def _chart_period_panel(series: dict[str, Any], period: dict[str, Any]) -> str:
    title = f"{series.get('series_id', 'series')} · {period.get('label', '')}"
    points = list(period.get("points", []))
    if period.get("chart_status") != "available" or not points:
        return (
            "<section class=\"chart-panel\">"
            f"<h4>{escape(title)}</h4>"
            "<p class=\"chart-meta\">此期間沒有可用數值。</p>"
            "</section>"
        )
    svg, rendered_count = _sparkline_svg(points)
    first = points[0]
    last = points[-1]
    return (
        "<section class=\"chart-panel\">"
        f"<h4>{escape(title)}</h4>"
        '<div class="chart-interactive-wrap">'
        f"{svg}"
        '<output class="chart-tooltip" aria-live="polite" hidden></output>'
        "</div>"
        '<p class="chart-hint">移動游標或觸碰走勢線，可查看日期與數值；鍵盤可用左右方向鍵。</p>'
        f"<p class=\"chart-meta\">{escape(str(first['date']))}："
        f"{escape(str(first['value']))} → {escape(str(last['date']))}："
        f"{escape(str(last['value']))}；資料點 {len(points)}，繪圖點 {rendered_count}</p>"
        "</section>"
    )


def _sparkline_svg(points: list[dict[str, Any]]) -> tuple[str, int]:
    rendered = _downsample_points(points, MAX_RENDERED_SVG_POINTS)
    values = [float(point["value"]) for point in rendered]
    minimum = min(values)
    maximum = max(values)
    span = maximum - minimum
    width = 300.0
    height = 80.0
    padding = 5.0
    coordinates: list[str] = []
    interactive_points: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        x = (
            padding
            if len(values) == 1
            else padding + (width - 2 * padding) * index / (len(values) - 1)
        )
        normalized = 0.5 if span == 0 else (value - minimum) / span
        y = height - padding - (height - 2 * padding) * normalized
        coordinates.append(f"{x:.2f},{y:.2f}")
        interactive_points.append(
            {
                "date": rendered[index]["date"],
                "value": value,
                "x": round(x, 2),
                "y": round(y, 2),
            },
        )
    encoded_points = escape(
        json.dumps(
            interactive_points,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        quote=True,
    )
    svg = (
        '<svg class="interactive-chart" viewBox="0 0 300 80" role="img" '
        'aria-label="指標歷史走勢；可查看日期與數值" tabindex="0" '
        f'data-chart-points="{encoded_points}">'
        '<line class="chart-axis" x1="5" y1="75" x2="295" y2="75"></line>'
        f'<polyline class="chart-line" points="{" ".join(coordinates)}"></polyline>'
        '<line class="chart-crosshair" x1="0" y1="5" x2="0" y2="75" '
        'visibility="hidden"></line>'
        '<circle class="chart-marker" cx="0" cy="0" r="3.5" '
        'visibility="hidden"></circle>'
        "</svg>"
    )
    return svg, len(rendered)


def _downsample_points(
    points: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    if len(points) <= limit:
        return points
    indexes = {
        round(index * (len(points) - 1) / (limit - 1))
        for index in range(limit)
    }
    return [points[index] for index in sorted(indexes)]


def _html_document(*, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Noto Sans TC", sans-serif; background: #f6f7f9; color: #1c2430; }}
    main {{ width: min(1120px, calc(100% - 28px)); margin: 0 auto; padding: 24px 0 40px; }}
    .hero {{ padding: 22px 0 14px; }}
    .eyebrow {{ font-size: 0.78rem; text-transform: uppercase; color: #516070; letter-spacing: 0; }}
    h1 {{ margin: 0 0 10px; font-size: clamp(1.65rem, 5vw, 2.8rem); line-height: 1.12; }}
    h2 {{ margin-top: 26px; font-size: 1.2rem; }}
    .summary-grid, .role-grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }}
    .summary-grid article, .role-card {{ background: #fff; border: 1px solid #d9dee6; border-radius: 8px; padding: 14px; }}
    .summary-grid strong {{ display: block; font-size: 1.8rem; }}
    .summary-grid span, .meta, .technical-id, dt {{ color: #5b6674; }}
    .technical-id {{ margin: -2px 0 8px; font-size: 0.82rem; }}
    details {{ margin-top: 12px; border-top: 1px solid #e1e5ea; padding-top: 10px; }}
    summary {{ color: #0b5cab; cursor: pointer; font-weight: 650; }}
    .chart-grid {{ display: grid; gap: 10px; margin-top: 10px; }}
    .chart-panel {{ border: 1px solid #e1e5ea; border-radius: 6px; padding: 8px; }}
    .chart-panel h4 {{ margin: 0 0 6px; font-size: 0.88rem; }}
    .chart-interactive-wrap {{ position: relative; }}
    .chart-panel svg {{ display: block; width: 100%; height: 92px; touch-action: pan-y; outline: none; }}
    .chart-panel svg:focus-visible {{ outline: 2px solid #0b5cab; outline-offset: 2px; }}
    .chart-axis {{ stroke: #c6cdd5; stroke-width: 1; }}
    .chart-line {{ fill: none; stroke: #0b5cab; stroke-width: 2; vector-effect: non-scaling-stroke; }}
    .chart-crosshair {{ stroke: #59697c; stroke-width: 1; stroke-dasharray: 3 2; vector-effect: non-scaling-stroke; }}
    .chart-marker {{ fill: #fff; stroke: #0b5cab; stroke-width: 2; vector-effect: non-scaling-stroke; }}
    .chart-tooltip {{ position: absolute; top: 2px; z-index: 2; transform: translateX(-50%); background: #1c2430; color: #fff; border-radius: 4px; padding: 5px 7px; font-size: 0.75rem; white-space: nowrap; pointer-events: none; }}
    .chart-hint {{ color: #5b6674; font-size: 0.72rem; margin: 2px 0 5px; }}
    .chart-meta {{ color: #5b6674; font-size: 0.78rem; margin: 4px 0 0; }}
    dl {{ display: grid; grid-template-columns: minmax(92px, auto) 1fr; gap: 6px 10px; margin: 0; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    code {{ background: #e9edf2; border-radius: 4px; padding: 2px 4px; }}
    a {{ color: #0b5cab; }}
    @media (min-width: 720px) {{
      .chart-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <main>{body}</main>
  {_chart_interaction_script()}
</body>
</html>
"""


def _chart_interaction_script() -> str:
    return """<script>
(() => {
  const formatter = new Intl.NumberFormat("zh-TW", { maximumFractionDigits: 4 });
  document.querySelectorAll("svg.interactive-chart").forEach((svg) => {
    const points = JSON.parse(svg.dataset.chartPoints || "[]");
    const wrap = svg.closest(".chart-interactive-wrap");
    const tooltip = wrap?.querySelector(".chart-tooltip");
    const crosshair = svg.querySelector(".chart-crosshair");
    const marker = svg.querySelector(".chart-marker");
    if (!points.length || !tooltip || !crosshair || !marker) return;
    let activeIndex = points.length - 1;
    const showPoint = (index) => {
      activeIndex = Math.max(0, Math.min(points.length - 1, index));
      const point = points[activeIndex];
      crosshair.setAttribute("x1", point.x);
      crosshair.setAttribute("x2", point.x);
      crosshair.setAttribute("visibility", "visible");
      marker.setAttribute("cx", point.x);
      marker.setAttribute("cy", point.y);
      marker.setAttribute("visibility", "visible");
      tooltip.textContent = `${point.date}｜數值 ${formatter.format(point.value)}`;
      tooltip.style.left = `${Math.max(8, Math.min(92, point.x / 3))}%`;
      tooltip.hidden = false;
    };
    const hidePoint = () => {
      crosshair.setAttribute("visibility", "hidden");
      marker.setAttribute("visibility", "hidden");
      tooltip.hidden = true;
    };
    const showFromPointer = (event) => {
      const bounds = svg.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (event.clientX - bounds.left) / bounds.width));
      showPoint(Math.round(ratio * (points.length - 1)));
    };
    svg.addEventListener("pointermove", showFromPointer);
    svg.addEventListener("pointerdown", showFromPointer);
    svg.addEventListener("pointerleave", (event) => {
      if (event.pointerType === "mouse") hidePoint();
    });
    svg.addEventListener("focus", () => showPoint(activeIndex));
    svg.addEventListener("blur", hidePoint);
    svg.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      showPoint(activeIndex + (event.key === "ArrowRight" ? 1 : -1));
    });
  });
})();
</script>"""


def _routes_ready(routes: list[dict[str, Any]], contract: dict[str, Any]) -> bool:
    return (
        len(routes) == int(contract["route_policy"]["route_count"])
        and all(route["private_nas_only"] is True for route in routes)
        and all(route["frontend_database_access_allowed"] is False for route in routes)
        and all(route["frontend_api_key_allowed"] is False for route in routes)
    )


def load_book_core_role_display_labels_zh(
    path: str | Path = DEFAULT_ROLE_LABELS_PATH,
) -> dict[str, str]:
    """Load the governed Traditional Chinese display name for every role."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["book_core_role_display_labels_zh"]
    if contract["language"] != "zh-Hant-TW":
        raise ValueError("book-core role labels must use zh-Hant-TW")
    return {str(key): str(value) for key, value in contract["roles"].items()}


def _validate_role_label_coverage(
    *,
    snapshot: dict[str, Any],
    role_labels: dict[str, str],
) -> None:
    role_ids = {str(row["role_id"]) for row in snapshot["role_snapshots"]}
    label_ids = set(role_labels)
    if role_ids != label_ids:
        missing = sorted(role_ids - label_ids)
        unexpected = sorted(label_ids - role_ids)
        raise ValueError(
            "book-core role label coverage mismatch: "
            f"missing={missing}, unexpected={unexpected}",
        )
    if any(not label.strip() for label in role_labels.values()):
        raise ValueError("book-core Traditional Chinese role labels must be non-empty")


def _api_payloads_ready(api_payloads: dict[str, Any], snapshot: dict[str, Any]) -> bool:
    expected_live_db = bool(snapshot["trust_metadata"].get("live_db_connected"))
    return (
        len(api_payloads) == 3
        and api_payloads["indicator_snapshot"]["role_count"]
        == snapshot["role_snapshot_count"]
        and api_payloads["service_status"]["live_db_connection_attempted"]
        is expected_live_db
        and api_payloads["service_status"]["postgres_write_attempted"] is False
        and api_payloads["service_status"]["live_fetch_attempted"] is False
        and api_payloads["service_status"]["frontend_database_access_allowed"] is False
        and api_payloads["service_status"]["frontend_api_key_allowed"] is False
    )


def _html_pages_ready(html_pages: list[dict[str, Any]], snapshot: dict[str, Any]) -> bool:
    html = "\n".join(page["html"] for page in html_pages)
    return (
        len(html_pages) == 2
        and "NAS 私有研究儀表板" in html
        and "research-only" in html
        and "revised diagnostic" in html
        and 'data-role-card="true"' in html
        and _html_marker_count(html_pages, "data-role-card=")
        == snapshot["role_snapshot_count"]
    )


def _trust_metadata(contract: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    live_db_connected = bool(snapshot["trust_metadata"].get("live_db_connected"))
    return {
        "service_target": contract["service_scope"]["target_runtime"],
        "nas_migration_surface": (
            "live_postgres_route_api_html_renderer"
            if live_db_connected
            else "route_api_html_renderer_rehearsal"
        ),
        "source_snapshot_artifact_id": snapshot["artifact_id"],
        "source_snapshot_hash": snapshot["snapshot_manifest_hash"],
        "research_only": True,
        "revised_diagnostic_only": True,
        "pit_availability_accounting_included": True,
        "strict_point_in_time_result": False,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "live_db_connection_attempted": live_db_connected,
        "live_db_connected": live_db_connected,
        "refresh_state": snapshot.get("refresh_status", {}).get(
            "refresh_state",
            "not_configured",
        ),
        "source_refresh_health_status": snapshot.get(
            "source_refresh_health_status",
            "not_configured",
        ),
        "declared_state_source": snapshot.get("declared_cycle_state", {}).get(
            "active_registry_source",
            "canonical_default",
        ),
        "postgres_write_attempted": False,
        "live_fetch_attempted": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _live_runtime_bundle_ready(bundle: dict[str, Any]) -> bool:
    return (
        bundle["nas_service_dashboard_contract_ready"] is True
        and bundle["nas_service_route_manifest_ready"] is True
        and bundle["nas_service_api_payload_ready"] is True
        and bundle["nas_service_html_renderer_ready"] is True
        and bundle["role_card_count"] == 39
        and bundle["traditional_chinese_role_label_count"] == 39
        and bundle["live_db_connection_attempt_count"] == 1
        and bundle["postgres_write_attempt_count"] == 0
        and bundle["candidate_phase_emitted"] is False
        and bundle["current_phase_emitted"] is False
        and bundle["prohibited_output_field_count"] == 0
    )


def _mobile_trust_caveats() -> list[str]:
    return [
        "研究用，不是正式景氣階段判斷。",
        "目前數值使用 revised diagnostic snapshot。",
        "PIT 欄位只表示補齊可行性，不是 point-in-time 結果。",
        "前端不持有資料庫帳密或 API key。",
        "不輸出買賣、配置或個人化交易指令。",
        "blocked/missing 不會被當作 neutral 或補零。",
    ]


def _validated_tmp_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    if resolved == tmp_resolved or tmp_resolved in resolved.parents:
        return path
    raise ValueError("Phase95 dry-run output must be under /tmp")


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _html_marker_count(html_pages: list[dict[str, Any]], marker: str) -> int:
    return sum(page["html"].count(marker) for page in html_pages)


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0

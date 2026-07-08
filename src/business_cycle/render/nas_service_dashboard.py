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
TMP_ROOT = Path("/tmp")

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
) -> dict[str, Any]:
    """Build route, API, and HTML view-models without starting a service."""

    contract = load_nas_service_dashboard_contract(contract_path)
    snapshot = snapshot_manifest or build_nas_indicator_snapshot_manifest()
    routes = _route_manifest(contract)
    api_payloads = _api_payloads(snapshot=snapshot, contract=contract, routes=routes)
    html_pages = _html_pages(snapshot=snapshot, contract=contract, routes=routes)
    progress = summarize_product_capability_progress()
    bundle: dict[str, Any] = {
        "phase": "95",
        "phase_id": 95,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase95_nas_service_dashboard_renderer",
        "artifact_version": contract["version"],
        "output_mode": "research_only_private_nas_dashboard_rehearsal",
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
        "mobile_trust_caveat_count": len(_mobile_trust_caveats()),
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "live_server_start_attempt_count": 0,
        "live_db_connection_attempt_count": 0,
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
    bundle["nas_service_dashboard_ready"] = _passes(bundle, contract["hard_gates"])
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
) -> dict[str, Any]:
    roles = [_role_api_row(row) for row in snapshot["role_snapshots"]]
    return {
        "indicator_snapshot": {
            "payload_id": "nas_indicator_snapshot_api_v1",
            "path": "/api/indicator-snapshot.json",
            "output_mode": "research_only_private_nas_api",
            "snapshot_manifest_hash": snapshot["snapshot_manifest_hash"],
            "data_mode": "revised_diagnostic_with_pit_availability_accounting",
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
            "live_db_connection_attempted": False,
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
                    "phase_or_layer": row["phase_or_layer"],
                    "major_group_id": row["major_group_id"],
                    "snapshot_status": row["snapshot_status"],
                    "pit_backfill_status": row["pit_backfill_status"],
                    "detail_anchor": f"#role-{row['role_id']}",
                }
                for row in roles
            ],
        },
    }


def _role_api_row(row: dict[str, Any]) -> dict[str, Any]:
    latest = row["latest_revised_observations"]
    latest_display = latest[0] if latest else {}
    return {
        "role_id": row["role_id"],
        "phase_or_layer": row["phase_or_layer"],
        "major_group_id": row["major_group_id"],
        "official_series_ids": row["official_series_ids"],
        "snapshot_status": row["snapshot_status"],
        "data_mode": row["data_mode"],
        "latest_revised_observation_count": len(latest),
        "latest_observation_date": latest_display.get("observation_date"),
        "latest_value_text": latest_display.get("value_text"),
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
) -> list[dict[str, Any]]:
    return [
        {
            "page_id": "overview",
            "path": "/",
            "title_zh": "NAS 私有研究儀表板",
            "html": _overview_html(snapshot=snapshot, contract=contract, routes=routes),
        },
        {
            "page_id": "indicator_index",
            "path": "/indicators",
            "title_zh": "指標總覽",
            "html": _indicator_index_html(snapshot=snapshot, contract=contract),
        },
    ]


def _overview_html(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
) -> str:
    samples = "\n".join(
        _role_sample(row)
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
    return _html_document(
        title="NAS 私有研究儀表板",
        body=f"""
        <section class="hero">
          <p class="eyebrow">Phase95 / private NAS dynamic service rehearsal</p>
          <h1>NAS 私有研究儀表板資料路由</h1>
          <p>此頁使用 Phase94 指標快照建立 server-side HTML 與 JSON API rehearsal。
          它是研究用 revised diagnostic surface，不是正式目前景氣判斷，也不是投資建議。</p>
        </section>
        <section class="summary-grid">
          <article><strong>{snapshot['role_snapshot_count']}</strong><span>指標角色快照</span></article>
          <article><strong>{snapshot['role_with_revised_snapshot_count']}</strong><span>有 revised 數值</span></article>
          <article><strong>{snapshot['role_without_revised_snapshot_count']}</strong><span>資料 blocked</span></article>
          <article><strong>{snapshot['series_snapshot_count']}</strong><span>序列快照</span></article>
        </section>
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
) -> str:
    cards = "\n".join(_role_card(row) for row in snapshot["role_snapshots"])
    caveats = "\n".join(
        f"<li>{escape(item)}</li>" for item in _mobile_trust_caveats()
    )
    return _html_document(
        title="指標總覽",
        body=f"""
        <section class="hero">
          <p class="eyebrow">research-only / revised diagnostic</p>
          <h1>總經指標快照</h1>
          <p>每個卡片顯示 role、major group、latest revised context、PIT 補齊狀態與資料缺口。
          blocked 不會被當作 neutral，也不會被補零。</p>
        </section>
        <section>
          <h2>資料邊界</h2>
          <ul>{caveats}</ul>
        </section>
        <section class="role-grid">{cards}</section>
        """,
    )


def _role_card(row: dict[str, Any]) -> str:
    status = row["snapshot_status"]
    latest = row["latest_revised_observations"]
    latest_display = latest[0] if latest else {}
    observation_date = latest_display.get("observation_date") or "尚無數值"
    value_text = latest_display.get("value_text") or "unavailable"
    blocked = ", ".join(row["blocked_reason_codes"]) or "none"
    return f"""
    <article id="role-{escape(row['role_id'])}" class="role-card"
      data-role-card="true" data-snapshot-status="{escape(status)}">
      <h3>{escape(row['role_id'])}</h3>
      <p class="meta">{escape(row['phase_or_layer'])} / {escape(row['major_group_id'])}</p>
      <dl>
        <dt>快照狀態</dt><dd>{escape(status)}</dd>
        <dt>最新 revised 日期</dt><dd>{escape(str(observation_date))}</dd>
        <dt>最新 revised 值</dt><dd>{escape(str(value_text))}</dd>
        <dt>PIT 補齊</dt><dd>{escape(row['pit_backfill_status'])}</dd>
        <dt>缺口</dt><dd>{escape(blocked)}</dd>
      </dl>
    </article>
    """


def _role_sample(row: dict[str, Any]) -> str:
    return (
        f"<li><a href=\"/indicators#role-{escape(row['role_id'])}\">"
        f"{escape(row['role_id'])}</a> - {escape(row['snapshot_status'])}</li>"
    )


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
    .summary-grid span, .meta, dt {{ color: #5b6674; }}
    dl {{ display: grid; grid-template-columns: minmax(92px, auto) 1fr; gap: 6px 10px; margin: 0; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    code {{ background: #e9edf2; border-radius: 4px; padding: 2px 4px; }}
    a {{ color: #0b5cab; }}
  </style>
</head>
<body>
  <main>{body}</main>
</body>
</html>
"""


def _routes_ready(routes: list[dict[str, Any]], contract: dict[str, Any]) -> bool:
    return (
        len(routes) == int(contract["route_policy"]["route_count"])
        and all(route["private_nas_only"] is True for route in routes)
        and all(route["frontend_database_access_allowed"] is False for route in routes)
        and all(route["frontend_api_key_allowed"] is False for route in routes)
    )


def _api_payloads_ready(api_payloads: dict[str, Any], snapshot: dict[str, Any]) -> bool:
    return (
        len(api_payloads) == 3
        and api_payloads["indicator_snapshot"]["role_count"]
        == snapshot["role_snapshot_count"]
        and api_payloads["service_status"]["live_db_connection_attempted"] is False
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
    return {
        "service_target": contract["service_scope"]["target_runtime"],
        "nas_migration_surface": "route_api_html_renderer_rehearsal",
        "source_snapshot_artifact_id": snapshot["artifact_id"],
        "source_snapshot_hash": snapshot["snapshot_manifest_hash"],
        "research_only": True,
        "revised_diagnostic_only": True,
        "pit_availability_accounting_included": True,
        "strict_point_in_time_result": False,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
        "live_fetch_attempted": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


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

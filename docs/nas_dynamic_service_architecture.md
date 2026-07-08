---
version: "1.6"
status: active
phase_id: 96
contract_path: specs/common/nas_dynamic_service_contract.yaml
---

# NAS Dynamic Service Architecture

Phase 90 retires GitHub Pages as the product deployment target and records the
new private NAS dynamic-service direction. The GitHub repository may remain a
source-control and CI safety net, but the user-facing dashboard should move to a
private NAS service.

## Target Shape

The first NAS service target is:

- Synology DS925+ as the host.
- Private mobile access through Tailscale or another VPN-style private network.
- FastAPI-style Python web service.
- Server-rendered HTML with Jinja/HTMX or similarly small frontend glue.
- Postgres as the macro data warehouse.
- Python refresh worker for source pulls and derived evidence snapshots.
- No direct browser-to-Postgres access.
- No frontend API keys.

The service remains a research system. It must not emit personalized trade
instructions, live allocation instructions, or a standalone current phase
classifier.

## Component Boundary

```text
source adapters
  -> refresh worker
  -> Postgres macro warehouse
  -> service layer
  -> dashboard pages and JSON endpoints
```

The dashboard may show declared current phase, declared phase age, legal next
phase, transition evidence, indicator details, YTD/1Y/5Y charts, historical
replay views, and portfolio policy research templates. It must label research
surfaces and preserve the distinction between evidence, watch, confirmation,
candidate transition, and current declared state.

## Data Warehouse Direction

The Postgres schema must support point-in-time and vintage semantics from the
start. Phase 91 records the schema contract in
`specs/common/postgres_macro_warehouse_contract.yaml` and provides a
deterministic DDL preview through `scripts/show_postgres_macro_warehouse_contract.py`.
The first data-completeness sprint may fill revised data first, but the schema
and contracts must not force a later rewrite to support vintage data.

Planned table families:

- `series_registry`
- `observation_revised`
- `observation_vintage`
- `release_calendar`
- `source_artifact`
- `indicator_value_snapshot`
- `evidence_snapshot`
- `dashboard_snapshot`
- `backtest_run`
- `backtest_result`
- `portfolio_policy_run`

Revised data completeness and vintage backfill are separate work:

- Phase 91: PIT-ready Postgres schema contract and DDL preview.
- Phase 92: revised macro data completeness import dry-run. This phase maps the
  current official/accepted macro source set into warehouse-shaped
  `series_registry`, `source_artifact`, and `observation_revised` rows without
  connecting to a live database or writing repository outputs.
- Phase 93: vintage/PIT backfill and availability accounting.
  This phase keeps the import no-write: it plans 24 direct vintage requests and
  one derived same-as-of PIT plan, records missing derived-lineage blockers, and
  writes no `observation_vintage` rows.
- Phase 94: NAS indicator snapshot materialization. This phase joins revised
  rows, source artifacts, and PIT availability accounting into a server-side
  indicator snapshot/view-model for the private NAS service. It does not create
  API endpoints, connect to Postgres, write `public/`, or emit current/candidate
  phase decisions.
- Phase 95: NAS service dashboard route/API/HTML rehearsal. This phase defines
  four private route shapes and renders two Traditional Chinese HTML pages plus
  three JSON payloads from the Phase 94 snapshot. It writes only to `/tmp` when
  explicitly requested, starts no live server, reads no live Postgres instance,
  and keeps browser-to-database/API-key access prohibited.
- Phase 96: NAS app shell local service smoke. This phase mounts the Phase 95
  routes in an in-process Python dispatcher, verifies a local session boundary,
  service-health payload, and rollback checklist, and still avoids network
  binding, live Postgres reads, live fetches, and public output.

## GitHub Pages Retirement

GitHub Pages is no longer a deployment target.

Required retirement conditions:

- `.github/workflows/pages.yml` is absent.
- CI workflows do not use `actions/configure-pages`,
  `actions/upload-pages-artifact`, or `actions/deploy-pages`.
- Pages-specific build and validator scripts are removed.
- `public/` remains generated local output only and must not be committed.

## Operational Notes

The first NAS deployment should prefer private networking over public exposure.
Public internet exposure, if ever wanted, needs a later explicit gate covering
TLS, authentication, rate limiting, rollback, backups, and source-secret
handling.

Backups must cover:

- Postgres data volume.
- Source artifacts and checksums.
- Application config excluding secrets.
- Versioned code release or git checkout.

## Deferred Gaps

- FastAPI service skeleton.
- Executed Postgres migrations and live DB smoke test.
- Live FastAPI/ASGI route mounting for the Phase 96 app shell.
- Production-grade auth/session boundary for private mobile use.
- Local Postgres read smoke with read-only credentials.
- Data refresh worker.
- Executed revised data import into the NAS Postgres instance.
- Executed vintage/PIT backfill into `observation_vintage`.
- NAS smoke test.
- Mobile dashboard browser verification over private access.

---
version: "3.0"
status: active
phase_id: 110
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
- Phase 97: ASGI adapter skeleton. This phase wraps the Phase 96 shell in a
  pure-Python ASGI callable that can be mounted by a later FastAPI/ASGI service.
  It verifies ASGI scope translation, authenticated and unauthenticated request
  handling, unsupported-method rejection, and unknown-route rejection without
  starting uvicorn, binding a port, reading Postgres, fetching live data, or
  writing public output.
- Phase 98: local service lifecycle rehearsal. This phase rehearses startup,
  readiness probes, shutdown, and rollback around the Phase 97 ASGI adapter.
  It still runs entirely in-process: no uvicorn, no network bind, no live
  server, no Postgres read/write, no live fetch, and no public output.
- Phase 99: fixture-backed Postgres read-only smoke and DS925+ package
  assessment. This phase validates read-only SQL shape, result row schema, and
  forbidden SQL rejection against Phase 92 warehouse-shaped fixture rows. It
  also records the preferred DS925+ package path: Container Manager for app and
  Postgres containers, Tailscale for private mobile access, and backup packages
  for later volume protection. It still performs no live database connection,
  no Postgres read/write, no schema migration, no network bind, and no public
  output.
- Phase 100: Container Manager compose/service bundle dry-run. This phase
  generates a governed compose preview, environment template, runbook, and
  rollback checklist for DS925+ Container Manager review. It does not import
  the bundle, run Docker/Container Manager, pull images, start containers, bind
  ports, connect to Postgres, migrate schema, fetch live data, or write repo
  outputs.
- Phase 101: private local service startup smoke. This phase validates the
  side-effect-free ASGI factory, startup command preview, readiness probes,
  environment placeholders, and rollback sequence for a private local runner.
  It does not run uvicorn, bind a port, start a live service, import Container
  Manager bundles, start containers, connect to Postgres, migrate schema, fetch
  live data, or write repo outputs.
- Phase 102: guided DS925+ install and NAS-side read-only smoke plan. This
  phase records the package checklist, operator inputs, install runbook,
  read-only smoke command preview, and rollback checklist for the future
  DS925+ handoff. It still performs no NAS login, package install, Tailscale
  login, Container Manager import, container start, live database read/write,
  schema migration, live data fetch, or repository output.
- Phase 103: DS925+ private LAN endpoint registration and connectivity smoke.
  This phase records the user-provided NAS IP `192.168.1.116` and adds an
  explicit-flag-only unauthenticated TCP reachability smoke for DSM/reverse
  proxy ports. CI remains no-network preview only. The live probe does not log
  into DSM or SSH, install packages, import Container Manager bundles, start
  containers, connect to Postgres, run migrations, fetch live data, or write
  repository output.
- Phase 104: NAS Postgres revised import and backup rehearsal. This phase
  converts the Phase 92 revised macro import manifest into a DS925+ handoff
  plan: table row counts, deterministic SQL preview comments, backup
  prerequisites, and restore-verification queries. It still does not connect to
  Postgres, execute schema migration, run backup or restore commands, import
  Container Manager bundles, fetch live data, or write repository output.
- Phase 105: NAS operator deployment handoff. This phase turns the Phase
  100-104 rehearsals into an operator preflight checklist, Container Manager
  import handoff, private auth acceptance checks, health checks,
  backup/rollback acceptance checks, and go/no-go gates. It still performs no
  DSM login, package install, tailnet login, Container Manager import,
  container start, live server start, Postgres read/write, schema migration,
  backup/restore execution, live fetch, or repository output.
- Phase 106: NAS operator live deployment session protocol. This phase expands
  the Phase105 handoff into 41 operator-owned actions, a live-session report
  template, a sample report validator, and acceptance artifacts. It still does
  not execute DSM login, package install, tailnet login, Container Manager
  import, container start, live server start, Postgres read/write, schema
  migration, backup/restore execution, live fetch, or repository output.
- Phase 107: NAS app container runtime bundle. This phase adds `Dockerfile.nas`,
  a Docker ignore policy, a standard-library private runtime HTTP server,
  container healthcheck, disabled refresh-worker entrypoint, and a buildable
  Container Manager compose bundle for `business-cycle-nas-app:phase107`. It
  still does not execute Docker build, Container Manager import, container
  start, live DB read/write, schema migration, live fetch, or public output.
- Phase 108: NAS Container Manager live-start package. This phase prepares the
  operator-owned import/build/start checklist, redacted live-start report
  template, private health/auth smoke checks, rollback drill, and validator for
  the Phase107 bundle. It still does not execute DSM login, Container Manager
  import, Docker build, container start, live DB read/write, schema migration,
  live fetch, or public output.

## DS925+ Deployment Package Assessment

Phase 99 records the current deployment recommendation in
`specs/audits/nas_ds925_deployment_package_assessment.yaml`.

Recommended package path:

- Container Manager as the primary deployment runtime.
- Official PostgreSQL container image as the preferred database runtime.
- Application container for the Python ASGI service.
- Tailscale for private phone access without exposing the NAS directly to the
  public internet.
- Hyper Backup / Snapshot Replication as later backup and rollback support.

Estimated deployment sequence:

- Phase 100: generate a Container Manager compose/service bundle dry-run.
- Phase 101: private local service startup smoke, command preview, and
  readiness-probe precheck.
- Phase 102: guided DS925+ install and NAS-side read-only smoke runbook. The
  live install remains operator-assisted and requires explicit confirmation.
- Phase 103: register the DS925+ private LAN endpoint and run an optional
  no-login TCP reachability smoke with explicit operator confirmation.
- Phase 104: rehearse revised macro data import into NAS Postgres and backup
  verification without live DB writes.
- Phase 105: operator-approved live NAS deployment handoff: Container Manager
  import, private auth, health check, and rollback acceptance, still emitted as
  a no-live-execution handoff package.
- Phase 106: operator-guided live deployment session can execute only after
  explicit approval, using the Phase 105 handoff package as the checklist.
  Phase 106 records the protocol and report template; live acceptance remains
  blocked until an operator-supplied report is validated.
- Phase 107: add the buildable NAS app image/runtime bundle and compose package
  so the DS925+ has an actual app container target instead of a dry-run image.
- Phase 108: operator imports/builds the Phase107 bundle in Container Manager,
  starts the private service, and returns the live health/auth/rollback report
  for validation. The repository now provides the checklist, report template,
  sample validator fixture, and rollback drill; live acceptance remains blocked
  until the operator report is supplied.
- Phase 109: reconcile the actual running app/Postgres containers, harden the
  browser login for HTTPS, and establish the Tailscale Serve/mobile acceptance
  gate. The NAS Tailscale node and private HTTPS Serve are online, the app is
  loopback-only with secure cookies, and phone cellular HTTPS/login/dashboard
  acceptance has passed. Funnel and public router forwarding remain prohibited.
- Phase 110: execute the first operator-authorized NAS Postgres migration and
  revised-history import. The live `macro` schema now contains 11 governed
  tables, 26 official source-series registry rows, 26 checksummed source
  artifacts, and 22,131 revised observations spanning 1919-01-01 through
  2026-07-04. The import is resumable and idempotent. `observation_vintage`
  remains empty, and no revised row may be described as point-in-time evidence.
- Phase 111: replace the active private NAS dashboard's bundled indicator values
  with a server-side, read-only Postgres materialization. The dashboard now
  exposes 37 available book-core role values, two explicit source-blocked roles,
  source lineage, freshness, and expandable YTD/1Y/5Y revised charts. A
  configured database failure blocks startup instead of silently falling back
  to fixtures. This read surface does not infer a current or candidate phase.
- Phase 112: run the existing revised-history importer as a governed daily NAS
  worker. Each execution requires the deployment confirmation, takes a
  single-process lock, uses three bounded source retries, writes per-run source
  artifacts, and atomically updates a redacted status file. The private
  dashboard reads that status, shows source health and last/next refresh times,
  and rematerializes its read-only Postgres snapshot on a 15-minute TTL. A
  refresh-read failure retains the last good snapshot with an explicit stale
  marker. This does not create point-in-time data or infer a phase.
- Phase 113: add an authenticated private-NAS declared boom start workflow.
  The operator page can preview either an exact user-declared date or a bounded
  user-declared window, rejects stale previews, and requires an explicit
  confirmation before atomically writing the NAS-only registry override. Every
  update retains a prior-registry backup and a hash-only event record; rollback
  requires a second explicit confirmation. The repository canonical registry
  remains the read-only default, and no macro data is used to infer the start.
- Phase 114: add `/source-operations` and
  `/api/source-operations.json`. The surface maps 26 direct series to 12
  official release families, shows exact official dates only where verified,
  and keeps cadence/reference-only sources from being mislabeled as delayed.
  Scheduled refresh status now preserves a redacted per-series trail so an
  operator can distinguish a source fetch failure, a downstream series not
  attempted after an earlier failure, and an official release merely waiting
  for the next refresh.
- Phase 115: add a token-bound failed-source retry preview and subset execution
  gate on the existing worker. A private custom-format Postgres backup is
  restored to an isolated staging database and verified against five table
  counts; source artifacts are restored to a temporary directory and checked by
  hash. The staging database is dropped after the drill, and the authenticated
  source-operations page displays only redacted verification status.
  The NAS image pins a PostgreSQL 16 client and refuses the drill when client
  and server major versions differ.
- Phase 116: replace elapsed 86,400-second scheduling with a fixed 03:30
  Asia/Taipei daily refresh. Exact official release events can schedule a
  canonical source-family subset follow-up after a governed ingestion buffer;
  cadence/reference-only sources retain the daily fallback. A private backup
  retention preview keeps seven successes and three failures while preserving
  unknown legacy runs; automatic deletion remains disabled.

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

- Tailscale stable update, access-grant review, DSM firewall review, and server
  key-expiry review.
- Exact-vintage/PIT backfill and normalized Postgres release-calendar rows.
- User confirmation of the declared boom exact start date or bounded window;
  until then, the dashboard displays an explicit unknown phase age.
- Dedicated least-privilege dashboard database role and credential rotation.
- Executed vintage/PIT backfill into `observation_vintage`.
- Backup restore rehearsal for Postgres and source artifacts.

---
phase_id: 96
phase_label: nas_app_shell_local_service_smoke
status: completed_research_only
---

# Phase 96 Product Alignment Cleanup Plan

Phase 96 adds the smallest useful NAS application shell around the Phase 95
route/API/HTML renderer. It is intentionally in-process: no network port is
bound, no live Postgres instance is opened, and no public output is written.

## Completed

- Added `specs/common/nas_app_shell_contract.yaml`.
- Added an in-process route dispatcher for five private NAS routes.
- Added a local smoke session boundary using a non-secret development marker.
- Verified unauthenticated requests are rejected.
- Verified authenticated smoke requests pass for every route.
- Added a service-health payload.
- Added a six-step rollback checklist.
- Added Phase96 closure checks and CI closure wiring.
- Updated product capability progress from the Phase95 NAS rebaseline.

## Explicit Non-Goals

- No live FastAPI/ASGI server start.
- No network bind.
- No live Postgres connection.
- No Postgres write.
- No live source fetch.
- No `public/` output.
- No production authentication claim.
- No strict point-in-time result.
- No candidate or current phase output.
- No portfolio or trade output.

## Next Gap

Phase 97 should add either a live ASGI adapter skeleton or a read-only local
Postgres smoke. The safer next step is likely an ASGI adapter skeleton first,
then a separate DB read smoke after local NAS credentials and database setup are
available.

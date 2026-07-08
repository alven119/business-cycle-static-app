---
phase_id: 97
phase_label: nas_asgi_adapter_skeleton_no_live_server
status: completed_research_only
---

# Phase 97 Product Alignment Cleanup Plan

Phase 97 adds a minimal ASGI-compatible adapter around the Phase 96 NAS app
shell. It is a mountable runtime shape for a future FastAPI/ASGI service, not a
live deployment step.

## Completed

- Added `specs/common/nas_asgi_adapter_contract.yaml`.
- Added `src/business_cycle/service/nas_asgi_adapter.py`.
- Added ASGI scope translation for the five Phase 96 private NAS routes.
- Verified authenticated ASGI smoke requests return `200`.
- Verified unauthenticated ASGI smoke requests return `401`.
- Verified unsupported methods return `405`.
- Verified an unknown route returns `404`.
- Added Phase97 closure checks and CI closure wiring.
- Updated product capability progress from the Phase96 NAS app shell baseline.

## Explicit Non-Goals

- No uvicorn run.
- No network bind.
- No live server process.
- No FastAPI dependency requirement yet.
- No live Postgres read.
- No Postgres write.
- No live macro source fetch.
- No `public/` output.
- No production authentication claim.
- No strict point-in-time result.
- No candidate or current phase output.
- No portfolio or trade output.

## Next Gap

Phase 98 should add a live-service startup rehearsal that remains local and
non-networked, or a read-only Postgres smoke if local NAS credentials and a test
database are available. The safer next step is to keep the service adapter
boundary stable before connecting real storage.

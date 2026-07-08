---
phase_id: 98
phase_label: nas_local_service_lifecycle_rehearsal_no_live_bind
status: closed_candidate
---

# Phase 98 Product Alignment Cleanup Plan

Phase 98 advances the private NAS migration by rehearsing the local service
lifecycle around the Phase 97 ASGI adapter.

## Completed In This Phase

- Added a governed NAS service lifecycle contract.
- Rehearsed startup, readiness probes, shutdown, and rollback in-process.
- Verified five ASGI readiness probes against the Phase 97 adapter.
- Preserved no-live boundaries:
  - no uvicorn run
  - no network bind
  - no live server start
  - no live Postgres read or write
  - no live macro fetch
  - no public output
- Added Phase 98 closure checks to the CI closure bundle.

## Product Alignment

This phase supports the NAS dynamic-service path without changing the product
answer shape. It does not introduce a standalone phase classifier, phase score,
phase rank, role-count voting, candidate phase output, current phase output,
portfolio instruction, or backtest execution.

## Deferred Gaps

- Actual FastAPI/ASGI service startup behind private local networking.
- Read-only Postgres smoke using controlled local credentials.
- Production-grade private authentication/session boundary.
- Service process supervision and rollback operation on the NAS.
- Live data refresh worker and scheduled import execution.

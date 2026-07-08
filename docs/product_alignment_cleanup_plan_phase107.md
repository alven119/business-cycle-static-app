---
phase_id: 107
phase_label: nas_app_container_runtime_bundle
status: completed
---

# Phase 107 Product Alignment Cleanup Plan

Phase 107 adds the first buildable NAS app container runtime bundle for the
DS925+ migration. It fills the gap discovered during Phase106: the prior
Container Manager compose preview referenced a dry-run local image and therefore
could not honestly be started on the NAS.

## Added

- `Dockerfile.nas`
- `.dockerignore`
- `src/business_cycle/service/nas_runtime_server.py`
- `src/business_cycle/service/healthcheck.py`
- `src/business_cycle/service/refresh_worker_disabled_until_gate.py`
- `specs/common/nas_app_container_runtime_bundle_contract.yaml`
- `src/business_cycle/service/nas_app_container_runtime_bundle.py`
- `scripts/show_nas_app_container_runtime_bundle.py`
- `scripts/run_nas_app_container_runtime_bundle.py`
- `specs/audits/phase107_nas_app_container_runtime_bundle_closure.yaml`
- `src/business_cycle/audits/phase107_nas_app_container_runtime_bundle_closure.py`
- `scripts/show_phase107_nas_app_container_runtime_bundle_closure.py`

## Product Alignment

- Keeps the product shape as declared state plus legal transition monitoring.
- Adds a private NAS runtime bundle without emitting current/candidate phase.
- Keeps the app service behind loopback host publishing for a later private
  reverse-proxy or Tailscale gate.
- Keeps refresh-worker execution disabled until a future explicit refresh gate.
- Keeps Postgres writes, schema migrations, live fetches, and public output at
  zero in this phase.

## Deferred

- Actual Container Manager import.
- Actual Docker image build on DS925+.
- Actual container start.
- Actual private auth/browser smoke over DSM/Tailscale.
- Actual Postgres schema migration/import/read smoke.
- Actual reverse-proxy or phone-access acceptance.

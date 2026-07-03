# Phase 71 Product Alignment Cleanup Plan

status: declared_phase_start_registry_update_gate_and_dashboard_handoff
closure: specs/audits/phase71_declared_phase_start_registry_update_closure.yaml

## What Changed

Phase 71 upgrades the Phase 70 preview into a governed registry update gate
rehearsal. It supports:

- exact user-supplied declared phase start date
- user-supplied bounded start window
- missing-input rejection
- `/tmp` registry copy write rehearsal
- dashboard handoff explaining exact-date age vs bounded-window age range

The canonical declared registry is not modified.

## Doctrine Boundaries

- No standalone current phase classifier was added.
- No phase score, rank, winner, or role-count vote was added.
- No candidate/current phase output was emitted.
- Current macro data is not used to infer the declared phase.
- Bounded windows never create exact phase-age precision.
- Canonical registry writes require a later explicit gate and user-confirmed
  input.

## Remaining Gap

The next product gap is a user-confirmed declared boom start date or bounded
window for a canonical write gate. Until that happens, the dashboard may show
the handoff mechanics and wait state, but it must not display a precise
declared phase age from the canonical registry.

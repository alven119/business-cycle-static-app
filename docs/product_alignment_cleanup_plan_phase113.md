# Phase 113 Product Alignment Plan

## Product Outcome

Phase 113 deploys the missing governed handoff between the user's declared
`boom` state and a durable private-NAS start context. It does not choose a
date. It gives the authenticated user a safe way to preview and confirm either:

- an exact declared boom start date; or
- a bounded declared boom start window.

The overview then shows the declared phase, legal next phase, start context,
and phase age or age range. This is declared research context, not inferred
current-phase output.

## Write And Rollback Flow

1. The operator opens `/cycle-state` after private login.
2. The operator enters an exact date or bounded window and a reason.
3. Preview validates dates and binds the inputs to the active registry hash.
4. Apply requires an explicit checkbox and rejects stale preview tokens.
5. The app backs up the current registry and atomically writes the NAS-only
   override.
6. Rollback requires the displayed active hash and a separate confirmation.

The repository `specs/common/declared_cycle_state_registry.yaml` remains
unchanged. Runtime state lives in the dedicated `cycle_state_config` volume.

## Safety Boundaries

- Current macro data never selects the start date or declared phase.
- Exact dates may show exact age; bounded windows show only an age range.
- Missing input remains `awaiting_user_confirmation`.
- The app never emits candidate/current phase, phase scores, rankings, trades,
  or personalized portfolio instructions.
- Event records contain hashes and operation metadata, not the confirmation
  note or service secret.
- Tests use only `tmp_path`; no repository output or network is used.

## Test Consolidation

No test file is added. Registry behavior extends the existing Phase 71 update
gate test, HTTP behavior extends the existing NAS runtime test, live rendering
extends the existing Postgres dashboard test, and CI closure indexing remains
in the existing workflow test.

## Completion Semantics

The Phase 113 software capability is complete when the private page/API and
volume are live and rollback is verified in tests. The actual start context
remains pending until the user selects and confirms a value. Structural
completion must not be reported as if the user-supplied date already exists.

## Next Product Gap

Phase 114 should add per-source official release-calendar and refresh failure
drill-down so transition evidence can explain not just whether refresh ran, but
which source is due, stale, delayed, or failed.

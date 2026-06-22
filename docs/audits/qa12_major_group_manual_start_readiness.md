# QA12 Major-Group Manual Start Readiness

QA12 completes the preflight and manual-start contract for the first eligible
forward observation period. It does not start the protocol and does not append
real registry records.

## Readiness Semantics

Observation contract readiness, adapter readiness, live no-write preflight,
period manifest readiness, period completeness, phase-evidence readiness, and
candidate-input completeness are separate gates.

Current major-group state:

- 24 major groups are in scope.
- 15 groups have complete observation-only contracts.
- 3 groups are partial.
- 6 groups remain blocked.
- 0 groups are phase-evidence ready.
- 0 groups are candidate-input complete.

The 15 observation-ready groups do not imply all 24 groups are ready, and
strict historical outputs remain zero. That historical gap does not invalidate
the forward contract, but it also does not create historical validation.

## First Period

The first eligible observation period remains `2026-07`. The first canonical
as-of remains `2026-08-31`. Real append is not allowed before that date, before
all required releases are available, or before period completeness is verified.

QA12 creates a manifest and preview bundle only. Preview records have no real
registry IDs, do not enter the hash chain, and do not contain candidate or
current phase fields.

## Governance

The registry still has zero real records. The protocol is armed but not
started. Candidate monitoring is disabled. Holdout is unregistered.
Production v1 remains unchanged. Real backtest progression and Phase 9B1
remain blocked.

After QA12, the correct next action is
`WAIT_FOR_FIRST_ELIGIBLE_AS_OF`, not a new QA phase to bypass the clock.


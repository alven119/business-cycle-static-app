---
phase_id: "44"
status: phase_contract_and_test_quarantine
created_at: "2026-06-27"
standing_contract: specs/common/phase_execution_standing_contract.yaml
test_quarantine_audit: scripts/audit_test_suite_doctrine_quarantine.py
---

# Phase 44 Phase Execution Contract And Test Quarantine Plan

Phase 44 is a cleanup and quarantine phase. It does not implement the ordered
state machine, boom transition monitor, portfolio policy engine, or historical
replay/backtest vertical slice. It makes future phases easier to prompt and
safer to test.

## Standing Contract

`docs/phase_execution_standing_contract.md` and
`specs/common/phase_execution_standing_contract.yaml` centralize recurring
rules for required reading, start checks, product doctrine, safety, test
strategy, and final report fields. Future prompts should cite this contract
instead of pasting the same boilerplate repeatedly.

## Test Marker Quarantine

The high-risk test suite is classified through pytest markers and a curated
quarantine map in `src/business_cycle/audits/test_suite_doctrine_quarantine.py`.

### Legacy v1

Legacy v1 groups cover phase scoring, score-driven state-machine compatibility,
data-only resolver compatibility, pipeline, snapshot, and production resolver
baseline tests. These tests remain in full pytest but are explicitly labeled as
legacy compatibility, not mature product doctrine.

Representative files:

- `tests/test_phase_scoring.py`
- `tests/test_phase_batch_scoring.py`
- `tests/test_state_machine.py`
- `tests/test_current_phase_resolver.py`
- `tests/test_data_only_resolver.py`
- `tests/test_build_cycle_snapshot_script.py`
- `tests/test_run_cycle_pipeline_script.py`

### Doctrine Aligned

Doctrine-aligned groups cover current research evidence readiness, dashboard
research-only semantics, product doctrine enforcement, and legacy boundary
metadata.

### Governance Scaffold

Governance scaffold groups cover closure, audit, freeze, lineage, and contract
tests. These may exist, but future phases must still show product movement or
be explicitly framed as cleanup, audit, or safety-blocker work.

### Historical Replay/Backtest

Historical accuracy and validation tests are currently replay-support
diagnostics. They are not the final backtest product because mature replay must
also include transition timing, policy replay, cash-flow-aware returns,
drawdowns, false-signal cost, and missed-recovery cost.

### Portfolio Policy Research

Portfolio policy tests cover research template schemas, dry-run contracts, and
safety validators. Template weights remain research assumptions and must not be
used as current allocation recommendations.

### Safety

Safety tests cover secret scans, generated-output scans, prohibited wording,
and result/output validators.

### Live Optional

Live/current refresh probes are marked `live_optional` and excluded from
default pytest and CI. They remain opt-in local checks.

## Updated Future Scope

### Phase 45

Scope:

- declared phase registry
- ordered legal transition state machine
- initial declared phase = boom
- no transition monitor yet unless minimal legal transition metadata is needed

### Phase 46

Scope:

- boom continuation
- boom-ending watch
- recession watch-confirmation monitor

### Phase 47

Scope:

- portfolio policy research template engine

### Phase 48

Scope:

- historical replay/backtest vertical slice

Default recommendation: keep Phase45 focused on registry/state-machine
semantics. Combining Phase45 with a minimal boom transition monitor would raise
blast radius because it mixes declared-state mechanics with phase-specific
evidence routing; keep them separate unless a later prompt explicitly accepts
that risk.

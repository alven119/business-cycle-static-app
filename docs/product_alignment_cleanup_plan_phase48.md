---
phase_id: "48"
status: boom_transition_monitor_evidence_wired_no_phase_selection
---

# Phase 48 Product Alignment Cleanup Plan

Phase 48 wires the Phase 47 priority macro evidence roles into the declared
boom-to-recession transition monitor. This advances the doctrine path from a
lane scaffold to a research-only transition monitor that can explain:

- boom continuation context
- boom ending watch
- recession watch
- recession confirmation diagnostics

The monitor still does not infer the declared current phase, emit a candidate
or current phase, choose a selected phase, compute a phase rank or score, or
modify the declared phase registry.

## Wired Priority Roles

1. `boom_claims_u_shape`
   - Lanes: boom ending watch, recession watch.
   - Boundary: watch only; raw direction and smoothing alone are insufficient.

2. `boom_retail_sales_vs_broad_pce`
   - Lanes: boom continuation, boom ending watch.
   - Boundary: broad consumption context is required; incomplete alignment
     abstains.

3. `boom_private_investment`
   - Lanes: boom continuation, boom ending watch.
   - Boundary: no arbitrary threshold or role-count vote.

4. `recession_employment_confirmation`
   - Lane: recession confirmation.
   - Boundary: confirmation requires stronger evidence than watch.

5. `recession_consumption_confirmation`
   - Lane: recession confirmation.
   - Boundary: broad consumer weakening is required; a single weak retail
     datapoint is not sufficient.

## Preserved Boundaries

- Declared state remains `boom`.
- Legal next phase remains `recession`.
- Phase age remains context only because the declared start date is still
  unknown or user-required.
- Watch evidence is not confirmation.
- Missing, stale, or unavailable evidence produces explicit abstention rather
  than neutral evidence.
- Production v1, portfolio policy output, historical replay/backtest, public
  output, and prospective registry behavior remain unchanged.

## Deferred Gaps

- A user or governed registry update is still required before phase age can be
  precise.
- Live/current data refresh remains opt-in and outside default tests.
- Future dashboard work may render these lane diagnostics, but must preserve
  the research-only labels and prohibited uses.

---
phase_id: "48-plan"
status: preregistered_by_phase47
source_phase: "47"
---

# Phase 48 Boom Monitor Evidence Wiring Plan

Phase 48 should wire concrete evidence into the declared boom transition
monitor without changing the declared phase registry and without emitting
candidate or current phase outputs.

## Lane Inputs

Each input must preserve:

- role or indicator id
- source availability status
- supported data mode
- required transformation
- rule readiness
- lane mapping
- watch versus confirmation semantics
- blocker when the input is not ready

## Highest Product-Value Inputs To Wire First

1. `boom_claims_u_shape`
   - Lane: boom ending watch and continuation context.
   - Why first: claims explain labor-market weakening risk during a declared
     boom and are easy for users to understand.

2. `boom_retail_sales_vs_broad_pce`
   - Lane: boom ending watch.
   - Why first: consumption slowdown is a visible transition-risk narrative.

3. `boom_private_investment`
   - Lane: boom continuation or weakening context.
   - Why first: investment deterioration is central to explaining late-cycle
     fragility.

4. `recession_employment_confirmation`
   - Lane: recession confirmation.
   - Why first: confirmation must remain separate from watch evidence.

5. `recession_consumption_confirmation`
   - Lane: recession confirmation.
   - Why first: it pairs with employment to explain why watch evidence is not
     automatically a recession confirmation.

## Governance Boundaries

- Watch evidence must not be promoted into confirmation.
- Missing evidence must not be treated as neutral.
- Current evidence must not infer the declared current phase.
- No phase score, phase rank, phase winner, selected phase, portfolio action,
  or backtest output may be introduced by this wiring.
- Phase age remains context only unless a later governed registry update adds a
  confirmed declared phase start date.

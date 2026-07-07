# Phase 85 Product Alignment Note

Status: current_data_refresh_ux_hardened

Phase 85 adds a research-only current data refresh UX surface to the latest
evidence dashboard. It summarizes:

- fixture or explicit local cache mode
- last visible observation date
- freshness and missing-value context
- source-risk context
- manual refresh handoff steps

The surface does not run live refresh, does not infer a formal phase from
current data, and does not emit allocation or trade actions. It keeps declared
state and legal transition semantics unchanged.

Product capability impact:

- C1/C2/C3 remain at 100% because the dashboard can now explain both evidence
  and refresh context before a user reads the declared state narrative.
- F1 reaches 100% for the current dashboard sprint because freshness, cache
  mode, visible last-date context, and abstention gaps are now explicit.
- F2 increases through a new contract, closure, and CI closure-check entry.

Next gap: Phase 86 should turn transition risk evidence accumulation into a
clear dashboard view with missing, contradictory, and next-required evidence.

# Phase 87 Product Alignment Note

Phase 87 implements the first step of the Phase 87-91 100% completion route:
research dashboard migration rehearsal.

This phase adds a dashboard-visible rehearsal package for:

- dashboard migration rehearsal
- renderer caveats
- rollback checklist
- production boundary drill

The rehearsal is intentionally research-only. It does not connect the research
dashboard to the production resolver, legacy state machine, Pages publication,
portfolio allocation, candidate phase output, or current phase output.

## Resulting Route

The recorded minimum engineering route remains:

| Phase | Focus |
|---|---|
| 87 | Research dashboard migration rehearsal |
| 88 | Portfolio policy replay research surface completion |
| 89 | Historical replay execution and attribution completion |
| 90 | Research backtest and policy artifact completion |
| 91 | Final research-production migration readiness seal |

If future production usage requires prospective economic validation, that gate
remains calendar-bound and cannot be bypassed by engineering work.

## Doctrine Boundary

Phase 87 preserves:

- declared state as governed input
- legal next transition semantics
- watch / confirmation separation
- missing-data abstention
- no standalone current phase classifier
- no phase score / rank / winner
- no current allocation recommendation
- no trade action
- no production behavior change

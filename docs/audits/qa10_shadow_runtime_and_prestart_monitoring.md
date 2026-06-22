# QA10 Shadow Runtime and Pre-Start Monitoring

QA10 verifies the QA8 evaluator freeze and QA9 monitoring freeze lineage, then
connects the shadow runtime path from causal input history to typed evidence
records. The protocol remains registered and armed but not started.

## Lineage

QA8 `book_faithful_shadow_v2_alpha4` remains the evaluator freeze and has
parent `book_faithful_shadow_v2_alpha3`. QA9
`prospective_shadow_monitoring_v1` points to alpha4. QA10 does not rewrite
either freeze.

## Runtime Window

QA10 fixes the runtime history-window path for the implemented initial-claims
three-calendar-month moving-average evaluator. The window is generated from
the evaluator contract, uses one data mode at a time, rejects future rows,
rejects proxy or revised fallback rows, and preserves abstention when strict
temporal evidence is missing.

The 2019 revised diagnostic now has a ready same-mode window and produces one
shadow smoothing output. That output remains smoothing only; evaluator runtime
readiness is not candidate capability readiness.

## Records

The registry record builder emits typed evidence observations or abstention
observations. Records do not contain candidate phase, current phase, decision
status, portfolio weights, target weights, trade actions, or return fields.
Abstentions require reasons.

Append semantics are hash chained and idempotent. Duplicate equivalent appends
are rejected. Corrections are appended as new records with lineage back to the
original hash; the original record is preserved.

## Pre-Start Gate

The first eligible observation period remains `2026-07`; the first canonical
eligible as-of remains `2026-08-31`. Before that date, real appends are
rejected and no real registry record is written.

Revised mode is allowed only for retrospective diagnostics and temporary
fixtures. A real prospective registry record must use strict point-in-time
evidence. QA10 does not add an automatic schedule.

Production v1 remains unchanged. Holdout is not registered, real backtest
progression remains blocked, and Phase 9B1 remains blocked.

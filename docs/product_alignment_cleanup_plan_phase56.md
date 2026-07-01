# Phase 56 Indicator Detail Source-Risk and Value Rendering

Phase 56 turns the Phase 55 macro coverage matrix into dashboard-ready
indicator detail cards. It is a product-facing explanation phase, not a phase
classifier.

## Product Purpose

The dashboard needs to explain each macro role with enough context for the user
to understand:

- what the role means
- which phase or transition surface it belongs to
- whether its source path is official, composite, user-supplied, or
  supporting-only
- whether a numeric current value is available
- what freshness and release timing say
- why the role still abstains or remains display-only

## Boundaries

This phase preserves the doctrine boundaries:

- no standalone current phase classifier
- no phase rank, score, winner, or role-count vote
- no candidate/current phase emission
- no production v1 behavior change
- no portfolio policy output
- no replay or backtest execution
- no `public`, `data/backtests`, or `data/prospective` output

Supporting proxies remain explanation-only. Authorized private or
user-supplied roles remain missing until local user input is supplied through a
future governed path.

## Result

Phase 56 adds:

- `specs/common/indicator_detail_source_risk_value_rendering.yaml`
- `src/business_cycle/render/indicator_detail_source_risk_values.py`
- `scripts/show_indicator_detail_source_risk_value_rendering.py`
- Phase 56 closure spec, audit, script, and tests

The view model is named `indicator_detail_source_risk_value_cards` and contains
39 research-only cards.

## Next Gap

Phase 57 should complete the boom-to-recession transition surface using these
indicator detail cards as the source-risk and value-context layer.

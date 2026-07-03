# Phase 72 Product Alignment Cleanup Plan

status: current_macro_numeric_chart_coverage_expansion
closure: specs/audits/phase72_current_macro_numeric_chart_coverage_closure.yaml

## What Changed

Phase 72 adds a research-only current macro numeric/chart coverage artifact.
It seeds a temporary fixture cache under `/tmp` and verifies that:

- 37 roles with official series can expose numeric context.
- The same 37 roles can expose YTD, trailing 1Y, and trailing 5Y chart payloads.
- 2 roles without automatable official/public series remain unavailable.
- Chart values are labeled as fixture/cache connectivity, not live or
  point-in-time data.

## Doctrine Boundaries

- No standalone current phase classifier was added.
- No phase score, rank, winner, or role-count vote was added.
- No candidate/current phase output was emitted.
- Current numeric values are not used to infer the declared phase.
- Missing or unavailable charts are not treated as zero or neutral evidence.
- Fixture values are not mislabeled as live data.
- No repository output is written.

## Remaining Gap

The next product gap is replacing fixture coverage with opt-in local current
cache coverage while preserving the same source-risk labels, chart data-mode
caveats, unavailable policy, and no phase-selection boundary.

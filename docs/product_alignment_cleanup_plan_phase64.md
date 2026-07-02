---
phase_id: 64
phase_label: indicator_transparency_chart_payload
status: completed_research_only
---

# Phase64 Indicator Transparency And Chart Payload

Phase64 extends the latest evidence dashboard with two product-facing
explanation layers:

- diagnostic method transparency for each role
- YTD / trailing 1Y / trailing 5Y chart payloads for each role

This is a dashboard education phase. It does not classify the current phase,
does not emit candidate/current phase, does not compute a formal score, and
does not change production v1 behavior.

## What Changed

- Added `indicator_chart_explanation_payload_v1`.
- Added one chart/method payload for all 39 indicator roles.
- Added method recipe visibility, including required inputs, trend windows,
  confirmation windows, minimum history, normalization method, confidence
  behavior, and insufficient-history behavior.
- Added chart payload periods:
  - YTD
  - trailing 1Y
  - trailing 5Y
- Wired those payloads into `latest-evidence.html`.

When no local numeric cache exists, chart payloads are marked unavailable with
an explicit reason. Missing or unavailable chart data is never treated as zero,
neutral, phase support, or a product answer.

## Product Doctrine Boundary

The dashboard still preserves:

- declared state semantics
- legal next transition semantics
- watch/confirmation separation
- research-only labeling
- no phase score/rank/winner
- no candidate/current phase emission
- no portfolio or trade action

## Deferred Gaps

- More actual numeric cache coverage.
- Governed declared boom start date.
- Transition timing replay preview.
- Final production renderer rehearsal through an explicit migration gate.

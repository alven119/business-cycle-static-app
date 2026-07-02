---
phase_id: 63
status: latest_evidence_dashboard_wired_no_phase_selection
dashboard_page: latest-evidence.html
closure: specs/audits/phase63_latest_evidence_dashboard_wiring_closure.yaml
---

# Phase 63：Latest Evidence Dashboard Wiring

Phase 63 wires the governed Phase62 indicator-to-dashboard explanation
drilldown into the local research dashboard HTML. It is a dashboard education
and explainability phase, not a production migration phase.

## What Changed

- Added a research-only `latest-evidence.html` page to the local research
  validation dashboard.
- Added an overview entry and navigation support for the latest evidence page.
- Rendered 24 major-group drilldowns and 39 role drilldowns.
- Rendered role-level source detail, release timing, freshness,
  transformation, rule usability, provenance, data-mode, and abstention
  explanations.
- Added a CLI flag:
  `--include-latest-evidence-drilldown`.
- Added Phase63 closure audit and CI closure wiring.
- Updated product capability progress for the production-distance view.

## Safety Boundaries

- The page is research-only.
- It does not infer the declared phase from current data.
- It does not emit candidate or current phase.
- It does not add phase rank, phase winner, role-count voting, numeric weight,
  trade action, target weight, or portfolio instruction.
- It does not write to `public`, `data/backtests`, or `data/prospective`.
- Legacy production v1 behavior remains unchanged.

## Product Impact

- C1 景氣階段判讀能力：latest evidence is visible from group to role.
- C2 轉折風險偵測能力：transition-related roles can be inspected from the
  dashboard.
- C3 解釋能力：source/rule/provenance/abstention drilldown is now an actual
  HTML surface.
- C6 安全輸出治理：score boundary and research-only labels are verified.
- F1 時間完整性與 abstention：release, freshness, and data-mode caveats are
  visible at role level.

## Deferred Gaps

- Legacy diagnostic score transparency.
- Indicator YTD / trailing 12-month / trailing 5-year chart payloads.
- More numeric current cache values or user-authorized inputs.
- Governed declared boom start date.
- Transition timing replay preview.
- Explicit production migration gate.

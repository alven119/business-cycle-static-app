# Phase 119: NAS Professional Research Dashboard UX Assessment

## User acceptance baseline

The private service is expected to become one coherent personal macro research
platform, not a collection of contract diagnostics. It must help the user:

1. understand the current declared cycle phase and risks of each legal transition;
2. learn the book's macro concepts and indicators through explanations and charts;
3. review book-based allocation research for the declared phase;
4. replay every month of major recession and slowdown scenarios;
5. retain a reusable Postgres macro database for future tools and studies.

Portfolio output remains a book-based research template, not a personalized
trade instruction. The dashboard may say which book template corresponds to the
declared phase and explain why, but it must not place trades or claim guaranteed
performance.

## Current UX diagnosis

The current NAS page proves that live data, indicator cards, charts, source
operations, and governed cycle-state routes work. Its main weakness is
information architecture: many implementation and trust fields share equal
visual weight, while the user's primary questions are not answered first.

Specific gaps:

- The overview does not read like a cycle command center.
- Declared phase, continuation evidence, next-transition watch, confirmation,
  and data health are not one coherent first viewport.
- Indicator cards contain useful material, but do not lead the user through
  meaning, current condition, chart pattern, and book interpretation.
- Portfolio templates exist in contracts but are not a visible declared-phase
  research workflow.
- Replay/backtest contracts exist, but the user does not have an event selector,
  monthly playhead, synchronized evidence panel, or clear result narrative.
- Operations details occupy too much attention for a normal research session.

## Reference patterns

MacroMicro presents cycle context and grouped economic indicators before
implementation details, and uses historical trajectories to make cycle movement
intuitive. Its public material also treats automatically updated charts as a
central exploration surface:

- https://www.macromicro.me/collections/22050/mm-exclusive
- https://www.macromicro.me/getting-started

Convex's public indicator dashboard pairs current readings, historical charts,
why-the-indicator-matters narratives, category navigation, and metric overlays:

- https://convextrade.com/indicators

The project should borrow these interaction patterns, not their proprietary
scores, data, branding, or allocation conclusions.

## Target information architecture

### 1. 景氣總覽

The first viewport answers only the highest-value questions:

- 目前 declared phase and phase age;
- legal next phase;
- continuation evidence state;
- transition watch and confirmation state;
- evidence completeness and latest data time;
- one concise reason summary and one missing-data warning.

Detailed provenance moves to drill-down, not the first screen.

### 2. 階段與轉折

Use four ordered phase tabs. Each phase shows book major groups, current
evidence, contradictory evidence, unavailable evidence, and the one legal next
transition. Watch and confirmation must use distinct visual lanes.

### 3. 指標學習庫

Every indicator detail page follows one reading sequence:

1. Chinese book-aligned name and one-sentence meaning;
2. why it matters in this phase or transition;
3. latest value, change, freshness, and release date;
4. how to interpret high, low, acceleration, reversal, or persistence;
5. YTD / 1Y / 5Y / Max interactive chart;
6. hover, touch, and keyboard date/value inspection;
7. recession-event shading and annotations;
8. revised versus vintage mode;
9. source, transformation, rule, and data-risk detail.

### 4. 歷史重播實驗室

The main control is an event selector plus a monthly playhead. Moving the
playhead updates available data, indicator evidence, transition state,
abstentions, and policy-template context for that month. Revised and strict PIT
views can be compared without silent fallback.

The Phase 119 artifact supplies 156 governed month-end input rows. It currently
supports full direct-series input for all 48 months covering 2018 late cycle and
COVID, while 108 earlier months remain explicit abstentions.

### 5. 資產配置研究

Show the book template associated with the declared phase, its rationale,
supporting indicators, alternatives, and historical behavior. Keep weights
labeled as book/research templates, not personalized live recommendations.

### 6. 資料與維運

Move source health, release calendar, refresh failures, provenance, Postgres
coverage, and backup status into a dedicated operations area. These remain
available without competing with the daily research workflow.

## Mobile behavior

- Use a bottom navigation or compact menu for the six primary surfaces.
- Keep the cycle command center first and charts full-width.
- Indicator tooltips must support touch and a pinned value state.
- Large tables become summaries with expandable rows.
- LAN HTTP displays a transport notice; remote use should prefer Tailscale HTTPS.

## Delivery roadmap

| Phase | Product delivery |
|---|---|
| 120 | Cycle command center and professional navigation shell |
| 121 | Indicator learning detail page, chart inspection, recession shading |
| 122 | Four-phase analysis and legal-transition evidence workspace |
| 123 | Declared-phase portfolio policy research and template comparison |
| 124 | Historical replay lab with event selector and monthly playhead |
| 125 | Understandable cash-flow-aware backtest UX and event attribution |
| 126 | Personal macro data catalog and extension API for future research tools |

Each phase must produce a visible product surface. Governance-only work is not
enough to raise the rebaselined production-readiness percentages.

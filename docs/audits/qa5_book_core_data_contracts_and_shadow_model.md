# QA5 Book-Core Indicator Data Contracts and Shadow Evidence Model

QA5 implements governance and shadow-only evidence plumbing for
`book_faithful_shadow_v2_alpha1`. It does not implement a formal decision
model, does not compute a candidate/current phase, and does not change
production v1 behavior.

## Scope

QA5 adds three audited layers:

- book-core data contracts for all 40 canonical indicator roles
- transformation contracts that avoid new weights and thresholds
- a feature-gated shadow evidence model that emits role evidence and phase
  evidence profiles only

The shadow evidence model is disabled from production paths. It does not read
external context priors, does not write `public`, does not write
`data/backtests`, and does not produce portfolio action.

## Count Semantics

QA5 reconciles four count systems that were easy to conflate:

- 98 canonical scope requirements from QA4
- 40 canonical book indicator roles requiring data contracts
- 38 existing repository indicators
- 54 indicator matrix rows after adding missing book-core roles

The current formal v1 indicator partition is mutually exclusive:

- retain as proposed v2 core: 8
- retain as proposed v2 supporting: 1
- retain as modern extension: 4
- exclude from v2 shadow scope: 0

## Data Contracts

Each canonical indicator role has exactly one data contract. Missing roles are
kept explicit rather than replaced by modern substitutes. Missing strict
evidence must abstain; it must not be zero-filled or silently fall back to
revised data.

Current QA5 contract status:

- canonical indicator roles: 40
- data contract rows: 40
- ready strict complete: 0
- ready strict partial: 15
- ready revised diagnostic: 9
- blocked roles: 16

Revised diagnostics are allowed only as diagnostics. They are not
point-in-time evidence and do not support validation, holdout, performance, or
book-alignment claims.

## Shadow Evidence Model

The shadow model computes role-level evidence and phase evidence profiles. It
does not compute:

- score-only candidate phase
- data-only current phase
- final phase decision
- decision status
- portfolio weights
- allocation
- trade signal

Synthetic fixtures are structural only. Real-date runs are diagnostics only and
must keep strict missing data as unavailable evidence.

## Candidate Freeze

QA5 freezes the shadow evidence architecture and its contracts, not decision
parameters. The freeze records hashes for:

- data contract registry
- transformation registry
- major group contract
- shadow model spec
- shadow source files

`book_faithful_shadow_v2_alpha1` has no registered candidate holdout and no
economic validation. Production migration remains disallowed.

## Remaining Blockers

Key unresolved book-core roles include growth saving/income/inflation roles and
boom confidence, government, inventory, and default roles. ADP employment also
requires an explicit data contract before it can be used.

QA6 should pre-register shadow aggregation rules and structural candidate model
validation before any decision-active candidate model freeze. Real backtest
progression and Phase 9B1 remain blocked.

---
version: "1.0"
status: active
created_at: "2026-06-27"
contract_path: specs/common/phase_execution_standing_contract.yaml
---

# Phase Execution Standing Contract

This standing contract collects rules that apply to every future phase unless a
prompt explicitly opens a narrower, documented exception. It reduces repeated
boilerplate while preserving the product doctrine, repository safety, and
legacy v1 boundary.

## Required Reading

Before planning or implementing any phase, read:

- `docs/project_north_star.md`
- `docs/investment_cycle_product_doctrine.md`
- `specs/common/investment_cycle_product_doctrine.yaml`
- `docs/phase_execution_standing_contract.md`
- `specs/common/phase_execution_standing_contract.yaml`

If a phase touches production v1 scoring, resolver, state machine, pipeline,
snapshot, Pages workflow, dashboard output, or phase wording, also read:

- `docs/legacy_production_v1_boundary.md`
- `specs/common/legacy_production_v1_boundary.yaml`

## Universal Start Checks

Every phase should begin with:

```bash
git status --short
git status --ignored --short
git branch --show-current
git remote -v
git rev-parse HEAD
git ls-files data/raw docs/景氣循環投資.pdf
```

The branch, expected parent commit, and clean working tree requirements come
from the phase prompt. `git ls-files data/raw docs/景氣循環投資.pdf` must remain
empty unless a later prompt explicitly authorizes tracked metadata; raw data
and the local book PDF must never be committed.

## Universal Product Doctrine Rules

- No standalone current phase classifier.
- No phase rank or phase winner as a product answer.
- No arbitrary phase score as a product answer.
- No isolated candidate phase classifier.
- Candidate phase means legal transition candidate only.
- Current phase means declared or governed state only.
- Phase evidence profile is explanation or transition input, not selector.
- Portfolio policy is a research template, not current allocation guidance.
- Historical replay/backtest must include transition timing and policy replay;
  it must not be only static-label accuracy.
- Legacy production v1 may remain as compatibility baseline, but must not be
  described as the mature product direction.

## Universal Safety Rules

- No secrets.
- No raw data commit.
- No book PDF commit.
- No `public`, `data/backtests`, or `data/prospective` output unless a prompt
  explicitly allows it and the output policy passes.
- No production behavior change without an explicit gate.
- No investment advice wording.
- No buy/sell/trade action or current allocation recommendation.
- No candidate/current phase output unless the prompt explicitly opens that
  gate.
- No live/FRED network dependency in tests.

## Universal Test Strategy

- Use targeted tests while implementing.
- Run full pytest only when runtime behavior changes or the final gate requires
  it.
- Run full ruff only when broad Python changes require it; otherwise run ruff
  on changed Python files.
- Docs/YAML-only phases should not run full pytest by default.
- Always run `git diff --check`.
- Run safety scans when docs, scripts, output policy, or wording changes.
- Live optional tests must be marked `live_optional` and must not run in
  default CI.

## Universal Final Report Fields

Every final report must include:

- `product_doctrine_alignment_status`
- `cycle_state_machine_alignment_status`
- `standalone_classifier_added_count`
- `phase_rank_or_score_added_count`
- `legal_transition_semantics_preserved`
- `portfolio_policy_research_alignment`
- `historical_replay_backtest_alignment`
- `deviation_cleanup_needed_count`
- `production_behavior_change_count`
- `semantic_drift_count`
- `raw_book_pdf_tracked_count`
- `tracked_data_raw_file_count`

Phase-specific prompts may add fields, but they should not repeat this full
contract unless a rule changes.

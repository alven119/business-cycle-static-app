# Agent Workflow / Self-Repair

## 為什麼需要 self-repair workflow

Phase 7F 系列已經形成固定節奏：candidate indicators、diagnostics、attribution、refinement、overlay、guardrails。這些階段不只是寫程式，還必須檢查 domain acceptance，例如 false positive 是否被降低、out-of-sample 是否穩定、caveats 是否保留。

因此 agent 不能只在第一次實作後回報結果。後續任務必須自行執行測試、讀 stdout 與 JSON output、比對 hard gates，必要時修正並重跑。

## Implement / Test / Domain Sanity / Repair Loop

每個 implementation task 都應遵守：

1. 實作使用者要求的最小變更。
2. 執行 pytest 與 ruff。
3. 執行該 phase 指定的 diagnostics / experiment / show command。
4. 讀取 stdout 與 JSON output。
5. 對照 `specs/backtests/phase_acceptance_gates.yaml` 與 prompt 內列出的 phase gates。
6. 若 hard gate 失敗，找 root cause、修正、重跑。
7. 重複直到 hard gates 全部通過，或遇到真正 blocker。

## Hard Gate vs Soft Warning

Hard gate 是完成條件，不通過就不能回報完成。例如 pytest fail、ruff fail、secret scan fail、baseline lookup warning 不為 0、expected_fail_count 不為 0。

Soft warning 是可接受的診斷訊號，但必須明確解釋。例如 diagnostics phase 的 mismatch_count 大於 0，可能正是該 phase 要揭露的問題；overlay phase 的 warning_count 大於 0，若 caveats 已說明外生衝擊或 watch density，通常可接受。

## 何時可以回報完成

只有在以下條件都成立時才能回報完成：

- pytest 通過。
- ruff 通過。
- secret scan 無洩漏。
- tracked generated-file scan 無輸出。
- phase hard gates 全部通過。
- soft warnings 已被分類並說明。

## 何時必須繼續修

若 hard gate 失敗，agent 必須繼續修，不應把第一次失敗結果交給使用者。常見例子：

- JSON output 欄位讀錯，導致 baseline status 全部是 `none`。
- output summary 與 phase acceptance target 不一致。
- generated data 被 tracked。
- secret scan 找到 FRED API key assignment pattern。
- experimental diagnostics 被接到 live dashboard 或正式 resolver。

## 何時才可以回報 blocked

只有在自動修復不安全或無法靠 repo 內資訊完成時，才可以回報 blocked。Blocked report 必須包含：

- failing hard gate。
- root cause hypothesis。
- 已檢查的檔案。
- 已嘗試的修正。
- 為什麼繼續自動修復不安全。

## Phase 7F 類任務常見 Domain Gates

- diagnostics point count 必須大於 0。
- missing score count 應為 0，除非該 phase 明確允許 missing local cache。
- refinement experiment 的 baseline lookup warning count 必須為 0。
- expected_fail_count 必須為 0，除非該 phase 是 attribution / planning 並明確允許 fail discovery。
- non-recession false positive 不應新增 confirmed recession 或 strong recovery。
- COVID / exogenous shock 必須保留 caveat。
- `watch` 不得被解讀為 confirmed recession 或 portfolio action。
- policy easing 不得單獨確認 recovery。

## 禁止事項

- 不得修改正式 `specs/indicator_catalog.yaml`，除非明確要求。
- 不得修改正式 phase scoring weights，除非明確要求。
- 不得修改 resolver / state machine live decision logic，除非明確要求。
- 不得修改 FRED provider 行為，除非明確要求。
- 不得把 experimental candidate indicators 接入 live dashboard，除非明確要求。
- 不得修改 GitHub Pages workflow，除非明確要求。
- 不得新增 LLM decision、database、chart、dashboard history page。
- 不得使用 `manual_review_required`。
- 不得產生投資建議或買賣建議。

## Secret / Generated Output 檢查

每個完成回報前至少執行：

```bash
git ls-files | grep -E '(__pycache__|\.pyc|\.pytest_cache|\.ruff_cache|\.mypy_cache|data/raw|data/backtests|public)'
grep -R "FRED_API_KEY" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ --exclude=".env" | grep "="
```

第一個 command 應無輸出。第二個 command 應無輸出。

## Caveat

本專案所有 backtest、diagnostics、overlay、guardrails 與 strategy-research output 都是模型診斷與研究材料，不構成投資建議。

## QA4 Scope-Governance Gates

QA4 tasks must preserve production defaults while defining formal scope. Agents
may add audit specs, scope contracts, documentation, and tests, but must not
change formal phase weights, thresholds, resolver behavior, dashboard behavior,
or production context handling.

QA4 completion requires the formal layer architecture, book-faithful scope
contract, indicator matrix, promotion gate, v1/v2 scope diff, and scope freeze
to pass. The expected closure keeps `book_faithful_scope_complete=false`,
`proposed_v2_implemented=false`, `proposed_v2_holdout_registered=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.

## QA5 Shadow Evidence Gates

QA5 tasks may add book-core data contracts, transformation contracts, shadow
evidence modules, audit specs, diagnostics scripts, and tests. Agents must not
change production resolver defaults, dashboard production behavior, scoring
weights, thresholds, or production context handling.

QA5 completion requires mutually exclusive scope count semantics, one data
contract per canonical indicator role, no silent substitution, no new weights
or thresholds, no formal candidate phase computation, no performance metrics,
no public or `data/backtests` output, and a valid shadow candidate freeze.

The expected closure keeps `formal_decision_model_ready=false`,
`production_book_fidelity_ready=false`,
`proposed_v2_economically_validated=false`, `holdout_registered=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA6.

## QA6 Shadow Aggregation Gates

QA6 tasks may add freeze-lineage audits, typed evidence contracts, layer routing
audits, aggregation schemas, structural eligibility checks, synthetic fixtures,
diagnostic CLIs, and aggregation architecture freezes. Agents must keep
candidate selection disabled and production isolated.

QA6 completion requires preserved freeze lineage, zero untyped roles, zero
numeric weights, zero new thresholds, zero historical-label rule selection,
passing synthetic structural fixtures, real-data diagnostics with candidate
phase disabled, reproducible aggregation freeze hashes, and production isolation
counts at zero.

The expected closure keeps `formal_decision_model_ready=false`,
`data_only_model_economically_validated=false`, `holdout_registered=false`,
`production_book_fidelity_ready=false`, `book_alignment_claim_allowed=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA7.

## QA7 Evidence Rule Gates

QA7 tasks may add evidence evaluability audits, book statement
operationalization registries, rule provenance contracts, role evaluation
contracts, evaluator metamorphic fixtures, synthetic candidate-selection
fixtures, real-data abstention diagnostics, leakage guards, candidate-selection
freeze artifacts, and production-isolation audits.

QA7 must not choose thresholds from historical outcomes, generalize contextual
book examples, emit real-data candidate phases, register holdout, or change
production resolver, state-machine, dashboard, weights, or thresholds.

QA7 completion requires all 40 roles to have classified evaluability reasons,
zero contextual-example generalization, zero arbitrary qualitative thresholds,
zero hidden defaults, passing synthetic candidate fixtures, real-data
candidate selection disabled, zero real-data candidate phase outputs,
reproducible alpha3 freeze hashes, and production isolation counts at zero.

The expected closure keeps `formal_decision_model_ready=false`,
`data_only_model_economically_validated=false`, `holdout_registered=false`,
`production_book_fidelity_ready=false`, `book_alignment_claim_allowed=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA8.

## QA8 Book-Explicit Evaluator Gates

QA8 tasks may add blocker-accounting reconciliation, book-explicit evaluator
eligibility audits, contextual numeric guards, shadow evaluator primitives,
implemented explicit evaluators, expanded metamorphic fixtures, retrospective
evidence diagnostics, a forward-only prospective diagnostic protocol, alpha4
freeze artifacts, leakage guards, and production-isolation audits.

QA8 must not choose lookbacks, persistence, or thresholds from historical
scenario outcomes, NBER dates, portfolio returns, or contextual examples. It
must not emit candidate phases on historical real data, inspect prospective
results, register holdout, or change production resolver, state-machine,
dashboard, weights, or thresholds.

QA8 completion requires mutually exclusive primary statuses, overlapping
secondary blockers documented, all operationally complete explicit rules
implemented, no contextual 250000 executable threshold, primitive guard counts
at zero, expanded metamorphic coverage, retrospective candidate selection
disabled, forward protocol registered-not-started, reproducible alpha4 freeze
hashes, leakage counts at zero, and production isolation counts at zero.

The expected closure keeps `formal_decision_model_ready=false`,
`data_only_model_economically_validated=false`, `holdout_registered=false`,
`production_book_fidelity_ready=false`, `book_alignment_claim_allowed=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA9.

## QA9 Prospective Registry Gates

QA9 tasks may add evaluator runtime wiring audits, runtime fixtures,
append-only prospective registry contracts, input snapshot manifests,
forward-only clock gates, protocol start semantics, protocol versioning,
inspection governance, registry fixtures, dry-run CLIs, monitoring
infrastructure freezes, and production-isolation audits.

QA9 must not write the first real prospective record, start the protocol,
backfill historical records, accept arbitrary real `as_of` overrides, inspect
real prospective evidence, emit candidate phases, create a scheduler, or change
production resolver, state-machine, dashboard, weights, or thresholds.

QA9 completion requires one implemented evaluator to be runtime-wired, zero
directional/candidate-eligible evaluators, valid append-only fixtures,
reproducible monitoring freeze hashes, registered/armed/not-started protocol
semantics, real record count zero, result inspection count zero, candidate
capability false, and production isolation counts at zero.

The expected closure keeps `formal_decision_model_ready=false`,
`economic_validation_status=not_started`, `holdout_registered=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA10.

## QA10 Runtime Readiness Gates

QA10 tasks may verify QA8/QA9 lineage, add dynamic history-window
materialization, runtime input snapshots, typed evidence records, idempotent
temporary append fixtures, pre-start preview and append CLIs, revision policy,
candidate-capability audits, scheduling audits, and production-isolation
checks.

QA10 must not write a real prospective record, start the protocol, inspect
prospective results, enable candidate phases, enable current phase decisions,
use revised fallback, add schedules, modify production resolver/state-machine
or dashboard behavior, tune thresholds or weights, or register holdout.

QA10 completion requires QA8 and QA9 closure lineage, one runtime output for
the 2019 revised diagnostic, legitimate strict temporal abstentions where
strict history is unavailable, no unexplained runtime abstention, deterministic
snapshot hashes, decision-field-free evidence records, idempotent append
behavior, correction lineage, pre-start write rejection, candidate capability
false, scheduling counts at zero, and production isolation counts at zero.

The expected closure keeps `formal_decision_model_ready=false`,
`data_only_model_economically_validated=false`, `holdout_registered=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA11.

## QA11 Forward Observation Gates

QA11 tasks may split monitoring-readiness semantics, add a 40-role forward
data-gap registry, define forward capture contracts, add observation-only
evaluators, generalize shadow history windows, validate role observation
records, audit major-group observation coverage, run retrospective observation
diagnostics, preview forward capture plans, and freeze alpha5 observation
runtime lineage.

QA11 must not write real prospective records, start the protocol, inspect
prospective results, emit candidate phases, convert raw observations into
phase support, tune thresholds or weights, add schedules, change production
resolver/state-machine/dashboard behavior, or register holdout.

QA11 completion requires all 40 roles to have forward status, runtime
observable role count greater than one, no arbitrary thresholds or persistence,
all implemented evaluators covered by runtime-window contracts, no candidate
eligible observation records, no modern substitution for missing core roles,
pre-start registry counts at zero, valid alpha5 freeze lineage, leakage counts
at zero, and production isolation counts at zero.

The expected closure keeps `formal_decision_model_ready=false`,
`data_only_model_economically_validated=false`, `holdout_registered=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The next allowed phase is QA12.

## QA12 Major-Group Manual Start Gates

QA12 tasks may reconcile major-group readiness semantics, audit leaf/derived
capture topology, inventory official source adapters, run no-write source
preflight, build the `2026-07` first-period manifest, add period-completeness
logic, build a preview bundle, add a manual-start gate and runbook, validate
tmp-path fixtures, freeze manual-start readiness, and verify production
isolation.

QA12 must not write a real prospective record, start the protocol, inspect
prospective results, enable candidate output, add schedules, move the
`2026-07` or `2026-08-31` protocol dates earlier, tune rules or thresholds, or
change production resolver/state-machine/dashboard behavior.

QA12 completion requires no readiness mislabels, no topology double counting,
no registry writes during preflight, a valid first-period manifest hash,
period-completeness error counts at zero, preview records without real IDs or
decision fields, no force bypass, valid manual-start freeze lineage, leakage
counts at zero, scheduling counts at zero, and production isolation counts at
zero.

The expected closure keeps `manual_start_allowed_now=false`,
`real_append_allowed_now=false`, `real_registry_record_count=0`,
`candidate_capability_ready=false`, `formal_decision_model_ready=false`,
`holdout_registered=false`, `real_backtest_progression_allowed=false`, and
`phase_9b1_allowed=false`. The recommended next action is
`WAIT_FOR_FIRST_ELIGIBLE_AS_OF`.

## Phase 10 Source Adapter Remediation Gates

Phase 10 is a development remediation track while the prospective monitoring
track keeps waiting for the first canonical eligible as-of. It may reconcile
the 16 QA11/QA12 forward-blocked book-core roles, verify official source
identity and economic equivalence, add shadow-only adapters and cache metadata,
define release semantics, run no-write preflight, refresh forward-capture and
observation-only readiness rollups, and freeze alpha6 lineage.

Phase 10 must not change the `2026-07` observation period, the `2026-08-31`
canonical as-of, the QA12 first-period manifest, the real prospective
registry, production resolver/state-machine/dashboard behavior, scoring
weights, thresholds, candidate selection, or live allocation outputs.

Phase 10 completion requires dynamic blocked-role reconciliation, 40/40 source
identity contracts, zero unresolved source identity, zero silent substitution,
all safely implementable adapters completed, no implementation failures,
genuine blocker evidence for remaining roles, valid alpha6 freeze lineage,
QA12 freeze unchanged, no prospective writes, no leakage, and production
isolation counts at zero.

The expected closure keeps `candidate_capability_ready=false`,
`candidate_monitoring_allowed=false`, `formal_decision_model_ready=false`,
`data_only_model_economically_validated=false`, `holdout_registered=false`,
`real_backtest_progression_allowed=false`, and `phase_9b1_allowed=false`.
The development next phase is `11`; the prospective track next action remains
`WAIT_FOR_FIRST_ELIGIBLE_AS_OF`.

## Project North Star Gates

Before planning or implementing any future phase, agents must read
`docs/project_north_star.md` and
`specs/common/project_north_star_contract.yaml`.

Phase 43A adds product doctrine files that future phases must also read:
`docs/investment_cycle_product_doctrine.md` and
`specs/common/investment_cycle_product_doctrine.yaml`. Each phase must declare
the product capabilities, milestones, and web surfaces it advances and must
keep the North Star semantic distinctions intact.

Common North Star hard gates are: document present, contract valid, phase
capability mapping complete, web-surface mapping complete, semantic drift
count zero, unsupported product claim count zero, no research output mislabeled
as production, no observation mislabeled as phase evidence, no watch mislabeled
as confirmation, no revised diagnostic mislabeled as point-in-time, and no
production behavior change without explicit approval.

## Investment Cycle Product Doctrine Gates

Future phases must preserve the Phase 43A doctrine amendment:

- the mature product is not a standalone current phase classifier;
- the legal cycle order is `recession -> recovery -> growth -> boom -> recession`;
- current phase handling should use a declared state plus legal transition
  monitoring;
- candidate phase, if used, must mean legal transition candidate, not isolated
  classifier winner;
- current evidence profile may explain support, contradiction, missing evidence,
  and abstention, but must not select the current phase before an explicit
  migration gate;
- historical validation should support transition timing, replay, and portfolio
  policy research, not only static-label accuracy.

Phase 43B adds doctrine-enforcement cleanup. Future phases must also preserve
`docs/legacy_production_v1_boundary.md` and
`specs/common/legacy_production_v1_boundary.yaml`: production v1 scoring,
resolver, pipeline, Pages workflow, and snapshot scripts are legacy baseline artifacts
until an explicit migration gate. They may be maintained for
compatibility, but their phase scores, ranked outputs, and resolver decisions
must not be described as the mature product answer.

Every future final report must include:

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

Phases that only add governance scaffolding are insufficient unless the prompt
explicitly frames the phase as cleanup, audit, or safety-blocker work.

Every future phase prompt should answer these doctrine checks before
implementation:

1. Which declared state, legal transition, evidence explanation, portfolio
   policy research template, historical replay/backtest, or dashboard education
   capability is being advanced?
2. Does any change add or depend on a standalone current phase classifier,
   phase rank/winner, arbitrary phase score, role-count selector, or isolated
   candidate classifier?
3. Are legacy v1 artifacts preserved only as baseline compatibility unless a
   migration gate is explicitly opened?
4. Are portfolio template weights treated as research assumptions rather than
   current allocation recommendations?

## Phase 11 North Star and Phase-Evidence Gates

Phase 11 may institutionalize the North Star, classify canonical roles,
exclude methodology requirements from indicator denominators, preregister
book-core evidence rules, implement all safely operationalizable phase-evidence
evaluators, add structural and metamorphic tests, build major-group evidence
profiles, run retrospective diagnostics, add shadow-only view-model contracts,
and freeze alpha7 lineage.

Phase 11 must not compute candidate or current phase, start prospective
monitoring, write real registry records, use historical labels or portfolio
returns for rules, add weights or arbitrary thresholds, route evidence to
resolver/state-machine/dashboard/portfolio, or change production behavior.

Phase 11 completion requires North Star gates passing, every economic role
represented in the evidence rule registry, methodology requirements excluded
from the indicator denominator, implemented phase-evidence evaluator count
greater than zero, new phase-evidence evaluable role count greater than zero,
partial phase-evidence major groups greater than zero, no candidate/current
phase emission, 2019 revised diagnostics with nonzero phase evidence, valid
alpha7 freeze lineage, QA12 freeze unchanged, no leakage, and production plus
prospective isolation counts at zero.

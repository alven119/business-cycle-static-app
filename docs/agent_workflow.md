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

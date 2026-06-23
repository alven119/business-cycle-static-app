---
version: "1.0"
status: active
approved_at: "2026-06-23"
contract_path: specs/common/project_north_star_contract.yaml
---

# 我的財務系統：產品北極星、最終能力與網頁呈現藍圖

- 文件版本：1.0
- 制定日期：2026-06-23
- 文件性質：長期產品目標、開發方向與介面呈現的最高層級契約
- 專案路徑：`docs/project_north_star.md`
- 專案依據：《景氣循環投資》、現有 repository contracts、QA0-QA12 治理成果，以及產品功能討論
- 目前狀態：本文件描述「最終應達成的能力」，不代表目前功能已完成或已通過經濟驗證

## 1. 產品北極星

本專案的最終目標，是建立一套可長期使用、可追溯、可解釋、具 point-in-time 意識的總體經濟研究網頁系統。系統應定期取得官方總體資料，判讀美國景氣循環所處的復甦、成長、榮景、衰退階段，偵測階段轉折風險，解釋所有判斷的資料與規則來源，並提供安全隔離的歷史重播、回測與 portfolio policy research。

系統不得將研究結果自動轉化為即時買賣建議、目標權重或交易訊號。任何正式輸出均必須揭露資料模式、完整度、模型版本、驗證狀態、限制與用途。

最終系統必須能回答：

1. 現在比較接近哪個景氣階段？
2. 哪些證據支持、反對或尚未具備？
3. 是否正在接近階段轉折？
4. 這是 observation、watch、confirmation，還是 formal phase？
5. 使用的是當時可取得的資料，還是後來修訂資料？
6. 模型為何判斷、為何 abstain？
7. 這項結果可以用於 diagnostics、回測、portfolio research，還是 production？
8. 這個模型版本是否已經過結構驗證、經濟驗證與前瞻驗證？

## 2. 不可違反的產品原則

### 2.1 客觀資料優先

景氣循環四階段依序為：`衰退 -> 復甦 -> 成長 -> 榮景 -> 衰退`。正常循環不得跳躍、逆行或略過。各階段長度與強度不可由日曆時間預設，必須由客觀資料與證據結構決定。

### 2.2 Book-core 與 modern extension 分離

書中明確要求的角色、現代擴充指標、工程安全規則與實驗性 evidence 必須分開標示。現代金融條件、殖利率曲線或信用利差可以提供 supporting／early-warning evidence，但不得靜默取代缺失的 book-core real-economy role。

### 2.3 嚴格分層

以下概念不得混用：

- raw observation != phase evidence
- phase evidence != transition watch
- watch != confirmation
- confirmation != formal phase
- candidate phase != current phase
- stage hint != phase decision
- portfolio research projection != current allocation recommendation
- structural validation != economic validation
- revised diagnostic != point-in-time result
- source contract ready != live source ready
- live source ready != period complete
- period complete != candidate capability ready
- portfolio research != investment recommendation

### 2.4 證據不足時 abstain

資料缺失、來源未驗證、release semantics 不完整、lookback 不足或規則尚未 preregister 時，系統必須 abstain。不得填零、縮小分母、使用 revised fallback、proxy fallback 或隱藏缺失。

### 2.5 Point-in-time 與資料血緣

所有歷史正式判斷都應盡可能只使用當時可取得的資料。每項結果都必須可追溯至 source agency／series／release artifact、reference period、release／availability date、vintage／revision、parser／adapter version、transformation、rule contract 與 model freeze。

### 2.6 Production 與 shadow 隔離

實驗性、shadow、research-only 功能不得自動進入 production catalog、resolver、dashboard、workflow、portfolio 或 public output。任何 migration 必須另有明確 gate。

### 2.7 安全輸出

研究工具不得自動輸出買進／賣出訊號、目標持股權重、即時配置建議，或保證、暗示未來績效的文字。回測與 policy 頁面必須標示 backtest-only、非未來績效保證、非投資建議。

## 3. 成熟版本的六大核心能力

### 3.1 景氣階段判讀能力

系統定期取得 FRED、ALFRED、BEA、BLS、DOL、Census、EIA 等官方資料，計算 level、YoY、moving average、slope、percentile、z-score 等轉換，並以書籍 major groups 與經過治理的 modern methodology 判斷復甦、成長、榮景與衰退。輸出必須包含 current phase、candidate phase、evidence completeness、confidence／uncertainty、major-group readiness、由證據結構推導的前段／中段／後段位置，以及 abstention reason。Weighted scoring 可以存在，但必須標記為 modern methodology，不得宣稱為書中明訂權重。

### 3.2 轉折風險偵測能力

系統應提供獨立於 formal phase 的 evidence lanes：榮景結束／late-cycle watch、衰退 watch 與 recession confirmation、recession trough／recovery watch、exogenous shock caveat。這些 evidence 只表示 watch、risk 或 confirmation，不直接改寫正式 phase，也不直接產生交易行動。

### 3.3 解釋能力

任何階段、watch、abstention 或回測結果都必須可解釋：哪些 major groups 支持或反對、哪些 roles／indicators 影響最大、哪些資料缺失、過期或只可 revised diagnostic、使用何種 transformation 與 rule、資料何時發布、是否 point-in-time、是否使用 external context、production v1 與 shadow v2 為何不同。

### 3.4 Portfolio policy research 能力

系統將書中的配置方法與 modern research templates 做成研究框架，而不是即時建議。至少支援被動全股票、股票／現金初階、股票／現金進階、股票／長天期美國公債初階、股票／長天期美國公債進階。書籍基準包括榮景期降低股票曝險，以及 70%／50%／30% 的進階模板。研究頁面必須區分書籍 benchmark 與 modern extension，不得把「衰退防守」等概括敘述冒充書中精確規則。

### 3.5 歷史重播與回測能力

系統應分成 revised diagnostic replay／backtest 與 strict point-in-time replay／backtest。前者用於程式除錯、結構比較、敏感度與 attribution，不得宣稱 point-in-time；後者只使用當時可取得資料，評估 phase timing、false signals、missed transitions 與 portfolio performance。正式回測需支援 total-return market data、初始投入與年度外部現金流、年度投入與年度再平衡、transaction cost、unitized NAV、cash-flow-aware returns、CAGR、波動率、最大回撤、Calmar、turnover、false signal cost 與 missed recovery cost。

### 3.6 安全輸出治理能力

系統必須具備 result output contract、metric formula registry、output location policy、caveat policy、safety validator、prohibited field／text validator、append-only prospective registry、model／data freeze lineage、no silent fallback、no auto-public output、no automatic allocation／trade signal。

## 4. 兩項基礎支撐能力

### 4.1 時間完整性與 abstention

必須支援 point-in-time data mode、release／revision semantics、strict vs revised 分離、missing evidence abstention、incomplete phase score 不進 formal resolver，以及 historical strict readiness 與 forward capture readiness 分離。

### 4.2 模型治理與前瞻驗證

必須支援 parameter inventory、parameter contamination disclosure、scenario exposure registry、model freeze／hash／lineage、preregistered validation protocol、no result peeking、append-only prospective observations，以及 model change resets future evaluation。

## 5. 產品能力 Milestones

Milestone 使用 `M0-M12`；QA 階段與 Codex execution Phase 不與這套編號混用。

| Milestone | 產品能力 | 目前精確狀態 |
|---|---|---|
| M0 | 專案骨架與官方資料基礎 | Python-first、provider、cache、catalog、CI/test 基礎完成；部分 book-core source adapters 待補 |
| M1 | 指標轉換與 scoring 基礎 | production v1 已具備；book-faithful shadow roles 多數仍為 observation/raw-only |
| M2 | 四階段景氣模型 | production v1 有基礎；book-faithful v2 formal evidence／decision 尚未完成 |
| M3 | 書籍指標對齊 | 40 roles、24 major groups 已盤點；來源、規則與 evidence 持續補齊 |
| M4 | Historical diagnostics／calibration | diagnostics 已有；calibration、validation 與 holdout 尚未完成 |
| M5 | Transition evidence | 7F experimental evidence／guardrails 已完成；尚未 formal integration |
| M6 | Evidence display contracts | 7G schema、fixtures、renderer contract 已完成；尚未正式 dashboard wiring |
| M7 | Portfolio policy research | 8A-8I contracts 已完成；policy engine 與經濟驗證未完成 |
| M8 | Real backtest contract stack | 9A contract stack 已完成；QA 補強 PIT、cash-flow、freeze 與治理 |
| M9 | Real backtest prototype | 9B 只屬 synthetic in-memory harness；真正歷史回測尚未開始 |
| M10 | Model calibration | 尚未正式開始；既有 scenarios 僅可作 development calibration |
| M11 | Dashboard integration | 尚未正式接線 |
| M12 | Automation／deployment／operations | 部分 workflow 基礎存在；完整來源監控、靜態頁與告警尚未整合 |

## 6. 後續 Execution Roadmap

Execution Phase 使用 `P10-P21`，與產品 Milestone 分開。

| Execution Phase | 主要工作 | 產出能力 |
|---|---|---|
| P10 | Book-core source／adapter remediation | 解決 blocked roles、官方來源與 release semantics |
| P11 | Phase-evidence evaluator implementation | observation 升級為可治理的復甦／成長／榮景／衰退 evidence |
| P12 | Shadow four-phase model | candidate selection、ambiguity、abstention、順向 state machine |
| P13 | Point-in-time historical replay | 每月 evidence／candidate／phase／transition 時間軸與 attribution |
| P14 | Real backtest prototype | development-only 的現金流感知策略回測 |
| P15 | Calibration and candidate freeze | thresholds／weights／false-signal cost 的 development calibration 與新版本 freeze |
| P16 | Book benchmark and portfolio policy engine | 五策略、年度投入／再平衡、股票／現金／長債政策 |
| P17 | Secular regime and shock overlay | 生產力／通膨長週期與外生衝擊分層 |
| P18 | Dashboard and explainability | 正式網頁整合、時間軸、drill-down、provenance |
| P19 | Prospective economic validation | freeze 後未見資料、無偷看結果的前瞻驗證 |
| P20 | Production migration | v1／v2 雙軌、context decoupling、rollback、正式 migration |
| P21 | Automation, deployment and operations | 定期更新、schema drift、source health、release checklist、長期維運 |

前瞻監控線有獨立日曆 gate；不得阻塞 P10-P18 的開發，也不得被這些 Phase 繞過。

## 7. 最終網頁資訊架構

建議左側主選單包含：總覽、景氣階段、轉折風險、指標總覽、歷史時間軸、歷史重播、長週期 Regime、Portfolio Research、回測研究、資料與血緣、前瞻監控、模型治理、系統維運。

所有分析頁面的全域控制列包含 As-of date、Data mode、Model、Model／freeze version、Date range、Frequency、View。所有頁面固定顯示 trust ribbon：資料最後更新時間、資料完整度、stale／missing 狀態、模型版本與 freeze、驗證狀態、formal／diagnostic／research-only 標籤、可用用途與禁止用途。

## 8. 各網頁頁面與可見資訊

### 8.1 首頁：景氣總覽

首頁必須立即回答目前接近哪個景氣階段、判斷完整度、移動方向、轉折風險、本月變化與資料可信度。核心卡片包含 current phase、candidate phase、evidence completeness、confidence／uncertainty、major groups ready／partial／missing、late-cycle／recession／recovery watches、data health、model／freeze／validation status。不得只顯示單一分數；若證據不完整，應顯示 partial 或 abstained。

### 8.2 景氣階段分析頁

可切換復甦、成長、榮景、衰退，查看 phase evidence profile、major groups、supportive／contradictory／mixed／unavailable、observation-only／phase-evidence／transition-evidence、current vs candidate、abstention reason。復甦至少依就業、消費、投資、進出口四組呈現；其他 phase 依各自書籍 major groups 呈現。

### 8.3 景氣時間軸

顯示四階段 evidence／score timeline、current phase 區間、candidate phase、transition watch／confirmation、abstention、data gaps、shock overlay、model version change points，並支援日期點擊、縮放、拖曳、production／shadow、revised／vintage_as_of 比較。

### 8.4 轉折風險頁

三條主要 lanes：Boom ending、Recession confirmation、Trough／recovery watch。每條 lane 顯示 evidence breadth、持續時間、缺失證據、false-positive guards 與 caveats。頁面固定說明：watch 不等於 phase、evidence 不等於 trade signal。

### 8.5 指標總覽與指標詳情

支援 phase／major group、formal／experimental、book-core／modern extension、observation／phase evidence／transition evidence、strict／revised／blocked、stale／missing、source agency 篩選。詳情頁顯示原始值、YoY、slope、MA、percentile、z-score、最新值與 evidence state、release／reference date、stale／missing、source、series ID、units、frequency、seasonal adjustment、transformation、rule、role、major group、書籍章節／頁碼與 modern extension 標籤、provenance 與 model version。

### 8.6 資料模式與血緣頁

支援 revised、exact vintage／vintage_as_of、official release archive、derived point-in-time，顯示 observation date、release date、vintage interval、artifact checksum、parser／adapter、transformation、freeze。

### 8.7 歷史重播頁

可選 Dotcom、GFC、COVID、Euro debt、2018 late cycle 或自訂期間，逐月播放當時可取得資料、role／group evidence、candidate／current phase、transition watch、abstention、revised vs point-in-time 差異。在 temporal gate 未通過前，只能標為 diagnostics。

### 8.8 回測研究頁

在回測 gate 通過後支援 production v1／frozen shadow v2／book benchmark、五種策略、起訖日期、投入、成本、再平衡、total return、CAGR、volatility、max drawdown、Calmar、turnover、false signal cost、missed recovery cost。頁首固定 caveats：backtest-only、非未來績效保證、非目前配置建議、非投資建議。

### 8.9 Portfolio Policy Research 頁

比較 passive all-stock、boom 50% template、boom 70／50／30 template、stock／cash、stock／long Treasury。顯示 policy schedule、rebalance rules、turnover、cost、drawdown 與書籍／modern 標籤。不得顯示即時買賣字樣。

### 8.10 生產力／通膨 Regime 頁

顯示 productivity-driven、inflation-driven、mixed／uncertain。此層影響長期 portfolio research，不得混入四階段 phase score。

### 8.11 Shock Overlay 頁

顯示 shock detected、normal-cycle phase、emergency watch、temporary shock state、normalization review 與 caveats。不得直接 override formal phase 或產生 portfolio action。

### 8.12 Production v1 vs Shadow v2 比較頁

比較 phase／candidate／decision status、context prior usage、completeness／abstention、book fidelity、model version／validation、差異來源與 attribution。

### 8.13 模型治理頁

顯示 model／freeze lineage、source hashes、parameter inventory、parameter contamination、scenario exposure、validation／holdout status、prospective protocol、migration status。

### 8.14 前瞻監控與 Registry 頁

正式啟動後顯示 observation period／canonical as-of、source release status、role／group completeness、typed observation／evidence／abstention／correction records、hash chain、model／evaluator freeze。管理操作只能是 preview、preflight、manifest、manual append 與 hash-chain validation；不得刪除、覆寫或回填。

### 8.15 系統維運頁

顯示 adapter health、last／next expected release、stale data、schema drift、cache checksum、parser version、source identity mismatch、CI／pytest／ruff、static build／deployment status。

## 9. 使用者角色與典型流程

一般研究使用者查看首頁 phase 與資料完整度、transition watches、major group 與 indicator 原因、data mode 與 caveats、portfolio research templates 與歷史脈絡。研究人員切換 vintage_as_of／revised、production／shadow 比較、historical replay、attribution、development backtest、freeze／provenance audit。管理者執行 source preflight、data update、cache validation、prospective preview、manual registry append、hash-chain validation、deployment checks。

## 10. 最終 Definition of Done

只有當下列能力都具備並通過相應 gate，才可視為成熟版本：官方資料來源與 adapters 可維運、book-core roles 與 major groups 有完整 contract、point-in-time 與 revised 模式明確、四階段模型可輸出 candidate／current phase 或 abstain、transition evidence 不與 formal phase 混用、所有輸出可解釋與追溯、historical replay 可用、書中五策略與 portfolio policy 可安全研究、strict backtest 可用且 cash-flow-aware、dashboard 完整接線、prospective registry append-only 且已前瞻驗證、production migration 有 rollback 與版本治理、automation／deployment／source health 可長期維運、任何研究結果都不會自動變成交易建議。

## 11. Repository Institutionalization Contract

本文件應於 Phase 11 正式加入 repository。後續 planning 或 implementation 前必須閱讀本文件與 `specs/common/project_north_star_contract.yaml`。任何 phase 必須映射至少一項 product capability，不得違反 mandatory semantic distinctions。所有 final report 必須包含 north star alignment、advanced capabilities、advanced web surfaces、deferred gaps、semantic drift count 與 production behavior change count。

Acceptance gates 至少包含：`north_star_document_present=true`、`north_star_contract_valid=true`、`phase_capability_mapping_complete=true`、`web_surface_mapping_complete=true`、`semantic_drift_count=0`、`user_visible_claim_without_readiness_gate_count=0`、`research_output_mislabeled_as_production_count=0`、`observation_mislabeled_as_phase_evidence_count=0`、`watch_mislabeled_as_confirmation_count=0`、`revised_mislabeled_as_point_in_time_count=0`、`production_behavior_change_without_approval_count=0`。

## 12. 下一個 Prompt 的固定 Work Package

Work Package 0 institutionalizes this North Star by adding this document, `specs/common/project_north_star_contract.yaml`, AGENTS/workflow/docs links, acceptance gates, and tests. It does not change production scoring, resolver, dashboard behavior, workflow, portfolio output, or data providers.

## 13. 日後查找與變更治理

本文件是產品方向的最高層級參考。技術規格可以演進，但不得與本文件的 semantic distinctions 衝突。若要修改北極星、六大核心能力、網頁資訊架構或 Definition of Done，必須明確提出變更原因、更新文件版本、更新 machine-readable contract、更新 tests 與 acceptance gates，並在 final report 列出 North Star change summary。不得在一般 Phase 中靜默改寫產品目標。

## 14. 書籍依據摘要

本文件採用的核心書籍原則包括：四階段順向循環，不跳躍、逆行或略過；各階段長度與強度不可預設，應讓客觀資料說話；復甦、成長、榮景、衰退有不同主要證據組合；榮景結束、衰退確認與落底反轉需要獨立觀察；生產力與通膨長週期應與一般四階段模型分層；投資規則與景氣階段判讀必須分層，不能讓配置規則反向決定景氣階段。頁碼與條文映射由 repository 的 canonical book requirement manifest 與 traceability registries 維護。

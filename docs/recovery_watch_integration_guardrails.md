# Recovery Watch Integration Guardrails

## 背景

Phase 7F3 建立了 recession trough / recovery candidate indicators，並在 7F3.3 加入 recession context gate 與 policy / financial support cap。Phase 7F3.4 將 refined diagnostics 轉成 experimental recovery watch rule，Phase 7F3.5 則把 rule 疊加到 full-horizon scenario timeline。

這份文件定義未來如何安全使用 recovery watch，避免把 experimental evidence 誤用成正式復甦確認、買進訊號或配置行動。

## Phase 7F3.5 Overlay 結論

Overlay 顯示 recovery watch 能在 dotcom、GFC 與 COVID 的 trough / recovery evidence 區域出現，且沒有在 euro debt slowdown 或 late-cycle 2018 形成 excessive recovery watch。

但 GFC 的 first recovery watch 比原始 recovery phase 早 18 個月，dotcom 早 9 個月，COVID watch density 偏高且需要外生衝擊 caveat。這代表 recovery watch 有研究價值，但不能直接接成正式模型決策。

## Recovery Watch 的價值

Recovery watch 可作為衰退後期與復甦初期的 evidence layer，用於回答「復甦證據是否開始形成」。它可輔助 dashboard diagnostics 或 future transition evidence research，但目前仍屬 experimental output。

## 不能等於正式復甦確認

Recovery watch 只代表 candidate evidence。正式復甦確認仍需正式 phase scoring、resolver persistence、confidence、recession context 與 broader model acceptance。Recovery watch 不得直接覆寫 current phase。

## 不能等於買進訊號

Recovery watch 不是買進訊號。GFC watch lead time 可達 18 個月，若直接觸發加碼，可能過早承擔 drawdown。任何 portfolio action 都必須等 Phase 8 / Phase 9 portfolio backtest 驗證 persistence、cooldown、risk control 與 allocation policy。

## Policy / Financial Cap

Policy easing 與 financial stress easing 可支持 recovery，但不得單獨確認 recovery。若缺少 labor reversal 或 real activity rebound，recovery watch / strong 應被 cap，避免把政策反應或金融壓力緩解誤判為真正復甦。

## Recession Context Gate

Recovery watch 必須保留 recession context gate。沒有近期 formal recession、recession candidate watch / confirmed，或 sufficient recession-depth evidence 時，最多只能作為 weak signal。這是避免 euro debt / 2018 non-recession false positive 的核心 guardrail。

## COVID Caveat

COVID 類外生衝擊後的快速反彈不等同一般景氣循環復甦。若 recovery watch 出現在 COVID shock 後，必須標記 caveat，且不能把它解讀為事前預測能力或一般循環規則。

## 未來可行整合模式

- `diagnostic_badge_only`：可安全作為低風險 diagnostics badge。
- `recovery_evidence_display`：可顯示「復甦證據形成中」，但不改 phase。
- `transition_evidence_input`：未來可研究作為 recession-to-recovery evidence input，但不直接改 resolver。
- `portfolio_policy_input`：可作為 Phase 8 / Phase 9 portfolio policy research input。
- `recovery_confirmation_trigger`：目前不允許。
- `buy_signal`：目前不允許。

## Live Integration 前 Guardrails

Live integration 前必須完成：

- recovery watch 不得直接成為正式復甦確認。
- recovery watch 不得直接觸發買進或加碼。
- 定義 persistence。
- 定義 cooldown。
- 保留 recession context gate。
- 保留 policy / financial support cap。
- COVID 類外生衝擊需標記 caveat。
- 任何 portfolio action 前必須完成 portfolio backtest。

## Phase 8 / Phase 9 關係

Recovery watch 可在 Phase 8 / Phase 9 中作為衰退後再加碼策略的 research input，但必須先經 portfolio backtest、風險控管、持續性與冷卻期設計。它不是目前的 live portfolio instruction。

## 下一步

下一步轉向 Phase 7G：cycle transition evidence architecture。Phase 7G 應整合 recession confirmation、boom ending watch、recovery watch 三類 evidence，定義哪些 evidence 只進 diagnostics，哪些可進 future transition risk，哪些可供 Phase 8 / Phase 9 portfolio policy research 使用。

## Caveats

- 使用修訂後歷史資料，不等同當時投資人可見資料。
- 此為 experimental overlay / integration guardrails，不代表正式模型已更新。
- recovery watch 不等於正式復甦確認。
- recovery watch 不是買進訊號。
- 不構成投資建議。

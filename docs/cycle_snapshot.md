# Cycle Snapshot

Phase 4B 建立 `cycle_snapshot.json`，把 indicator、phase 與 current phase decision 的既有輸出整合成 dashboard-ready data。這一步不重新計算分數、不重新 resolve current phase，也不建立 dashboard。

## 角色

`cycle_snapshot.json` 是後續靜態頁面或其他讀取端可以使用的單一資料入口。它整合：

- `data/derived/indicator_scores.json`
- `data/derived/phase_scores.json`
- `data/derived/current_phase_decision.json`

Snapshot 只做排序、摘要、warnings 與 failures 整理。

## Output JSON 結構

主要欄位：

- `generated_at`：產生 snapshot 的 UTC 時間。
- `as_of`：可選的資料日期。
- `current_phase_decision`：Phase 4A 的 current phase decision。
- `phase_scores`：Phase 3C 的 phase score results，依 phase order 或 phase id 排序。
- `indicator_scores`：Phase 2F 的 indicator score results，依 indicator id 排序。
- `summary`：常用摘要。
- `warnings`：資料或判斷品質提醒。
- `failures`：indicator 與 phase scoring failures。

## summary

`summary` 至少包含：

- `current_phase_id`
- `decision_status`
- `decision_confidence`
- `total_indicators`
- `scored_indicators`
- `failed_indicators`
- `total_phases`
- `scored_phases`
- `failed_phases`
- `blocked_phase_count`

## warnings

Warnings 用於提示讀取端不要過度解讀 snapshot，例如：

- current decision 是 `insufficient_evidence`
- indicator scoring 有 failure
- phase scoring 有 failure
- 有 blocked phase ids
- current phase decision confidence 偏低

Warnings 不是投資訊號，也不是人工審核欄位。

## failures

`failures` 分成：

- `indicator_failures`
- `phase_failures`

這讓 dashboard 或報表可以顯示哪些資料缺失或 scoring 失敗，而不會讓整批流程中斷。

## Dashboard-ready 但不是 Dashboard

Snapshot 的目標是讓未來 dashboard 有穩定資料格式可讀。Phase 4B 不新增前端框架、不產生 HTML dashboard，也不處理互動 UI。

## 不是投資建議

`cycle_snapshot.json` 只整理景氣指標、phase scores 與 state machine decision。它不包含資產配置、交易訊號或投資建議。

# Batch Phase Scoring

Phase 3C 建立 batch phase scoring output。它從 Phase 2F 的 `indicator_scores.json` 讀取 indicator-level results，從 `specs/phases` 載入 phase specs，輸出 phase-level scoring results。

## 角色

Batch phase scoring 負責批次計算每個 phase spec 的 `PhaseScoreResult`。它只輸出 phase scores，不選出 `current_phase`，也不做四階段最終判斷。

## 串接流程

1. `data/derived/indicator_scores.json` 提供 indicator-level `score` 與 `confidence`。
2. `specs/phases/*.yaml` 提供 phase spec、indicator weights、roles、confidence policy。
3. `score_phase_batch_safe()` 對每個 phase 呼叫 `score_phase()`。
4. `write_phase_scores_json()` 寫出 `data/derived/phase_scores.json`。

## phase_scores.json 結構

輸出包含：

- `summary.total_phases`
- `summary.scored_phases`
- `summary.failed_phases`
- `results`
- `failures`

每個 result 包含 phase score、confidence、available_weight、missing_indicators、contributing_indicators、stage_hint、reason_zh 與 details。

## Failure 不中斷整批

單一 phase spec 可能有設定錯誤或 scoring error。Batch scoring 會把錯誤記錄在 `failures`，讓其他 phase results 仍可輸出。

## available_weight / confidence / stage_hint

`available_weight` 表示 phase spec 中有可用 indicator score 的權重總和。

`confidence` 會受到 available_weight、indicator confidence、missing role penalty 影響。

`stage_hint` 只表示該 phase 內的 early/mid/late 位階提示，不是 `current_phase`。

## 為什麼 Phase 3C 仍然不是 current_phase 判斷

即使 phase scores 已可批次輸出，仍不能直接選最高分當作目前景氣階段。`current_phase` 需要 state machine、transition policy、persistence、資料覆蓋與 confidence 共同確認。

## 不可只因某 phase score 最高就判定景氣階段

某個 phase score 可能因缺資料、單一高分 indicator 或低 confidence 而不可靠。最終階段判斷必須等後續 state machine 與 transition rules 處理。


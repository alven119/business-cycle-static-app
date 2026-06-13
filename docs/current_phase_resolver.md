# Current Phase Resolver

Phase 4A 建立 deterministic current phase resolver。它可以根據 `phase_scores.json` 與 optional `previous_phase_id` 產生 `CurrentPhaseDecision`，但不做 dashboard，也不產生投資建議。

## 為什麼不能只取最高 phase score

景氣循環有順序與持續性。若只取最高 phase score，可能在資料噪音、缺值、單期修正或 phase signal 尚未確認時跳到不相鄰階段。

Resolver 會同時看：

- phase score
- phase confidence
- available_weight
- score margin
- previous_phase_id
- phase_order

## phase_order 的角色

狀態順序固定為：

```text
recession -> recovery -> growth -> boom -> recession
```

有 `previous_phase_id` 時，只能考慮目前 phase 與 allowed next phase。例如 previous 是 `recovery` 時，只能維持 `recovery` 或轉到 `growth`。即使 `recession` 分數很高，也會被放入 `blocked_phase_ids`，本階段不做 shock rule。

## previous_phase_id 的重要性

`previous_phase_id` 讓 resolver 知道目前狀態脈絡，避免任意跳躍。沒有 previous phase 時，只能做 `initial_estimate`，而且必須滿足分數、confidence、available_weight 與第二名分數差距門檻。

## decision_status

- `initial_estimate`：沒有 previous phase，但最高分達到初始估計門檻且與第二名差距足夠。
- `confirmed`：allowed next phase 的 score、confidence、available_weight 與相對目前 phase 的 margin 都達標。
- `transition_watch`：allowed next phase 有改善跡象，但 margin、confidence 或 available_weight 尚未同時達標，因此維持 previous phase。
- `hold_current`：目前 phase 仍較合理，或 allowed next phase 證據不足。
- `insufficient_evidence`：沒有足夠證據產生 current phase。

## blocked_phase_ids

`blocked_phase_ids` 表示分數可能很高，但因為不是 previous phase 的相鄰下一階段而被阻擋的 phases。這能避免例如 `recovery` 直接跳到 `recession`。

## Output JSON

`scripts/resolve_current_phase.py` 預設輸出到被 git ignore 的：

```text
data/derived/current_phase_decision.json
```

主要欄位：

- `current_phase_id`
- `current_phase_name_zh`
- `decision_status`
- `previous_phase_id`
- `candidate_phase_id`
- `candidate_score`
- `candidate_confidence`
- `current_score`
- `confidence`
- `allowed_next_phase_id`
- `blocked_phase_ids`
- `reason_zh`
- `details`

`details` 會包含 ranked phase scores、config、allowed next phase、blocked phases、score margin 與 evidence summary。

## 不是投資建議

Current phase resolver 只是一個景氣狀態判斷元件。它不產生資產配置、不產生交易訊號，也不是投資建議。

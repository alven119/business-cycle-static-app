# 景氣循環 State Machine

Phase 0D 建立最小可測版本的景氣循環 state machine。狀態順序固定為：

```text
recession -> recovery -> growth -> boom -> recession
```

## 核心規則

- 不允許任意跳階段。
- 不允許逆行。
- 只能維持目前階段，或往下一階段轉換。
- 轉換需要同時滿足 target phase score、confidence、available weight、persistence。
- evidence 混雜時保留 `current_phase`，並提高 `transition_radar`。
- 不使用 `manual_review` 作為輸出狀態；改輸出 confidence、reasons、missing data impact 與 transition watch。

## Policy Spec

共用規格位於 `specs/common/transition_policy.yaml`，定義：

- `cycle_order`
- `next_phase`
- default thresholds
- transition radar level
- 可測試規則描述

## Python Skeleton

最小實作位於 `src/business_cycle/phases/state_machine.py`。

主要資料結構：

- `TransitionThresholds`
- `PhaseEvidence`
- `PhaseDecision`

主要函式：

- `next_phase_for(phase)`
- `decide_phase_transition(evidence, thresholds=None)`

## Required Output Shape

`PhaseDecision` 會輸出：

- `current_phase`
- `current_substage`
- `phase_scores`
- `transition_radar`
- `confidence`
- `available_weight`
- `stale_indicators`
- `top_positive_reasons`
- `top_warning_reasons`
- `missing_data_impact`
- `transitioned`
- `blocked_reasons`
- `transition_watch`

## 下一步

後續 phase engine 應把前一次 phase snapshot 存成靜態檔，讓下一次執行能檢查 persistence 與 transition radar。Phase 0D 尚不實作檔案 I/O 或完整 scoring。

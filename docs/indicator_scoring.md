# Indicator Scoring

Phase 2B 建立單一總經指標的 scoring methods。這些方法只輸出單一 indicator 的 `score` 與 `confidence`，不產生 `current_phase`，不做 phase scoring，也不提供投資建議。

## Score 與 Confidence

`score` 是 0.0 到 100.0 的方向性分數，代表該指標對其設定方向的支持程度。高分不等於景氣階段結論，只代表單一指標訊號較強。

`confidence` 是 0.0 到 1.0 的資料信心，反映歷史長度、缺值、stale data、確認窗是否足夠。資料不足時可以有 score，但 confidence 必須下降。

## 為什麼不能只看最新值

總經資料有修正、缺值、短期噪音與發布落差。只看最新一筆資料容易把單月 spike、基期效果或暫時缺口誤判為趨勢。因此 scoring methods 都使用 trailing windows、moving average、percentile、YoY momentum 或 confirmation window。

## Methods

### level_percentile_score

用途：把目前水準放在歷史分布中比較。

適合：失業率、利率、信用利差、通膨、估值、油價或其他水準型指標。

方向：

- `higher_is_better`：分位數越高，score 越高。
- `lower_is_better`：分位數越低，score 越高。
- `neutral_midpoint`：越接近中位數，score 越高，極端高低都降低。

### moving_average_slope_score

用途：用移動平均斜率判斷趨勢方向，降低單期噪音。

適合：初領失業救濟金、失業率、房貸利率、工業生產、訂單、零售銷售。

方向：

- `rising_is_better`
- `falling_is_better`

單期 spike 不應形成高分，因為分數使用 moving average slope 與 confirmation window。

### yoy_momentum_score

用途：使用 YoY 或指定期數的 pct change，衡量成長率與成長動能變化。

適合：消費、投資、企業獲利、工業生產、進出口。

此方法特別適合需求與產出類指標，因為這些指標的景氣訊號通常來自成長率是否持續改善，而不是最新水準本身。

### peak_trough_reversal_score

用途：偵測落底回升或見頂轉弱。

適合：復甦/衰退轉折觀察，例如初領失業救濟金、耐久財新訂單、信用利差、油價或市場壓力指標。

模式：

- `trough_recovery`：低點後連續改善才確認。
- `peak_rollover`：高點後連續轉弱才確認。

此方法必須使用 `confirmation_window`。單一 observation 不可直接確認反轉。

## 資料不足與 Stale Data

資料不足時，方法會降低 confidence，通常回到接近中性分數。缺值不會被靜默忽略；缺值比例會降低 confidence。若資料超過 `stale_after_days`，score 可保留作為歷史計算結果，但 confidence 會下降。

## 為什麼 Phase Scoring 前要先有 Indicator Scoring

Phase scoring 需要整合多個指標、權重、coverage、confidence 與 persistence。若沒有先把每個 indicator 轉成可比較的 score/confidence，phase engine 容易被單一最新值、單一指標或缺值資料誤導。


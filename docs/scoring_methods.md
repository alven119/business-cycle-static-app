# 趨勢評分方法

本文件說明 `specs/common/scoring_methods.yaml` 中的 scoring method 規格。這些方法只定義評分設計，不實作資料下載，也不直接判斷景氣階段。

## 共同原則

- 不可以只看最新一筆資料。
- 趨勢至少要使用 3M、6M、12M，或依週、季資料頻率調整的等效觀察窗。
- 單月或單期 spike 不得直接造成景氣階段轉換。
- 每個 score 都必須輸出 `confidence`。
- missing、stale、insufficient history 必須明確降低 confidence，不能被靜默忽略。

## level_percentile_score

用途：把目前水準放到歷史分布中比較，判斷目前值偏高、偏低或接近中性。

適合指標：失業率、利率、信用利差、通膨、估值、油價或原物料價格。

重點：此方法不是看最新值是否超過單一門檻，而是比較 rolling historical percentile。若方向是 `lower_is_stronger`，高分位可能是負面；若方向是 `higher_is_stronger`，高分位可能是正面。對油價、長端利率等指標，極端高分位可能反而是 warning。

## moving_average_slope_score

用途：用移動平均斜率判斷趨勢方向，降低單期噪音。

適合指標：初領失業救濟金、短期失業人數、失業率、房貸利率、生產類序列。

重點：週資料可用 4W/13W，月資料可用 3M/6M/12M，季資料可用 2Q/4Q。單期 spike 不能直接改變結論，必須通過移動平均與確認窗。

## yoy_momentum_score

用途：衡量年增率與年增率動能，觀察需求、生產、訂單或盈利是否改善。

適合指標：實質零售銷售、個人耐久財消費、耐久財新訂單、私人固定投資、進出口、企業盈利。

重點：月資料至少要有 12M 歷史才能算 YoY，季資料至少要有 4Q。復甦判斷應看 YoY 是否從低點持續改善，而不是單月年增率跳升。

## peak_trough_reversal_score

用途：偵測序列是否從高點或低點反轉，並確認反轉是否持續。

適合指標：初領失業救濟金、耐久財新訂單、衰退與復甦轉折訊號、信用壓力、油價或部分原物料價格。

重點：反轉需要平滑、幅度與持續性。單月反彈或單週回落不可被當成正式轉折。

## diffusion_score

用途：衡量同一群組中有多少指標支持同一景氣階段，避免單一指標主導。

適合指標群組：勞動市場、需求、投資、貿易、金融條件。

重點：此方法使用 indicator score、confidence 與 weight。若正向訊號只集中在單一指標，最高分必須受限。missing 或 stale constituent 會降低 available weight 與 confidence。

## persistence_confirmed_score

用途：要求條件連續成立多期後才提高分數，避免短期噪音造成錯誤轉換。

適合指標與規則：失業率確認、景氣階段轉換確認、政策利率轉向、趨勢破壞或趨勢修復確認。

重點：月資料常用 3M confirmation，週資料常用 4W 到 13W，季資料常用 2Q。missing 或 stale 不能視為條件成立。若確認窗未滿，score 應維持中性或低信心，而不是提前轉換階段。

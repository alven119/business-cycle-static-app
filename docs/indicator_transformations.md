# Indicator Transformations

Phase 2A 建立總經指標趨勢判讀的基礎 time-series transformations。這些函式只處理指標序列，不產生 `current_phase`，不做投資建議，也不取代後續 scoring engine。

## 共同原則

- 不可以只看最新一筆資料判斷趨勢。
- 週、月、季資料都應使用符合頻率的觀察窗。
- 所有 rolling transformation 只使用當期與過去資料，不使用未來資料。
- 資料不足、缺值或標準差為 0 時輸出 `NaN`，避免產生假的趨勢訊號。
- 單期 spike 可以被 transformation 顯示出來，但不得被解讀為持續趨勢。

## clean_observations

用途：清理原始觀測值，解析日期、將 value 轉成 numeric、移除無法解析日期的 rows，並依日期排序。

適合所有資料源輸入，尤其是 FRED CSV/API 取回後的第一步。FRED 常用 `.` 表示缺值，會被轉成 `NaN` 並保留下來，讓後續步驟明確處理。

## add_moving_average

用途：計算 trailing moving average，降低單期雜訊。

適合：

- 就業：初領失業救濟金、短期失業人數、失業率
- 消費：實質零售銷售、耐久財消費
- 投資：耐久財新訂單、固定投資
- 房地產：房貸利率、住宅相關序列

週資料可用 4W 或 13W，月資料可用 3M、6M、12M，季資料可用 2Q 或 4Q。

## add_pct_change

用途：計算 MoM、QoQ、YoY 等百分比變化。

適合：

- 消費：零售銷售、PCE
- 投資：耐久財訂單、私人固定投資
- 通膨：CPI、PCE price index
- 股市與估值：盈利、指數或估值序列的變化率
- 房地產：房價、住宅銷售量

月資料常用 1M 或 12M，季資料常用 1Q 或 4Q。資料不足時不應補出變化率。

## add_rolling_slope

用途：用 rolling window 估計線性斜率，判斷趨勢方向。

適合：

- 就業：失業率是否持續上升或下降
- 消費：需求是否持續改善
- 投資：訂單或固定投資是否回升
- 利率：短端、長端、房貸利率趨勢
- 信用利差：壓力是否擴大或收斂

斜率只代表 window 內趨勢，不能單獨產生景氣階段轉換。單期 spike 若沒有持續，應在後續 window 中被抵消或反轉。

## add_rolling_zscore

用途：衡量目前值相對 rolling mean 的標準化偏離。

適合：

- 通膨：價格壓力是否異常
- 利率：利率是否偏離近期常態
- 信用利差：壓力是否異常擴大
- 股市與估值：估值或市場壓力是否偏極端
- 原物料：油價或商品價格是否異常偏離

當 rolling std 為 0 時輸出 `NaN`，避免除以 0 後產生誤導訊號。

## add_rolling_percentile

用途：計算目前值在 trailing rolling window 中的 percentile，範圍為 0.0 到 1.0。

適合：

- 失業率、通膨、利率、信用利差等水準型指標
- 股市與估值的歷史分位比較
- 房地產估值或融資成本分位比較

高 percentile 不一定代表正向，需搭配 indicator direction。例如失業率或信用利差高分位通常偏負面，但零售銷售高分位可能偏正面。

## detect_peak_trough

用途：偵測 trailing lookback window 內目前值是否為 local peak 或 local trough。

適合：

- 就業：初領失業救濟金是否從高點回落
- 消費與投資：需求是否從低點回升
- 信用利差：壓力是否見頂
- 股市與估值：市場或估值是否形成近期高低點
- 房地產：房貸利率或住宅需求是否出現近期轉折

此函式不使用未來資料，因此是即時判讀可用的基礎轉折偵測。真正的 peak/trough reversal 仍需要後續 confirmation window，不能只靠單期 local peak 或 trough。


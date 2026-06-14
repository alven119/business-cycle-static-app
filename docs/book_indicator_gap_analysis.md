# Book-Aligned Indicator Gap Analysis

Phase 7D 建立《景氣循環投資》語意下的指標缺口分析，但不修改 scoring、phase resolver、FRED provider 或 live dashboard。

Machine-readable spec：

```text
specs/backtests/book_indicator_gap_analysis.yaml
```

查看摘要：

```bash
python scripts/show_book_indicator_gap.py
```

## 為什麼不直接改 threshold

Phase 7C.2 的 full-horizon diagnostics 顯示 transition controls 對 dotcom、金融海嘯、歐債疑慮與 2018 late-cycle 壓力有改善或穩定效果，但 COVID scenario 仍在 2019-02-28 出現 too-early confirmed recession。

這比較像指標覆蓋與確認邏輯不足，而不是單純 threshold 太鬆。若直接調 threshold，可能讓 dotcom 或金融海嘯這類真正衰退案例變得太晚確認，也可能針對 COVID 單一案例 overfit。

因此 Phase 7D 先整理 gap：哪些書中觀察主軸尚未工程化、哪些 MVP 指標太敏感、哪些確認邏輯應先以 breadth 或 confirmation 方式實驗。

## 目前 MVP 指標

目前已工程化的核心指標包括：

- 就業：初領失業救濟金人數、短期失業人數、失業率。
- 消費：實質零售銷售、個人耐久財消費支出。
- 投資：製造業耐久財新訂單、實質民間固定資本投資。
- 進出口：進口金額、出口金額。
- 利率與金融條件：聯邦基金利率、美國 10 年期公債殖利率、美國 30 年房屋抵押貸款平均利率。
- 原物料：西德州原油價格。

這些足以支撐 MVP dashboard 與初版 backtest diagnostics，但尚未完整覆蓋榮景期結束、衰退確認與衰退落底反轉。

## 榮景期結束缺口

榮景期結束不是單純確認經濟仍強，而是觀察過熱後是否接近轉折。現有模型已有利率、油價與部分就業資料，但仍缺少：

- yield curve spread，例如 10Y-3M。
- corporate credit spread。
- financial conditions index。
- CPI / inflation pressure。
- ISM new orders 或類似領先訂單。
- housing starts。
- valuation pressure 類資料。

這些候選指標可補足過熱、升息、信用壓力與需求轉弱的觀察面向。

## 衰退確認缺口

COVID 2019 early false recession 顯示，衰退確認不應只由少數高敏感指標推動。下一步應優先檢查：

- 就業惡化 breadth。
- 初領失業救濟金是否持續升高，而非單期波動。
- 失業率與短期失業人數是否同步惡化。
- 消費是否廣泛惡化，不只耐久財。
- 投資與訂單是否同步惡化。
- credit / financial stress 是否惡化。
- yield curve / rate cut cycle 是否確認轉向。

這些方向較適合作為 recession-specific breadth confirmation，而不是直接改現有 threshold。

## 衰退落底反轉缺口

衰退落底與復甦初期需要確認高峰反轉與需求修復。目前已有部分指標，但仍需把下列訊號工程化：

- initial jobless claims peak reversal。
- short-term unemployment peak reversal。
- retail sales / durable goods bottoming。
- durable goods orders bottoming。
- exports / imports bottoming。
- monetary easing already in place。

這些規則有助於 state machine 判斷從衰退轉復甦，而不只是在衰退確認上變得更保守。

## 高敏感指標

Phase 7C.2 COVID attribution 顯示以下指標需要先做診斷與 breadth confirmation：

- `short_term_unemployment`
- `real_pce_durable_goods`
- `initial_jobless_claims`
- `real_retail_sales`

Phase 7D 不把這些問題直接視為 scoring bug。它們是重要指標，但需要搭配持續性、群組共振與書中衰退確認指標，避免短期波動造成 early false recession。

## 後續建議

- Phase 7E：實作 recession-specific breadth confirmation，仍放在 feature flags 後面。
- Phase 7F：實作 book-aligned recession / recovery indicators。
- Phase 8A：建立 portfolio policy spec，讓模型判讀與投資政策分層。

本分析使用 revised data，不等同當時投資人可見資料。所有內容僅用於模型診斷與研究，不構成投資建議。

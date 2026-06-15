# Book-Aligned Indicator Implementation Plan

Phase 7F 建立書籍方法論對齊指標的實作計畫，但不修改 scoring、phase resolver、FRED provider 或 live dashboard。

Machine-readable spec：

```text
specs/backtests/book_aligned_indicator_implementation_plan.yaml
```

查看摘要：

```bash
python scripts/show_book_indicator_plan.py
```

## 為什麼不再硬調 breadth rule

Phase 7E.1 的 breadth sensitivity 顯示，單靠 recession breadth rule 無法同時滿足所有 acceptance targets。較嚴格的 `v4_core_plus_financial` / `v6_strict_core` 可以擋掉 COVID 2019 early false recession，但會漏掉 dotcom 與金融海嘯的 recession detection；較寬鬆的 `v2_current_breadth` / `v3_core_required` / `v5_no_trade_as_core` 可以保留 dotcom 與金融海嘯，卻擋不掉 COVID 2019 false positive。

這代表問題不只是 breadth rule 太鬆或太嚴，而是 MVP 指標覆蓋仍不足。繼續硬調 breadth 容易在單一歷史案例上 overfit。

## 為什麼要補書籍方法論指標

目前 MVP 指標已涵蓋就業、消費、投資、進出口、利率與原物料，但對三個關鍵環節仍不夠完整：

- 衰退確認：需要更多就業廣度、廣義消費、投資訂單、信用壓力與金融條件確認。
- 榮景結束：需要更完整的利率曲線、信用利差、金融壓力、油價壓力與生產/訂單轉弱訊號。
- 衰退落底：需要高峰反轉、政策寬鬆已到位、信用壓力緩和與需求止跌訊號。

Phase 7F 先定義候選指標與驗收方法，後續才分批工程化。

## 實作批次

Phase 7F1：衰退確認指標

- 續領失業救濟金人數。
- 投保失業率。
- 失業 15 週以上人數。
- 實質個人消費支出。
- 金融壓力指數。
- 信用利差。

Phase 7F2：榮景期結束指標

- 10Y-3M 與 10Y-2Y yield curve。
- Baa-Aaa 信用利差。
- 工業生產。
- 耐久財訂單精煉訊號。
- 油價壓力。
- Fed 政策反轉訊號。

Phase 7F3：衰退落底與復甦反轉指標

- 初領失業救濟金高峰反轉。
- 短期失業人數高峰反轉。
- 消費與耐久財落底。
- 訂單落底。
- 寬鬆政策已到位。
- 信用壓力緩和。

## 驗收方式

後續實作不得只看單一 scenario。至少要用既有 backtest / calibration review 檢查：

- COVID 2019 early false recession 應降低，或至少降為 transition_watch。
- dotcom 與 GFC 仍需在合理 recession window 內偵測。
- euro debt slowdown 與 late cycle 2018 不應新增 confirmed recession。
- 新指標必須保留中文 reason、資料 freshness、confidence 與 phase impact。

本計畫使用 revised data 作為第一版診斷基礎，不等同當時投資人可見資料。所有內容僅供模型校準與總經研究，不構成投資建議。

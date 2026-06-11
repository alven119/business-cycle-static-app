# 復甦期 Spec 說明

`specs/phases/recovery.yaml` 將復甦期定義為「從衰退後谷底轉向擴張」的階段。判斷重點不是單一最新數值，而是多個群組的趨勢、反轉、持續性與資料信心。

## 核心觀察

- 勞動市場早期訊號：初領失業救濟金與短期失業人數需要持續下降，代表裁員壓力緩和。
- 失業率：只作為落後確認，不可成為復甦初期唯一判斷。
- 消費：實質零售銷售與個人耐久財消費需看到年增率或三個月動能改善。
- 投資：耐久財新訂單與私人固定投資用來確認復甦是否擴散到企業與住宅投資。
- 進出口：進口反映內需與補庫存，出口反映外需支撐。
- 利率與金融條件：聯邦基金利率、10年期公債殖利率、30年房貸利率用來判斷金融環境是否支撐復甦。
- 油價或原物料 proxy：溫和回升可能伴隨需求改善，快速上升則可能是成本壓力。

## 可測試規則

Recovery spec 要求至少兩個核心群組改善，且必須包含：

- `labor_leading`
- `demand`

從 `recession` 轉向 `recovery` 時，還需要：

- recovery score 達到門檻
- 指標覆蓋率達標
- 資料信心達標
- evidence 持續至少 `3m`
- 單月或單週尖峰通過 `confirmation_window`

## FRED mapping 狀態

`specs/indicator_catalog.yaml` 中的 FRED series 均標為 `candidate_unverified_for_project`。這表示 series ID 來自候選 mapping，但尚未在本專案內完成下載、歷史長度、缺漏、stale、修正與頻率相容性檢查。

Phase 0C 不實作下載、不硬編假資料，也不產生 phase classification。

## 下一步

1. 建立 YAML schema validation，檢查 indicator 必填欄位與 phase weights。
2. 實作 FRED metadata/download 驗證，但 API key 只能讀取環境變數。
3. 為每個 `score_method` 加入 trend-aware 測試案例。
4. 實作 phase engine 的 coverage、confidence、persistence 與 transition radar。

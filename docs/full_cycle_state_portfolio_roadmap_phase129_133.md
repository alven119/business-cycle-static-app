# Phase 129–133：全循環狀態、資料、Dashboard 與配置研究路線

本文件是 Phase 128 之後的 active engineering roadmap。它將使用者旅程固定為：

`觀察 → 理解 → 確認 → Dashboard 換檔 → 學習 → 歷史配置研究`

五個 Phase 的順序不可顛倒。Phase 127 prospective calendar gate 繼續平行等待，
不得被 Phase 129–133 的工程進展取代。

## 一、UX 連貫性原則

### 永遠可見的研究脈絡

所有核心頁面固定顯示：declared phase、phase start 或日期區間、phase age 狀態、
legal next phase、最新資料日期、data mode、完整度與來源風險。使用者不應在不同頁面
看到互相矛盾的景氣階段或資料日期。

### 轉折確認不是一顆沒有脈絡的按鈕

確認流程固定為五步：

1. 檢閱支持、反對、缺失、watch 與 confirmation evidence。
2. 輸入下一階段生效日或合理日期區間。
3. 預覽切換前後的 declared state、legal next phase、Dashboard 研究位置與配置模板。
4. 明確確認，不允許 latest data 自動替使用者切換階段。
5. 顯示 append-only receipt；rollback 以 correction 記錄完成，不刪除歷史。

### Dashboard 必須原子換檔

使用者確認後，首頁、轉折雷達、優先指標、教育說明與配置研究 context 必須從同一
active registry 一致切換。不可出現首頁已是衰退、指標頁仍在解釋榮景的半套狀態。
舊階段仍可由歷史入口查看，但不再占據首頁主要位置。

### 狀態語言固定

- observation：只有資料現象。
- watch：值得提前注意，尚未確認。
- confirmation：規則所需證據已達成，但不等於交易動作。
- operator-confirmed declared state：使用者完成受治理確認後的研究位置。
- blocked／abstained：必須說明缺什麼、影響什麼、接下來怎麼補。

### 指標頁必須回答「為什麼現在重要」

每個 priority indicator 除了數值與圖表，還要顯示：目前階段中的意義、數值高低代表
什麼、近期方向、是否支持 watch／confirmation、資料時間、來源風險與缺漏影響。

### 配置研究避免事後最佳化誤解

歷史頁並列「書籍規則回放」與「固定權重敏感度」。書籍模板權重是政策狀態，不是造成
市場轉折的原因；歷史績效最好的固定權重也不是未來建議。

## 二、Phase 執行路線

### Phase 129：受治理景氣階段轉換確認

狀態：已完成。受治理 transition core、preview、receipt 與 correction rollback 已就緒；
live transition activation 依原路線保持關閉，待 Phase 132 完成 Dashboard phase context 原子切換後啟用。

完成 private transition review、合法下一階段、起始日／日期區間、before/after preview、
append-only confirmation receipt 與 correction rollback。先完成目前 boom start 的無假精度
確認，再允許未來 `boom → recession`。

### Phase 130：四階段 revised/current 資料倉儲

狀態：已完成。26 個 canonical raw inputs 與 1 個明示風險的 supporting series 已納入每日 revised
排程；37 個經濟角色可由 PostgreSQL 重建，ADP／Conference Board confidence 保持 blocked，
PAYEMS／UMCSENT 只作旁證。

完成 role-series-transformation-phase-lane 矩陣、PostgreSQL current/revised inputs、derived
lineage、來源排程、重試與 schema drift。ADP 與 Conference Board confidence 保留 proxy
及授權風險，不得把 PAYEMS 或 UMich sentiment 冒充原 role。

### Phase 131：歷史 PIT 與轉折事件

狀態：已完成。五個情境均有明確 PIT 狀態；COVID 與 2018–2019 為 strict complete，
網路泡沫、GFC、歐債危機保留 uncertainty window。七條早期官方缺口已逐一登錄來源、
可重現性與 blocker，不以目前修訂表或固定 lag 冒充當時 vintage。

完成 scenario window、shock、uncertainty window 與 strict evidence-derived watch／confirmation
事件契約及 provenance。revised comparison 與 strict PIT 在歷史重播頁視覺分離，歷史 label
不回饋 runtime tuning，也不改寫 declared state。

### Phase 132：Phase-aware Dashboard 原子切換

狀態：已完成。四種 synthetic declared states 均可從同一 active registry context hash 原子重建
overview、radar、priority indicators、learning copy、portfolio context 與 mobile ribbon。Boom 使用
既有 live evaluator；recession／recovery／growth 在 evaluator 尚未 operationalize 時明確顯示
input-readiness-only abstention，不會誤套 boom 規則。

Transition activation gate 已開啟，但仍須完成 Phase 129 的受治理 preview、證據確認與 operator
confirmation；資料不會自動切換 declared state。確認後無需重新部署，所有核心研究頁同步換檔。

### Phase 133：歷史政策時間軸與固定權重敏感度

五個案例逐月標記 phase、phase age、watch、confirmation、shock 與書籍模板權重；平行比較
100/70/50/30、股票／現金與股票／長債，顯示 drawdown、恢復時間、turnover、成本、錯失復甦
與錯誤去風險代價。不得挑事後最佳結果作為目前配置指令。

## 三、最容易造成困惑的情況與處理

| 可能困惑 | UX 處理 |
|---|---|
| watch 已亮燈，為什麼還沒換階段？ | 顯示 why-not-confirmation 與缺少的必要證據。 |
| confirmation 已成立，為什麼系統沒自動切換？ | 顯示「等待使用者受治理確認」，提供 review 入口。 |
| 切換後為什麼 legal next phase 變了？ | confirmation receipt 顯示 before/after cycle order。 |
| 起始日不確定怎麼辦？ | 允許 bounded date window，phase age 顯示區間而非假精確值。 |
| proxy 有數值，為什麼 role 仍 blocked？ | 顯示 supporting-only 與 substitution risk。 |
| revised 與 PIT 圖為何不同？ | data-mode badge、release/vintage provenance 與差異說明常駐。 |
| 歷史案例 50% 表示 50% 時市場會轉折？ | 明示這是書籍 policy state，不是轉折原因。 |
| 回測最好權重是否就是現在應使用的配置？ | 明示 sensitivity research，不提供 personalized action。 |

## 四、完成邊界

Phase 133 完成後，景氣判讀、轉折雷達、配置研究與歷史 replay 的工程產品面可達 100%。
F2 prospective validation 仍維持 calendar-gated；只有累積 12 個完整月份、12 個 strict dates
並完成獨立驗證後，才可達正式 production 100%。

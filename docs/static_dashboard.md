# Static Dashboard

Phase 5A 建立最小靜態 dashboard generator。它讀取 `data/derived/cycle_snapshot.json`，產生本機可瀏覽的 `public/index.html` 與 `public/data/cycle_snapshot.json`。

## 角色

Static dashboard 是 `cycle_snapshot.json` 的可讀化輸出。它呈現：

- current phase decision
- four phase scores
- indicator scores
- warnings
- pipeline failures

它不重新計算 indicator score、不重新計算 phase score，也不重新 resolve current phase。

Dashboard 預設語言是 zh-TW / Traditional Chinese。主要顯示名稱會使用 `specs/common/display_labels_zh.yaml`，對齊《景氣循環投資》常用語：

- 復甦期
- 成長期
- 榮景期
- 衰退期

Technical ids 仍會保留在小字欄位，方便 debug、對照 JSON 與測試。

## Current Cycle Context

`specs/common/current_cycle_context.yaml` 提供 resolver 的 previous-phase baseline/context。現階段預設為「榮景期第一年剛結束」，來源是使用者提供的作者近期敘述。

這不是把模型結論硬寫死，也不是 manual review。Pipeline 會把它當作 state machine 的前一階段脈絡，再用 phase scores、資料信心、可用權重與轉換規則檢查是否維持或轉換。Dashboard 會清楚顯示此資訊是外部基準情境，不是純模型自動算出的結果。

## 不打 FRED API

`scripts/build_site.py` 只讀本機 snapshot JSON，不呼叫 FRED API，也不需要 `FRED_API_KEY`。HTML 與 public JSON 不應包含任何 API key。

## Output

預設輸出：

```text
public/index.html
public/data/cycle_snapshot.json
```

`public/index.html` 是 generated local dashboard output。`public/data/cycle_snapshot.json` 是 generated snapshot copy，給未來前端或檢視工具讀取。

兩者現階段都不 commit 到主分支：

- `public/index.html` 由 live `cycle_snapshot` 產生，是本機 build output。
- `public/data/cycle_snapshot.json` 是 live generated data copy。

未來 GitHub Pages deployment 應由 CI 產生並部署 artifact，而不是把 live generated dashboard output 或 data commit 進主分支。

## 使用方式

```bash
python scripts/run_cycle_pipeline.py
python scripts/build_site.py
python -m http.server 8000 -d public
```

## 不是投資建議

Dashboard 只呈現總經資料整理與景氣循環判讀輔助。它不提供資產配置、不提供交易訊號，也不構成投資建議。分數與階段判讀依賴資料品質、資料修正與模型假設。

## 尚未做 Deployment

Phase 5A 不新增 GitHub Actions，也不做 GitHub Pages deployment。這一步只產生本機 static HTML output。

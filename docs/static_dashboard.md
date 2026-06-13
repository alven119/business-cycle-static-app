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
python scripts/run_cycle_pipeline.py --previous-phase-id recovery
python scripts/build_site.py
python -m http.server 8000 -d public
```

## 不是投資建議

Dashboard 只呈現總經資料整理與景氣循環判讀輔助。它不提供資產配置、不提供交易訊號，也不構成投資建議。分數與階段判讀依賴資料品質、資料修正與模型假設。

## 尚未做 Deployment

Phase 5A 不新增 GitHub Actions，也不做 GitHub Pages deployment。這一步只產生本機 static HTML output。

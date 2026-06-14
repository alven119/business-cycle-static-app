# GitHub Pages Deployment

Phase 5B 使用 GitHub Actions 產生 dashboard artifact，並部署到 GitHub Pages。`public/index.html` 與 `public/data/cycle_snapshot.json` 仍然是 generated output，不 commit 到主分支。

## 設定 FRED_API_KEY Secret

在 GitHub repository 頁面：

1. 進入 `Settings`。
2. 進入 `Secrets and variables` -> `Actions`。
3. 選擇 `New repository secret`。
4. Name 填入 `FRED_API_KEY`。
5. Secret 填入本機使用的 FRED API key。

不要把 `.env`、API key、`data/raw/`、`data/derived/` 或 `public/` generated output commit 到 repository。

## 啟用 GitHub Pages

在 GitHub repository 頁面：

1. 進入 `Settings`。
2. 進入 `Pages`。
3. Source 選擇 `GitHub Actions`。

Workflow 使用官方 Pages artifact flow：

- `actions/configure-pages`
- `actions/upload-pages-artifact`
- `actions/deploy-pages`

部署 artifact path 是 `public`。

## 為什麼不 Commit public/index.html

`public/index.html` 是由 live `data/derived/cycle_snapshot.json` 產生的本機 dashboard output。`public/data/cycle_snapshot.json` 是 generated snapshot copy。兩者都可能反映當下下載的公開總經資料與模型輸出，因此現階段不放進主分支。

GitHub Pages 應由 CI 在 workflow 執行時重新下載資料、跑 pipeline、產生 `public/`，再部署 Pages artifact。這樣 repository 只保留 source code、tests、specs 與 docs。

## Workflow 如何運作

Workflow 位於 `.github/workflows/pages.yml`。

每次執行會先：

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
env -u FRED_API_KEY python -m pytest
ruff check .
```

部署觸發時會使用 repository secret：

```yaml
FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
```

然後產生資料與網站：

```bash
python scripts/update_catalog_data.py --force-refresh
python scripts/run_cycle_pipeline.py
python scripts/build_site.py
```

Workflow 不硬寫正式 previous phase。`run_cycle_pipeline.py` 會讀取 `specs/common/current_cycle_context.yaml`，目前以「榮景期第一年剛結束」作為外部 baseline/context，讓 resolver 依循景氣循環順序與轉換規則檢查是否維持或轉換。

最後把 `public/` 上傳為 Pages artifact 並部署。

## 手動觸發

在 GitHub repository 頁面：

1. 進入 `Actions`。
2. 選擇 `Build and deploy business cycle dashboard`。
3. 選擇 `Run workflow`。

`workflow_dispatch` 會執行測試、lint、資料更新、dashboard build 與 Pages deploy。

## 排程時間

`schedule` 使用 UTC，不使用本機時區。若要改排程，請用 UTC 設定 cron。

目前排程是：

```yaml
- cron: "17 10 * * 1"
```

## Push 行為

Push 到 `main` 或 `master` 會跑 test job 與 dashboard build sanity。部署策略保守，push 不會 upload Pages artifact，也不會直接部署 Pages；手動觸發或排程才會產生 live dashboard artifact 並部署。

## 常見錯誤

`FRED_API_KEY missing`

確認 repository secret 名稱完全是 `FRED_API_KEY`，並且 workflow 是在原 repository 執行。不要在 log 中印出 secret。

`Pages 沒有啟用 GitHub Actions source`

到 `Settings` -> `Pages`，把 Source 設成 `GitHub Actions`。

`workflow permissions 不足`

Workflow 需要至少：

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

Repository settings 也需允許 GitHub Actions 建立 Pages deployment。

`public/index.html 沒產生`

檢查 `scripts/run_cycle_pipeline.py` 是否成功產生 `data/derived/cycle_snapshot.json`，再檢查 `scripts/build_site.py` 的錯誤訊息。

`FRED API 下載失敗`

檢查 FRED API key 是否有效、FRED 服務是否可用、GitHub Actions 是否暫時遇到網路錯誤。可重新手動觸發 workflow。

## 不是投資建議

Dashboard 只呈現公開總經資料整理與景氣循環判讀輔助，不提供資產配置、不提供交易訊號，也不構成投資建議。

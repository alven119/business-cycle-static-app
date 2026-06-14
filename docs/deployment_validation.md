# Deployment Validation

Phase 5E 用於 GitHub Pages 部署後驗證與手機 QA。這份 checklist 只確認 generated site 是否可穩定使用，不改 scoring、不改 resolver，也不提供投資建議。

## GitHub Actions 檢查

- `workflow_dispatch` 是否成功啟動。
- `pytest` 是否通過。
- `ruff check .` 是否通過。
- `update_catalog_data.py --force-refresh` 是否成功。
- `run_cycle_pipeline.py` 是否成功，且 stdout 顯示 `previous_phase id=boom source=cycle_context`。
- `build_site.py` 是否成功產生 `public/index.html` 與 `public/data/cycle_snapshot.json`。
- `validate_generated_site.py` 是否通過。
- `actions/upload-pages-artifact` 是否成功。
- `actions/deploy-pages` 是否成功。
- GitHub Pages URL 是否產生。

## GitHub Pages 頁面檢查

- 頁面可開啟。
- Browser title 為「景氣循環儀表板」。
- 目前判讀階段顯示「榮景期」。
- 基準情境顯示「榮景期第一年剛結束」。
- 下一階段觀察顯示「衰退期」。
- 四階段卡片順序為復甦期、成長期、榮景期、衰退期。
- 榮景期卡片有 `目前階段` badge。
- 有「分數最高不等於目前階段」提示。
- 指標依就業、消費、投資、進出口、利率與金融條件、原物料分組。
- 頁面顯示「不構成投資建議」。
- 英文 technical id 可以存在，但不應是主要標題。

## 手機 QA

- iPhone Safari 可開啟。
- 加入主畫面後可正常開啟。
- Hero 不會爆版。
- 四階段卡片可讀。
- 指標卡片不會橫向溢出。
- 字體大小可讀。
- Footer 可讀。
- 深色模式若未支援，至少不能不可讀。

## 常見問題

`Pages 404`

確認 repository Pages source 設為 GitHub Actions，並確認 deploy job 成功完成。若剛部署完成，等待 GitHub Pages 快取更新後再重整。

`workflow 成功但頁面仍是舊版`

確認瀏覽器沒有快取舊頁面。可用無痕視窗、強制重新整理，或直接開 GitHub Actions deployment 輸出的 Pages URL。

`FRED_API_KEY missing`

確認 repository secret 名稱為 `FRED_API_KEY`，並且 workflow 在原 repository 執行。

`FRED API 下載失敗`

檢查 FRED API key 是否有效、FRED 服務是否暫時失敗、GitHub Actions 是否遇到網路問題。可重新手動觸發 workflow。

`public/index.html 未產生`

檢查 `run_cycle_pipeline.py` 是否成功產生 `data/derived/cycle_snapshot.json`，再看 `build_site.py` 與 `validate_generated_site.py` 的錯誤訊息。

`mobile cache 顯示舊頁面`

iPhone Safari 可嘗試關閉分頁後重開、清除網站資料，或移除主畫面捷徑後重新加入。

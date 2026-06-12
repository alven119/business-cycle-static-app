# FRED Catalog Verification

Phase 2E 建立手動的 catalog-level FRED series verification。這個流程用來檢查 `specs/indicator_catalog.yaml` 內的 `candidate_series` 是否能從 FRED 取得資料。

## 為什麼需要驗證 candidate_series

Catalog 內的 series ID 先被視為候選資料來源。候選資料需要驗證是否可下載、是否有觀測值、日期範圍是否合理，以及是否適合作為後續 scoring 的輸入。沒有驗證前，不應把它當成 production-ready data source。

## candidate_series vs verified_series

`candidate_series` 表示尚未完成專案驗證的候選序列。

未來若完成下載、歷史長度、缺值、stale、頻率與修正資料檢查，可以另行新增 `verified_series` 或驗證 metadata。Phase 2E 只產生本機 verification output，不直接改 catalog 為 verified。

## 建立 `.env`

在 repo 根目錄建立本機 `.env`：

```bash
FRED_API_KEY=your_fred_api_key_here
```

`.env` 已被 `.gitignore` 排除，不應 commit。

## 執行驗證

驗證整個 catalog：

```bash
python scripts/verify_fred_catalog.py
```

只驗證單一 indicator：

```bash
python scripts/verify_fred_catalog.py --indicator-id unemployment_rate
```

只驗證單一 series：

```bash
python scripts/verify_fred_catalog.py --series-id UNRATE
```

## Output JSON

預設輸出：

```text
data/derived/fred_catalog_verification.json
```

`data/derived/` 已被 `.gitignore` 排除。這份檔案是本機驗證輸出，可能包含資料狀態與錯誤訊息，不應 commit。

## Status 解讀

- `ok`：series 可下載且有 observations。
- `download_failed`：provider 下載失敗，例如 API key、網路、rate limit 或 series ID 錯誤。
- `empty_observations`：下載成功但沒有 observations。
- `provider_not_supported`：目前 verifier 只支援 FRED。
- `missing_candidate_series`：indicator 沒有設定 `candidate_series`。

## 仍然不是 Phase Scoring

Series verification 只檢查資料來源能否取得資料。它不計算 indicator score、不計算 phase score、不輸出 `current_phase`，也不產生投資建議。


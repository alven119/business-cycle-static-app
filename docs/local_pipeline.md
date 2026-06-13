# Local Pipeline

Phase 4C 建立本機 end-to-end pipeline。它可以從 indicator catalog 的 FRED `candidate_series` 更新 raw cache，並依序產生 indicator scores、phase scores、current phase decision 與 cycle snapshot。

## update_catalog_data.py

`scripts/update_catalog_data.py` 是手動 live data refresh script。它會讀取本機 `.env`，使用 `FRED_API_KEY`，並從 `specs/indicator_catalog.yaml` 找出 provider 為 `fred` 的 `candidate_series`。

常用指令：

```bash
python scripts/update_catalog_data.py --dry-run
python scripts/update_catalog_data.py --force-refresh
python scripts/update_catalog_data.py --indicator-id unemployment_rate
python scripts/update_catalog_data.py --series-id UNRATE
```

`--dry-run` 只列出將處理的 series 與 cache 狀態，不下載資料。實際下載時，單一 series 失敗不會中斷整批，會記錄 failure 並繼續處理其他 series。

## run_cycle_pipeline.py

`scripts/run_cycle_pipeline.py` 串接既有步驟：

1. `score_indicators`
2. `score_phases`
3. `resolve_current_phase`
4. `build_cycle_snapshot`

若加上 `--update-data`，會先執行 catalog data refresh。

```bash
python scripts/run_cycle_pipeline.py --previous-phase-id recovery
python scripts/run_cycle_pipeline.py --update-data --force-refresh --previous-phase-id recovery
```

推薦直接使用上述檔案路徑執行方式，不需要手動設定 `PYTHONPATH`，也不要求使用 `python -m`。Pipeline runner 會用目前 Python interpreter 呼叫各步驟 script，並在子程序環境中設定專案的 `src` import path。

## .env 與 FRED API key

本機 `.env` 可放：

```text
FRED_API_KEY=your_fred_api_key_here
```

`.env` 不應 commit。沒有 `FRED_API_KEY` 時，live data refresh 會清楚報錯。

## Output JSON

預設輸出都在 `data/derived/`：

- `indicator_scores.json`：每個 indicator 的 score/confidence 與 failures。
- `phase_scores.json`：每個 phase 的 score/confidence/available_weight。
- `current_phase_decision.json`：state machine resolver 的 current phase decision。
- `cycle_snapshot.json`：dashboard-ready 的整合 snapshot。

Raw cache 預設在 `data/raw/`。`data/raw` 與 `data/derived` 都不 commit，因為它們是本機產物，可能很大、會更新，也可能含有外部資料快取。

## Raw CSV Mapping

FRED raw CSV 以 series id 命名：

```text
data/raw/fred/<SERIES_ID>.csv
```

例如 `UNRATE` 會對應到：

```text
data/raw/fred/UNRATE.csv
```

`score_indicators.py` 會從 `indicator_catalog.yaml` 的 `candidate_series` 找 raw CSV。若 `candidate_series` 是 list，會依順序選第一個存在且可讀的 CSV；如果第一個不存在，會 fallback 到下一個 candidate。成功評分後，`indicator_scores.json` 的 result details 會包含：

- `selected_series_id`
- `selected_csv_path`
- `candidate_series`

若所有 candidate 都沒有可用 CSV，該 indicator 會進入 failures，不會用假資料補分，也不會產生高 confidence score。

## indicator_scores.json failures

Failure 會包含：

- `indicator_id`
- `error_type`
- `message`

`message` 會說明 candidate series、預期 CSV path 與 root cause。例如 raw CSV 缺漏時，應先確認是否已執行：

```bash
python scripts/update_catalog_data.py --force-refresh
```

## 常見錯誤

- `FRED_API_KEY missing`：確認 `.env` 存在且包含 `FRED_API_KEY`，或環境變數已設定。
- `candidate_series missing`：catalog entry 沒有可用 FRED candidate series，需補 candidate mapping。
- `raw CSV missing`：尚未執行 data refresh，或 scoring 使用的 first candidate raw CSV 不存在。
- `score_indicators failure`：通常是 raw CSV 缺漏、欄位格式不符、資料不足或 indicator spec 參數錯誤。
- `insufficient_evidence`：current phase resolver 沒有足夠 confidence、available_weight 或 score margin 產生 current phase。
- `ModuleNotFoundError: scripts`：代表 pipeline runner 又回到從 `src` package 反向 import `scripts.*` 的 regression；正式流程不應需要手動設定 `PYTHONPATH=.`

## 不是 Dashboard，也不是投資建議

Phase 4C 只建立本機 pipeline 與 JSON outputs。它不建立前端 dashboard、不新增資料庫、不使用 LLM 判斷，也不產生投資建議。

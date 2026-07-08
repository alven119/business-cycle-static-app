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

## Homepage Layout

Phase 5D/5F 將首頁整理為 mobile-first 的景氣循環儀表板，而不是 JSON 欄位清單。頁面主要區塊包含：

- 頂部 headline summary：目前景氣位階、週期位階分數、轉折風險、資料信心、本期重點、`generated_at` 與 `as_of`。
- 下一階段觀察卡：依 `allowed_next_phase_id` 顯示允許的下一階段、candidate score/confidence、resolver reason 與 blocked phases。
- 四階段分數卡：固定顯示復甦期、成長期、榮景期、衰退期。
- 榮景期觀察重點：目前階段為榮景期時，說明這是景氣後期循環與轉折風險觀察，不是投資建議。
- 核心指標：依就業、消費、投資、進出口、利率與金融條件、原物料分組。
- 資料警示與 pipeline failure。

`週期位階分數` 暫時使用 current phase 的 evidence score。它代表目前資料對該階段的證據強度，不是景氣好壞分數，也不是越高就代表景氣越好。

若 current phase 的 `stage_hint` 尚未由 scoring 產生，dashboard 可使用 `current_cycle_context` 的基準文字作為顯示層位階提示；這不會改變模型判斷結果，也不會寫回 `current_phase_decision`。

四階段卡片的 `目前階段` badge 只來自 `current_phase_decision.current_phase_id`。它不使用最高分 phase，也不表示最高分就是 current phase；若最高分與 resolver 判讀不同，頁面會提示仍需依循景氣循環順序與轉換規則。

四階段證據分數表示資料有多像該景氣階段。例如衰退期分數高代表衰退證據較強，榮景期分數高代表景氣後期循環證據較強。

指標分組對齊書中觀察主軸：就業、消費、投資、進出口，以及晚週期常見的利率/金融條件與原物料壓力。這些分組只是閱讀與研究用的資訊架構，不改變 indicator scoring 或 phase scoring。

指標教育性說明來自 `specs/common/indicator_explanations_zh.yaml`。四階段分數說明來自 `specs/common/phase_score_explanations_zh.yaml`。這些文字用於解釋指標在景氣循環中的意義，以及它們如何支持或削弱不同階段證據。

`本期重點` 第一版是保守摘要，不做 period-over-period diff。未來可結合 backtest diagnostics、歷史 timeline 與真實 period-over-period changes 強化摘要。

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

GitHub Pages deployment 已退役。`public/` 仍是本機 generated output，不得把 live generated dashboard output 或 data commit 進主分支。

## 使用方式

```bash
python scripts/run_cycle_pipeline.py
python scripts/build_site.py
python -m http.server 8000 -d public
```

## 不是投資建議

Dashboard 只呈現總經資料整理與景氣循環判讀輔助。它不提供資產配置、不提供交易訊號，也不構成投資建議。分數與階段判讀依賴資料品質、資料修正與模型假設。

榮景期說明聚焦景氣後期循環、升息、通膨、利率、原物料、估值與就業/消費轉弱訊號。它是景氣循環脈絡說明，不是資產配置或交易建議。

## 尚未做 Deployment

Phase 5A 不新增 GitHub Actions，也不做部署。這一步只產生本機 static HTML output。

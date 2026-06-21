# Book strategy golden benchmark

`specs/portfolio/book_strategy_golden_benchmark.yaml` 定義書中策略重現的 golden benchmark，但不執行市場回測。

核心規格：

- 期間：1994 年第一個交易日至 2018 年末。
- 初始投入：10,000 USD。
- 每年最後一個交易日追加 10,000 USD。
- 每年第一個交易日再平衡。
- recession / recovery / growth：100% stocks。
- boom basic：50% stocks，其餘 cash 或 long Treasury。
- boom advanced：year 1 = 70%、year 2 = 50%、year 3 = 30%、year 4+ = 30%；若 boom 僅兩年，最低只降到 50%。
- long Treasury 必須是 7 年以上 U.S. Treasury total-return series。
- cash return、dividends、bond coupons、transaction costs、tax assumptions 都必須明確。

五組策略：

- passive_all_stock
- stock_cash_basic
- stock_cash_advanced
- stock_long_treasury_basic
- stock_long_treasury_advanced

Execution remains blocked until point-in-time phase labels、market total-return data contract、cash-flow-aware methodology runtime、long Treasury series 與 reproduction tolerance 都完成。

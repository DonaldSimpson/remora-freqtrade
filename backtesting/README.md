# Backtesting Utilities

Simple scripts to analyze and compare backtest results.

## compare_results.py

Compare backtest results with and without Remora filtering.

### Usage

```bash
# Run backtests first (with and without Remora)
freqtrade backtesting --strategy SimpleRiskFilterStrategy --export trades
freqtrade backtesting --strategy YourBaselineStrategy --export trades

# Compare results
python backtesting/compare_results.py backtest_with_remora.json backtest_without_remora.json
```

### Output

Shows side-by-side comparison of:
- Total trades
- Win rate
- Profit percentage
- Max drawdown
- Sharpe ratio
- And more...

### Example Output

```
BACKTEST COMPARISON: With Remora vs Without Remora
======================================================================

Metric                         With Remora        Without Remora      Change         
----------------------------------------------------------------------
total_trades                   245                312                -67 (-21.5%)
win_rate                       0.5420             0.4872             +5.48%
profit_total_pct               0.1234             0.0891             +3.43%
max_drawdown                   -0.0823            -0.1245            +4.22%

KEY INSIGHTS:
======================================================================
• Trades reduced by: 21.5%
• Win rate change: +5.48%
• Profit change: +3.43%
• Max drawdown change: +4.22%

Remora improved win rate!
Remora improved profitability!
Remora reduced drawdown!
```

## Notes

- Adjust the `extract_metrics()` function if your backtest output format differs
- Freqtrade exports results in JSON format when using `--export trades`
- For more detailed analysis, see the [remora-backtests repository](https://github.com/DonaldSimpson/remora-backtests)


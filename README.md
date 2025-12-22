# Market Awareness for your Freqtrade Strategies

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Website](https://img.shields.io/badge/Website-remora--ai.com-purple)](https://remora-ai.com) [![Blog](https://img.shields.io/badge/Blog-Detailed%20Analysis-blue)](https://www.donaldsimpson.co.uk/2025/12/22/advanced-risk-management-for-freqtrade-strategies/) [![Backtests](https://img.shields.io/badge/Backtests-Available-green)](https://github.com/DonaldSimpson/remora-backtests) [![Freqtrade](https://img.shields.io/badge/Built%20for-Freqtrade-orange)](https://www.freqtrade.io)

[<img src="images/remora-social-card.jpg" alt="Remora Risk Engine - Stop Bad Trades Before They Happen" width="600">](https://remora-ai.com)

**Market awareness layer for your [Freqtrade](https://www.freqtrade.io) strategies. Add real-time risk filtering with a simple API call - transparent, fail-safe, and easy to remove.**

Remora lets you know if the current market conditions are safe to trade in. It answers "Should I be trading at all right now?" - not "Is this a good entry?"

**How it works:**
```
Your Strategy → Remora API Check → Filtered Trades
     ↓                ↓                    ↓
  Entry Signal    Risk Assessment    Safe Entries Only
```

## What Remora Does

- ✅ Lets you know if current market conditions are safe to trade in
- ✅ Blocks trades during high-risk periods (volatility spikes, regime changes, extreme fear, etc.)
- ✅ Provides full transparency (returns reasoning, not just boolean)
- ✅ Uses multiple data sources with redundancy and failover
- ✅ Market awareness layer specifically built for Freqtrade strategies

## What Remora Does NOT Do

- ❌ Does not replace your Freqtrade strategy logic
- ❌ Does not optimise entry/exit signals
- ❌ Does not require complex configuration
- ❌ Does not lock you in (easy to remove - just delete a few lines)

## Table of Contents

- [Integration Example](#integration-example)
- [What Remora Does](#what-remora-does)
- [Optional: Example Strategies](#optional-example-strategies)
- [Advanced Users](#advanced-users-free-tier)
- [Want Proof?](#want-proof)
- [Who This Is For](#who-this-is-for)
- [Resources & Links](#resources--links)

---

## Integration Example

Protect your Freqtrade strategy in 30 seconds. See exactly what to add to your existing strategy (green) vs what you already have (gray).

> **💡 See the [interactive color-coded example on remora-ai.com](https://remora-ai.com) for the best visual experience.** The website shows the color-coded version that makes it crystal clear what to add.

### Step 0: Set your API key

Before running your strategy, set the environment variable:

```bash
export REMORA_API_KEY="your-api-key"
```

Get your free API key at [remora-ai.com/signup.php](https://remora-ai.com/signup.php)

**Note:** You can use Remora without an API key (60 requests/minute), but registration gives you 300 requests/minute.

### Add Remora to your strategy

The code below shows what to add (marked with `# REMORA:` comments) vs your existing code:

```python
class MyStrategy(IStrategy):
    # Your existing populate_entry_trend method:
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata['pair']

        # Your existing entry conditions...
        # dataframe.loc[:, 'enter_long'] = 1  # example existing logic

        # REMORA: Add this check before return
        if not self.confirm_trade_entry(pair):
            dataframe.loc[:, 'enter_long'] = 0  # REMORA: Skip high-risk trades

        return dataframe  # Your existing return statement

    # REMORA: Add this new method
    def confirm_trade_entry(self, pair: str, **kwargs) -> bool:
        import os
        import requests
        api_key = os.getenv("REMORA_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

        try:
            r = requests.get(
                "https://remora-ai.com/api/v1/risk",
                params={"pair": pair},
                headers=headers,
                timeout=2.0
            )
            return r.json().get("safe_to_trade", True)  # REMORA: Block entry if market is high-risk
        except Exception:
            return True  # REMORA: Fail-open
```

**Instructions:**
1. Inside your existing `populate_entry_trend()`, insert the Remora check (marked with `# REMORA:`) just before `return dataframe`
2. Add the `confirm_trade_entry()` method at the same indentation level as your other strategy methods
3. Everything else in your strategy stays unchanged

**That's it. No extra dependencies, no plugins, no cloning a repo.**

Your strategy will skip risky entries automatically. If Remora is unavailable, trades proceed normally (fail-open by design).

**Removing Remora is as simple as deleting these lines. No lock-in, fully transparent.**

---

## Optional: Example Strategies

### Complete Examples

- **[`simple_risk_filter_strategy.py`](examples/simple_risk_filter_strategy.py)** - Minimal Remora integration
- **[`advanced_risk_filter_strategy.py`](examples/advanced_risk_filter_strategy.py)** - Position sizing, dataframe columns, multi-timeframe context
- **[`freqtrade_config_snippet.json`](examples/freqtrade_config_snippet.json)** - Example Freqtrade configuration file

### Advanced Tools

- **[`plot_risk_vs_price.ipynb`](examples/plot_risk_vs_price.ipynb)** - Jupyter notebook for visualizing risk scores vs price (requires additional dependencies)
- **[`backtesting/compare_results.py`](backtesting/compare_results.py)** - Utility to compare backtest results with/without Remora

---

## Advanced Users (Free Tier)

### Features

- **Structured API access** - Use `remora.client` for `risk_score`, `regime`, and `reasoning`
- **Custom thresholds** - Adjust risk sensitivity in your own code
- **Indicator integration** - Combine Remora with technical indicators
- **Pattern blocking** - Block only specific patterns during high-risk regimes
- **Multi-timeframe context** - Logging and advanced analysis

### Example

```python
from remora.client import RemoraClient

client = RemoraClient()
ctx = client.get_context("BTC/USDT")

if ctx["risk_score"] > 0.7:
    dataframe.loc[:, 'enter_long'] = 0
```

See [`examples/advanced_risk_filter_strategy.py`](examples/advanced_risk_filter_strategy.py) for full examples.

**Note:** Advanced users using `remora.client` may want to check `requirements-advanced.txt` for optional dependencies. The simple snippet integration requires no additional dependencies.

**Coming soon:** Save your preferences, even higher rate limits, and per-user settings/preferences tied to your API key.

---

## Want Proof?

### Backtest Results

**6 years of data, 4 strategies, 20 tests** - See the [Remora Backtests Repository](https://github.com/DonaldSimpson/remora-backtests) for full details.

| Metric | Improvement |
|--------|-------------|
| **Profit** | +1.54% |
| **Drawdown** | -1.55% |
| **Trades Filtered** | 4.3% (increases to 16-19% during bear markets) |
| **Success Rate** | 90% (18 out of 20 tests improved) |

**Key Findings:**
- **Strongest impact during bear markets** - 2022 saw 16-19% filtering during crashes
- **Adaptive filtering** - More trades blocked when market conditions worsen
- **Smoother equity curves** - Fewer losing entries, better risk-adjusted performance

**Detailed Analysis:** See the [blog post](https://www.donaldsimpson.co.uk/2025/12/22/advanced-risk-management-for-freqtrade-strategies/) for complete analysis, financial impact, and methodology.

---

## Who This Is For

| Level | What to do |
|-------|------------|
| **Beginners** | Add the snippet - start blocking risky entries instantly |
| **Intermediate** | Use `advanced_risk_filter_strategy.py` - log risk, adjust sizing |
| **Advanced** | Full API + custom weighting - regime-aware optimisation |

### Why Freqtrade Users Should Care

- **Reduced Drawdowns:** Avoid trading during high-risk market conditions
- **Improved Risk-Adjusted Performance:** Better Sharpe and Sortino ratios
- **Transparency:** See exactly why trades were blocked
- **Fail-Safe:** If Remora is unavailable, trades proceed normally (fail-open)
- **Easy Integration:** Simple API call, not a plugin
- **Easy to Remove:** Just delete a few lines if you want to disable it

---

## Resources & Links

### Remora Website
- [Homepage](https://remora-ai.com/) - Interactive color-coded integration example
- [How It Works](https://remora-ai.com/how-it-works.php) - Technical deep dive
- [Proven Results](https://remora-ai.com/evidence-backtesting.php) - Backtest analysis
- [API Documentation](https://remora-ai.com/api-docs.php) - Complete API reference
- [Sign Up](https://remora-ai.com/signup.php) - Get your free API key
- [Live Status Dashboard](https://remora-ai.com/status.php) - Real-time market conditions

### Blog Post
- [Advanced Risk Management for Freqtrade](https://www.donaldsimpson.co.uk/2025/12/22/advanced-risk-management-for-freqtrade-strategies/) - Detailed analysis and methodology

### GitHub Repositories
- [This Repository](https://github.com/DonaldSimpson/remora-freqtrade) - Freqtrade integration examples
- [Backtests Repository](https://github.com/DonaldSimpson/remora-backtests) - Full backtest results and analysis

### Freqtrade
- [Freqtrade](https://www.freqtrade.io) - Open-source cryptocurrency trading bot

---

## Contributing & Feedback

PRs, issues, and feature requests welcome!

Questions? [remora-ai.com](https://remora-ai.com)

---

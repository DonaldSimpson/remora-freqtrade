# Remora + Freqtrade Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Backtests](https://img.shields.io/badge/Backtests-Available-blue)](https://github.com/DonaldSimpson/remora-backtests)

**Add real-time market context to your existing Freqtrade strategy - avoid the worst trades in seconds.**

Remora helps your strategies avoid high-risk market periods:

- Volatility spikes
- Extreme fear / panic regimes
- Choppy sideways markets
- Market-wide selloffs
- Liquidity traps or news-driven whipsaws

**Remora does NOT replace your strategy.**

It simply acts as a "risk filter" that blocks the entries most likely to lose money.

## Table of Contents

- [Quickest Start (Beginner-Friendly)](#quickest-start-beginner-friendly)
- [Optional: Example Strategies](#optional-example-strategies)
- [Advanced Users (Free Tier)](#advanced-users-free-tier)
- [Want Proof?](#want-proof)
- [Who This Is For](#who-this-is-for)
- [Contributing & Feedback](#contributing--feedback)

---

## Quickest Start (Beginner-Friendly)

If you already have a strategy and want to **start protecting it immediately**, this is all you need.

### 1. Set your API key

Sign up at [remora-ai.com/signup.php](https://remora-ai.com/signup.php) to get your free API key. Then in your terminal:

```bash
export REMORA_API_KEY="your-api-key"
```

(Or add it to `~/.bashrc` / `~/.zshrc` for persistence.)

### 2. Add Remora to your strategy

Inside your strategy class, add this method (or integrate into your entry logic):

```python
import os
import requests

def confirm_trade_entry(self, pair: str, **kwargs) -> bool:
    api_key = os.getenv("REMORA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        response = requests.get(
            "https://api.remora-ai.com/context",
            params={"symbol": pair},
            headers=headers,
            timeout=2.0
        )
        data = response.json()
        return data.get("safe_to_trade", True)
    except Exception:
        return True  # Fail-open if Remora is unavailable
```

Then wrap your entry logic:

```python
if not self.confirm_trade_entry(pair):
    dataframe.loc[:, 'enter_long'] = 0
```

**That's it. No extra dependencies, no plugins, no cloning a repo.**

Your strategy will skip risky entries automatically.

### 3. Verify it works

Run a small backtest:

```bash
freqtrade backtesting --strategy YourStrategy
```

Watch your logs - entries blocked by Remora will show `safe_to_trade=False`.

Your existing logic stays intact, but you avoid the worst trades.

---

## Optional: Example Strategies

- **`examples/simple_risk_filter_strategy.py`** - minimal Remora integration
- **`examples/advanced_risk_filter_strategy.py`** - position sizing, dataframe columns, multi-timeframe context
- **`examples/freqtrade_config_snippet.json`** - example Freqtrade configuration file

These examples show how to extend your strategy with more features.

**Advanced/Optional:** 
- `examples/plot_risk_vs_price.ipynb` - Jupyter notebook for visualizing risk scores vs price (requires additional dependencies)
- `backtesting/compare_results.py` - utility to compare backtest results with/without Remora

---

## Advanced Users (Free Tier)

For more control with the current free tier:

- Use `remora.client` for structured access to `risk_score` and `reasoning`
- Adjust thresholds for risk sensitivity in your own code
- Combine Remora with technical indicators
- Block only specific patterns during high-risk regimes
- Multi-timeframe context and logging

Example:

```python
from remora.client import RemoraClient

client = RemoraClient()
ctx = client.get_context("BTC/USDT")

if ctx["risk_score"] > 0.7:
    dataframe.loc[:, 'enter_long'] = 0
```

See `examples/advanced_risk_filter_strategy.py` for full examples.

**Note:** Advanced users using `remora.client` may want to check `requirements-advanced.txt` for optional dependencies. The simple snippet integration requires no additional dependencies.

**Coming soon with Remora-ai:** save your preferences, even higher rate limits, and per-user settings/preferences tied to your API key.

---

## Want Proof?

Backtests comparing with/without Remora are in:

**[Remora Backtests Repository](https://github.com/DonaldSimpson/remora-backtests)**

Shows actual trade improvements, smoother equity curves, and fewer losing entries.

---

## Who This Is For

| Level | What to do |
|-------|------------|
| **Beginners** | Add the snippet - start blocking risky entries instantly |
| **Intermediate** | Use `advanced_risk_filter_strategy.py` - log risk, adjust sizing |
| **Advanced** | Full API + custom weighting - regime-aware optimisation |

---

## Contributing & Feedback

PRs, issues, and feature requests welcome!


Questions? https://remora-ai.com

---


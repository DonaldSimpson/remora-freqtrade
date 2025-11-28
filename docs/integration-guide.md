# Remora Integration Guide

A comprehensive guide for integrating Remora into your Freqtrade strategies.

## Table of Contents

1. [Understanding Remora's Risk Signals](#understanding-remoras-risk-signals)
2. [Basic Integration](#basic-integration)
3. [Advanced Integration Patterns](#advanced-integration-patterns)
4. [Position Sizing with Risk Scores](#position-sizing-with-risk-scores)
5. [Multi-Timeframe Context](#multi-timeframe-context)
6. [Error Handling Best Practices](#error-handling-best-practices)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Understanding Remora's Risk Signals

Remora provides three key pieces of information:

### `safe_to_trade` (boolean)
- `True`: Market conditions are acceptable for trading
- `False`: High-risk conditions detected - avoid entries

### `risk_score` (float: 0.0 - 1.0)
- `0.0 - 0.3`: Low risk - normal trading conditions
- `0.3 - 0.6`: Moderate risk - consider reducing position size
- `0.6 - 1.0`: High risk - avoid new entries

### `reasoning` (list of strings)
- Human-readable explanations of why risk is elevated
- Examples: "Volatility spike detected", "Extreme fear conditions", "Low liquidity"

---

## Basic Integration

### Simple Approach (Recommended for Beginners)

The simplest way is to use inline `requests` calls - no extra dependencies needed:

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

Then in your entry logic:

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    pair = metadata["pair"]
    
    if not self.confirm_trade_entry(pair):
        return dataframe  # Block entries
    
    # Your normal entry logic
    dataframe.loc[:, "enter_long"] = 1
    return dataframe
```

See `examples/simple_risk_filter_strategy.py` for a complete example.

### Advanced Approach (Using Client Library)

For more structured access, use the Remora client:

### Step 1: Initialize Remora Client

```python
from remora.client import RemoraClient

class MyStrategy(IStrategy):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.remora = RemoraClient()
```

### Step 2: Check Risk Before Entry

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    pair = metadata["pair"]
    
    try:
        ctx = self.remora.get_context(pair)
        
        if not ctx.get("safe_to_trade", True):
            self.log(f"Remora blocked entry for {pair}: {ctx.get('reasoning')}")
            return dataframe  # No entries
        
        # Your normal entry logic here
        dataframe.loc[:, "enter_long"] = 1
        
    except Exception as e:
        self.log(f"Remora error for {pair}: {e}")
        # Fallback: allow entries if API fails
        dataframe.loc[:, "enter_long"] = 1
    
    return dataframe
```

---

## Advanced Integration Patterns

### Pattern 1: Attach Risk Data to DataFrame

This allows you to use risk scores in your technical indicators:

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    pair = metadata["pair"]
    
    try:
        ctx = self.remora.get_context(pair)
        
        # Add Remora data as columns
        dataframe["remora_safe"] = ctx["safe_to_trade"]
        dataframe["remora_risk"] = ctx["risk_score"]
        dataframe["remora_reason"] = str(ctx.get("reasoning", []))
        
    except Exception as e:
        self.log(f"Remora error: {e}")
        # Default to safe if API fails
        dataframe["remora_safe"] = True
        dataframe["remora_risk"] = 0.0
        dataframe["remora_reason"] = ""
    
    # Your other indicators
    dataframe["rsi"] = ta.RSI(dataframe)
    
    return dataframe
```

### Pattern 2: Combine with Technical Indicators

Use Remora as a filter on top of your existing strategy:

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Your normal TA logic
    dataframe.loc[
        (dataframe["rsi"] < 30) &
        (dataframe["macd"] > dataframe["macdsignal"]),
        "enter_long"
    ] = 1
    
    # Apply Remora filter
    dataframe.loc[~dataframe["remora_safe"], "enter_long"] = 0
    
    return dataframe
```

### Pattern 3: Risk-Adjusted Entry Thresholds

Adjust your entry conditions based on risk level:

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Stricter RSI threshold during high risk
    low_risk_mask = dataframe["remora_risk"] < 0.3
    high_risk_mask = dataframe["remora_risk"] >= 0.3
    
    # Normal entries during low risk
    dataframe.loc[
        low_risk_mask &
        (dataframe["rsi"] < 30),
        "enter_long"
    ] = 1
    
    # Stricter entries during high risk (RSI < 25)
    dataframe.loc[
        high_risk_mask &
        (dataframe["rsi"] < 25),
        "enter_long"
    ] = 1
    
    return dataframe
```

---

## Position Sizing with Risk Scores

### Basic Position Sizing

```python
def adjust_trade_position(self, trade, current_time, current_rate, 
                         current_profit, **kwargs):
    """Reduce position size during high-risk periods"""
    
    dataframe = self.dp.get_analyzed_dataframe(trade.pair)
    risk = dataframe["remora_risk"].iloc[-1]
    
    if risk > 0.7:
        return 0  # Don't increase position
    elif risk > 0.4:
        return 0.5  # Half size
    else:
        return 1.0  # Full size
```

### Dynamic Position Sizing

```python
def custom_stake_amount(self, pair: str, current_time, current_rate,
                       proposed_stake, min_stake, max_stake, **kwargs):
    """Adjust initial stake based on risk"""
    
    try:
        ctx = self.remora.get_context(pair)
        risk = ctx.get("risk_score", 0.0)
        
        # Scale stake inversely with risk
        risk_multiplier = max(0.3, 1.0 - risk)  # Minimum 30% of stake
        adjusted_stake = proposed_stake * risk_multiplier
        
        return max(min_stake, min(adjusted_stake, max_stake))
        
    except Exception as e:
        self.log(f"Remora error in stake calculation: {e}")
        return proposed_stake  # Fallback to normal stake
```

---

## Multi-Timeframe Context

Fetch Remora context for different timeframes:

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    pair = metadata["pair"]
    
    # Get context for current timeframe
    try:
        ctx_5m = self.remora.get_context(pair)  # Current timeframe
        dataframe["remora_risk_5m"] = ctx_5m["risk_score"]
    except:
        dataframe["remora_risk_5m"] = 0.0
    
    # You could also check higher timeframes for trend context
    # (This would require additional API calls or caching)
    
    return dataframe
```

---

## Error Handling Best Practices

### Graceful Degradation

Always handle API failures gracefully:

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    pair = metadata["pair"]
    
    try:
        ctx = self.remora.get_context(pair)
        safe = ctx.get("safe_to_trade", True)
    except requests.exceptions.Timeout:
        self.log(f"Remora timeout for {pair} - allowing entries")
        safe = True  # Allow entries if API is slow
    except requests.exceptions.RequestException as e:
        self.log(f"Remora API error for {pair}: {e} - allowing entries")
        safe = True  # Don't block trading if API is down
    except Exception as e:
        self.log(f"Unexpected Remora error for {pair}: {e}")
        safe = True  # Fail open
    
    if not safe:
        return dataframe  # Block entries
    
    # Your entry logic
    dataframe.loc[:, "enter_long"] = 1
    return dataframe
```

### Caching for Performance

Cache risk context to avoid excessive API calls:

```python
class MyStrategy(IStrategy):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.remora = RemoraClient()
        self.risk_cache = {}  # pair -> (ctx, timestamp)
        self.cache_ttl = 60  # Cache for 60 seconds
    
    def get_cached_context(self, pair: str):
        """Get context with caching"""
        now = time.time()
        
        if pair in self.risk_cache:
            ctx, timestamp = self.risk_cache[pair]
            if now - timestamp < self.cache_ttl:
                return ctx
        
        # Fetch fresh context
        try:
            ctx = self.remora.get_context(pair)
            self.risk_cache[pair] = (ctx, now)
            return ctx
        except Exception as e:
            self.log(f"Remora error: {e}")
            # Return cached if available, else default
            if pair in self.risk_cache:
                return self.risk_cache[pair][0]
            return {"safe_to_trade": True, "risk_score": 0.0}
```

---

## Performance Optimization

### 1. Call Remora in `populate_indicators` (Recommended)

This is called once per candle, not per entry signal:

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Call Remora here - once per candle
    ctx = self.remora.get_context(metadata["pair"])
    dataframe["remora_safe"] = ctx["safe_to_trade"]
    return dataframe

def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Use cached data - no API call
    if not dataframe["remora_safe"].iloc[-1]:
        return dataframe
    # Entry logic...
```

### 2. Avoid Calling in `populate_entry_trend`

❌ **Don't do this:**
```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    ctx = self.remora.get_context(metadata["pair"])  # Called many times!
    # ...
```

✅ **Do this instead:**
```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    ctx = self.remora.get_context(metadata["pair"])  # Called once per candle
    dataframe["remora_safe"] = ctx["safe_to_trade"]
    return dataframe
```

---

## Troubleshooting

### Issue: "Remora API key missing"

**Solution:**
```bash
export REMORA_API_KEY="your-api-key"
```

Or add to your Freqtrade config:
```json
{
  "remora_api_key": "your-api-key"
}
```

Then modify your strategy:
```python
def __init__(self, config: dict) -> None:
    super().__init__(config)
    api_key = config.get("remora_api_key") or os.getenv("REMORA_API_KEY")
    self.remora = RemoraClient(api_key=api_key)
```

### Issue: API calls are too slow

**Solutions:**
1. Use caching (see above)
2. Call Remora in `populate_indicators`, not `populate_entry_trend`
3. Reduce timeout if needed: `RemoraClient(timeout=1)`

### Issue: Too many entries blocked

**Solution:** Adjust your risk threshold:
```python
# Instead of blocking all unsafe trades
if not ctx["safe_to_trade"]:
    return dataframe

# Use a threshold
if ctx["risk_score"] > 0.7:  # Only block very high risk
    return dataframe
```

### Issue: Strategy not using Remora data

**Check:**
1. Is `REMORA_API_KEY` set?
2. Are you calling `get_context()` in the right method?
3. Are you checking the dataframe columns correctly?
4. Check Freqtrade logs for Remora errors

---

## Next Steps

- Review example strategies: `examples/simple_risk_filter_strategy.py` and `examples/advanced_risk_filter_strategy.py`
- For hybrid strategies combining indicators, see `examples/advanced_risk_filter_strategy.py`
- Run backtests to see the impact
- Visit the backtesting repository: https://github.com/DonaldSimpson/remora-backtests

---

## Questions?

Open an issue or visit: https://remora-ai.com/


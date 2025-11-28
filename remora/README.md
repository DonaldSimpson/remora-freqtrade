# Remora Client Library

**For advanced users only.** The simple integration (see main README) doesn't require this.

This is a convenience wrapper around the Remora API for structured access to risk data.

## Usage

The client is part of this repo - no installation needed. Just import it:

```python
from remora.client import RemoraClient

client = RemoraClient()
ctx = client.get_context("BTC/USDT")

print(ctx["safe_to_trade"])  # bool
print(ctx["risk_score"])      # float 0.0-1.0
print(ctx["reasoning"])       # list of strings
```

## When to Use

- You want structured access to all Remora fields
- You're building complex strategies with risk scoring
- You prefer object-oriented API access
- You want type hints and IDE autocomplete

## When NOT to Use

- You just want simple entry blocking → use the inline snippet from main README
- You want zero dependencies → use inline `requests.get()` calls
- You're just getting started → the simple integration is easier

See `examples/advanced_risk_filter_strategy.py` for usage examples.


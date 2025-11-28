"""
Simple utility to compare backtest results with and without Remora filtering.

Usage:
    python backtesting/compare_results.py <backtest_with_remora.json> <backtest_without_remora.json>
"""

import json
import sys
from typing import Dict, Any


def load_backtest_results(filepath: str) -> Dict[str, Any]:
    """Load backtest results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_metrics(results: Dict[str, Any]) -> Dict[str, float]:
    """Extract key metrics from backtest results."""
    # Adjust these keys based on your actual Freqtrade backtest output format
    return {
        "total_trades": results.get("total_trades", 0),
        "winning_trades": results.get("wins", 0),
        "losing_trades": results.get("losses", 0),
        "win_rate": results.get("winrate", 0.0),
        "profit_total": results.get("profit_total", 0.0),
        "profit_total_pct": results.get("profit_total_pct", 0.0),
        "max_drawdown": results.get("max_drawdown", 0.0),
        "max_drawdown_abs": results.get("max_drawdown_abs", 0.0),
        "sharpe_ratio": results.get("sharpe_ratio", 0.0),
    }


def print_comparison(with_remora: Dict[str, float], without_remora: Dict[str, float]):
    """Print a formatted comparison of results."""
    print("\n" + "="*70)
    print("BACKTEST COMPARISON: With Remora vs Without Remora")
    print("="*70)
    
    print(f"\n{'Metric':<30} {'With Remora':<20} {'Without Remora':<20} {'Change':<15}")
    print("-" * 70)
    
    for key in with_remora.keys():
        with_val = with_remora[key]
        without_val = without_remora[key]
        
        if isinstance(with_val, float):
            if key in ["win_rate", "profit_total_pct", "max_drawdown", "sharpe_ratio"]:
                change = with_val - without_val
                change_str = f"{change:+.2%}" if "%" in str(change) else f"{change:+.4f}"
                print(f"{key:<30} {with_val:<20.4f} {without_val:<20.4f} {change_str:<15}")
            else:
                change = with_val - without_val
                change_pct = (change / without_val * 100) if without_val != 0 else 0
                print(f"{key:<30} {with_val:<20.0f} {without_val:<20.0f} {change:+.0f} ({change_pct:+.1f}%)")
        else:
            change = with_val - without_val
            change_pct = (change / without_val * 100) if without_val != 0 else 0
            print(f"{key:<30} {with_val:<20} {without_val:<20} {change:+.0f} ({change_pct:+.1f}%)")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    
    # Calculate improvements
    trades_reduction = ((without_remora["total_trades"] - with_remora["total_trades"]) / 
                       without_remora["total_trades"] * 100) if without_remora["total_trades"] > 0 else 0
    
    winrate_improvement = with_remora["win_rate"] - without_remora["win_rate"]
    profit_improvement = with_remora["profit_total_pct"] - without_remora["profit_total_pct"]
    drawdown_reduction = without_remora["max_drawdown"] - with_remora["max_drawdown"]
    
    print(f"• Trades reduced by: {trades_reduction:.1f}%")
    print(f"• Win rate change: {winrate_improvement:+.2%}")
    print(f"• Profit change: {profit_improvement:+.2%}")
    print(f"• Max drawdown change: {drawdown_reduction:+.2%}")
    
    if winrate_improvement > 0:
        print("\n✅ Remora improved win rate!")
    if profit_improvement > 0:
        print("✅ Remora improved profitability!")
    if drawdown_reduction > 0:
        print("✅ Remora reduced drawdown!")
    
    print()


def main():
    """Main comparison function."""
    if len(sys.argv) != 3:
        print("Usage: python compare_results.py <with_remora.json> <without_remora.json>")
        print("\nExample:")
        print("  python compare_results.py backtest_remora.json backtest_baseline.json")
        sys.exit(1)
    
    with_remora_file = sys.argv[1]
    without_remora_file = sys.argv[2]
    
    try:
        with_remora_results = load_backtest_results(with_remora_file)
        without_remora_results = load_backtest_results(without_remora_file)
        
        with_remora_metrics = extract_metrics(with_remora_results)
        without_remora_metrics = extract_metrics(without_remora_results)
        
        print_comparison(with_remora_metrics, without_remora_metrics)
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


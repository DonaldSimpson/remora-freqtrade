"""
Simple Risk Filter Strategy - Minimal Remora Integration

This is the simplest possible integration - just blocks entries when Remora
detects high-risk market conditions. Perfect for adding to your existing strategy.

No dependencies required beyond requests (which Freqtrade already uses).

To use: Copy the confirm_trade_entry() method into your existing strategy.
"""

from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import os
import requests


class SimpleRiskFilterStrategy(IStrategy):
    """
    A minimal example showing how to add Remora risk filtering to any strategy.
    
    This demonstrates the simplest integration:
    1. Check Remora API before entries
    2. Block entries if safe_to_trade is False
    3. Fail-open if API is unavailable (don't break your strategy)
    """

    timeframe = "5m"

    def confirm_trade_entry(self, pair: str, **kwargs) -> bool:
        """
        Check Remora API to see if it's safe to enter this trade.
        
        Returns True if safe to trade, False if Remora blocks it.
        Fails open (returns True) if API is unavailable.
        """
        api_key = os.getenv("REMORA_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
        try:
            response = requests.get(
                "https://remora-ai.com/api/v1/risk",
                params={"pair": pair},  # REMORA: API expects "pair" parameter
                headers=headers,
                timeout=2.0
            )
            response.raise_for_status()
            data = response.json()
            
            safe = data.get("safe_to_trade", True)
            
            if not safe:
                reasoning = data.get('reasoning', ['High risk'])
                self.log(f"REMORA: Blocked entry for {pair}: {reasoning}")
            
            return safe
            
        except requests.exceptions.Timeout:
            self.log(f"Remora timeout for {pair} - allowing entry")
            return True  # Fail-open if API is slow
        except requests.exceptions.RequestException as e:
            self.log(f"Remora API error for {pair}: {e} - allowing entry")
            return True  # Fail-open if API is down
        except Exception as e:
            self.log(f"Unexpected Remora error for {pair}: {e} - allowing entry")
            return True  # Fail-open on any error

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Your normal indicator logic goes here"""
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry logic with Remora filtering.
        
        Your normal entry conditions go here, then Remora filters them.
        """
        pair = metadata["pair"]
        
        # Your normal entry logic
        # Example: enter on any signal (you'd replace this with your actual logic)
        dataframe.loc[:, "enter_long"] = 1
        
        # REMORA: Apply risk filter - block entries if market conditions are unsafe
        if not self.confirm_trade_entry(pair):
            dataframe.loc[:, "enter_long"] = 0  # REMORA: Skip high-risk trades
        
        return dataframe


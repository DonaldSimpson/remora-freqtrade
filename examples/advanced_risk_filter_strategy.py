"""
Advanced Risk Filter Strategy - Full Remora Integration

This example shows advanced Remora usage with the remora.client library:
- Risk-adjusted position sizing
- Adding Remora context to dataframe columns
- Logging risk reasoning
- Using risk_score for threshold-based filtering
- Position adjustment based on risk

Uses remora.client from this repo for structured API access.
See remora/README.md for when to use the client vs inline requests.
"""

from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from remora.client import RemoraClient


class AdvancedRiskFilterStrategy(IStrategy):
    """
    Advanced example using Remora with full feature set:
    
    - Blocks trades in dangerous regimes
    - Logs reasoning for debugging
    - Adjusts position sizing based on risk score
    - Attaches Remora data to dataframe for use in indicators
    - Risk-threshold based entry filtering
    """

    timeframe = "5m"

    minimal_roi = {
        "0": 0.05,
        "30": 0.02,
        "60": 0.01,
    }

    stoploss = -0.10

    position_adjustment_enable = True

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.remora = RemoraClient()

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add Remora risk context to the dataframe.
        
        This allows you to use risk scores in your technical analysis.
        """
        pair = metadata["pair"]

        try:
            ctx = self.remora.get_context(pair)
            
            # Attach Remora context to the dataframe
            dataframe["remora_safe"] = ctx["safe_to_trade"]
            dataframe["remora_risk"] = ctx["risk_score"]
            dataframe["remora_reason"] = str(ctx.get("reasoning", []))
            
        except Exception as e:
            self.log(f"Remora error for {pair}: {e}")
            # Default to safe if API fails
            dataframe["remora_safe"] = True
            dataframe["remora_risk"] = 0.0
            dataframe["remora_reason"] = ""

        # Your other indicators go here
        # dataframe["rsi"] = ta.RSI(dataframe)
        # etc.

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry logic with risk-based filtering.
        
        Uses both safe_to_trade boolean and risk_score threshold.
        """
        safe = dataframe["remora_safe"].iloc[-1]
        risk_score = dataframe["remora_risk"].iloc[-1]
        reason = dataframe["remora_reason"].iloc[-1]

        # Block if Remora says unsafe
        if not safe:
            self.log(f"Remora blocked entry: {reason}")
            return dataframe

        # Your normal entry logic here
        # Example: enter on any signal (replace with your actual logic)
        dataframe.loc[:, "enter_long"] = 1

        # Additional filtering: only enter if risk is below threshold
        # Adjust 0.4 threshold based on your risk tolerance
        if risk_score >= 0.4:
            self.log(f"Remora filtered entry (risk_score={risk_score:.2f} >= 0.4)")
            dataframe.loc[:, "enter_long"] = 0

        return dataframe

    def adjust_trade_position(self, trade, current_time, current_rate,
                             current_profit, **kwargs):
        """
        Risk-adjusted position sizing.
        
        Reduces position size during elevated risk periods.
        """
        if trade.pair not in self.dp.current_whitelist():
            return None

        dataframe = self.dp.get_analyzed_dataframe(trade.pair)
        risk = dataframe["remora_risk"].iloc[-1]

        if risk > 0.7:
            return 0  # Don't increase position during high risk
        elif risk > 0.4:
            return 0.5  # Half size during moderate risk
        else:
            return 1.0  # Full size during low risk

    def custom_stake_amount(self, pair: str, current_time, current_rate,
                           proposed_stake, min_stake, max_stake, **kwargs):
        """
        Adjust initial stake based on Remora risk score.
        
        Reduces position size during elevated risk periods.
        """
        try:
            ctx = self.remora.get_context(pair)
            risk = ctx.get("risk_score", 0.0)

            # Scale stake: 100% at risk=0, 50% at risk=0.5, 30% at risk=1.0
            risk_multiplier = max(0.3, 1.0 - (risk * 0.7))
            adjusted_stake = proposed_stake * risk_multiplier

            return max(min_stake, min(adjusted_stake, max_stake))

        except Exception as e:
            self.log(f"Remora error in stake calculation: {e}")
            return proposed_stake  # Fallback to normal stake


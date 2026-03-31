import pandas as pd
import structlog

from datetime import datetime
from typing import Optional

logger = structlog.get_logger()

DEFAULT_COSTS = {
    "spread_pips": 1.5,
    "slippage_pips": 0.5,
    "pip_value": 0.0001,
}


class OrderSimulator:
    """
    Simulates realistic order execution for backtesting.

    GOLDEN RULE: Signal at bar[i] → execute at bar[i+1] open.
    Never execute at current bar close.
    """

    def __init__(
        self,
        spread_pips: float = 1.5,
        slippage_pips: float = 0.5,
        initial_capital: float = 10000.0,
        risk_per_trade: float = 0.01,
    ):
        self.spread_pips = spread_pips
        self.slippage_pips = slippage_pips
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade

        self.pip_value = 0.0001
        self.total_cost_pips = spread_pips + slippage_pips
        self.logger = logger.bind(component="OrderSimulator")

    def simulate(self, df: pd.DataFrame, strategy: dict) -> dict:
        """
        Run full simulation bar by bar.

        Args:
            df: DataFrame with OHLC data and signals
            strategy: Dict with entry/exit rules

        Returns:
            dict with trades and equity_curve
        """
        return self._run_simulation(df, strategy)

    def _calculate_position_size(self, equity: float, stop_loss_pips: float) -> float:
        """
        Calculate position size based on risk management.

        Args:
            equity: Current account equity
            stop_loss_pips: Stop loss in pips

        Returns:
            Position size in lots
        """
        risk_amount = equity * self.risk_per_trade

        if stop_loss_pips > 0:
            lots = risk_amount / (stop_loss_pips * self.pip_value * 100000)
        else:
            lots = 0.01

        return max(0.01, min(lots, 10.0))

    def _run_simulation(self, df: pd.DataFrame, strategy: dict) -> dict:
        """
        Run the backtest simulation bar by bar.

        Args:
            df: DataFrame with OHLC data and signals
            strategy: Strategy configuration dict

        Returns:
            dict with trades, equity_curve, and final_equity
        """
        equity = self.initial_capital
        equity_curve = [self.initial_capital]
        trades = []

        position = None
        entry_price = None
        entry_bar = None
        entry_lots = None

        exit_rules = strategy.get("exit_rules", {})
        sl_pips = exit_rules.get("stop_loss_pips", 50)
        tp_pips = exit_rules.get("take_profit_pips", 100)

        for bar_idx in range(1, len(df)):
            current_bar = df.iloc[bar_idx]
            prev_bar = df.iloc[bar_idx - 1]

            if position is not None:
                execute_price = current_bar["open"]

                if position == "long":
                    sl_price = entry_price - sl_pips * self.pip_value
                    tp_price = entry_price + tp_pips * self.pip_value

                    if current_bar["low"] <= sl_price:
                        exit_price = sl_price
                        pnl_pips = -sl_pips - self.total_cost_pips

                        exit_time = (
                            current_bar.name
                            if hasattr(current_bar, "name")
                            else bar_idx
                        )
                        entry_time = (
                            prev_bar.name if hasattr(prev_bar, "name") else entry_bar
                        )

                        trade = self._close_trade(
                            direction="long",
                            entry_price=entry_price,
                            exit_price=exit_price,
                            entry_bar=entry_bar,
                            exit_bar=bar_idx,
                            pnl_pips=pnl_pips,
                            lots=entry_lots,
                            exit_reason="stop_loss",
                            df=df,
                        )
                        trades.append(trade)

                        pnl_dollars = pnl_pips * self.pip_value * 100000 * entry_lots
                        equity += pnl_dollars
                        position = None

                    elif current_bar["high"] >= tp_price:
                        exit_price = tp_price
                        pnl_pips = tp_pips - self.total_cost_pips

                        trade = self._close_trade(
                            direction="long",
                            entry_price=entry_price,
                            exit_price=exit_price,
                            entry_bar=entry_bar,
                            exit_bar=bar_idx,
                            pnl_pips=pnl_pips,
                            lots=entry_lots,
                            exit_reason="take_profit",
                            df=df,
                        )
                        trades.append(trade)

                        pnl_dollars = pnl_pips * self.pip_value * 100000 * entry_lots
                        equity += pnl_dollars
                        position = None

                elif position == "short":
                    sl_price = entry_price + sl_pips * self.pip_value
                    tp_price = entry_price - tp_pips * self.pip_value

                    if current_bar["high"] >= sl_price:
                        exit_price = sl_price
                        pnl_pips = -sl_pips - self.total_cost_pips

                        trade = self._close_trade(
                            direction="short",
                            entry_price=entry_price,
                            exit_price=exit_price,
                            entry_bar=entry_bar,
                            exit_bar=bar_idx,
                            pnl_pips=pnl_pips,
                            lots=entry_lots,
                            exit_reason="stop_loss",
                            df=df,
                        )
                        trades.append(trade)

                        pnl_dollars = pnl_pips * self.pip_value * 100000 * entry_lots
                        equity += pnl_dollars
                        position = None

                    elif current_bar["low"] <= tp_price:
                        exit_price = tp_price
                        pnl_pips = tp_pips - self.total_cost_pips

                        trade = self._close_trade(
                            direction="short",
                            entry_price=entry_price,
                            exit_price=exit_price,
                            entry_bar=entry_bar,
                            exit_bar=bar_idx,
                            pnl_pips=pnl_pips,
                            lots=entry_lots,
                            exit_reason="take_profit",
                            df=df,
                        )
                        trades.append(trade)

                        pnl_dollars = pnl_pips * self.pip_value * 100000 * entry_lots
                        equity += pnl_dollars
                        position = None

            if position is None:
                if prev_bar.get("signal_long", False):
                    entry_price = current_bar["open"] + (
                        self.spread_pips * self.pip_value
                    )
                    entry_lots = self._calculate_position_size(equity, sl_pips)
                    position = "long"
                    entry_bar = bar_idx

                elif prev_bar.get("signal_short", False):
                    entry_price = current_bar["open"] - (
                        self.spread_pips * self.pip_value
                    )
                    entry_lots = self._calculate_position_size(equity, sl_pips)
                    position = "short"
                    entry_bar = bar_idx

            equity_curve.append(equity)

        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "final_equity": equity,
        }

    def _close_trade(
        self,
        direction: str,
        entry_price: float,
        exit_price: float,
        entry_bar: int,
        exit_bar: int,
        pnl_pips: float,
        lots: float,
        exit_reason: str,
        df: pd.DataFrame,
    ) -> dict:
        """
        Create a trade record dict matching TradeRecord fields.

        Args:
            direction: "long" or "short"
            entry_price: Price at entry
            exit_price: Price at exit
            entry_bar: Bar index of entry
            exit_bar: Bar index of exit
            pnl_pips: Profit/loss in pips
            lots: Position size
            exit_reason: Reason for exit (stop_loss, take_profit)
            df: DataFrame for timestamp lookup

        Returns:
            dict matching TradeRecord fields
        """
        entry_time = df.index[entry_bar] if entry_bar < len(df) else entry_bar
        exit_time = df.index[exit_bar] if exit_bar < len(df) else exit_bar

        pnl_dollars = pnl_pips * self.pip_value * 100000 * lots

        return {
            "direction": direction,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl_pips": pnl_pips,
            "pnl_dollars": pnl_dollars,
            "exit_reason": exit_reason,
            "lots": lots,
        }

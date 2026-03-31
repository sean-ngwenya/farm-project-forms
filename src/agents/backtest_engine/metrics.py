import numpy as np
import structlog

logger = structlog.get_logger()


class MetricsCalculator:
    """
    Calculates all performance metrics from trades and equity curve.
    """

    def __init__(self):
        self.trading_hours_per_year = 6240
        self.logger = logger.bind(component="MetricsCalculator")

    def calculate(
        self,
        trades: list[dict],
        equity_curve: list[float],
        initial_capital: float = 10000.0,
    ) -> dict:
        """
        Calculate all performance metrics.

        Args:
            trades: List of trade dicts with pnl_pips and pnl_dollars
            equity_curve: List of equity values over time
            initial_capital: Starting capital

        Returns:
            dict with all calculated metrics
        """
        if len(trades) == 0:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "calmar_ratio": 0.0,
                "max_drawdown": 0.0,
                "net_profit_pips": 0.0,
                "net_profit_dollars": 0.0,
                "avg_trade_pips": 0.0,
                "avg_win_pips": 0.0,
                "avg_loss_pips": 0.0,
                "equity_curve_r2": 0.0,
                "initial_capital": initial_capital,
                "final_capital": initial_capital,
                "total_return_pct": 0.0,
            }

        net_profit_pips = sum(t["pnl_pips"] for t in trades)
        net_profit_dollars = sum(t["pnl_dollars"] for t in trades)
        final_capital = equity_curve[-1] if equity_curve else initial_capital

        winners = [t for t in trades if t["pnl_pips"] > 0]
        losers = [t for t in trades if t["pnl_pips"] < 0]

        avg_trade_pips = net_profit_pips / len(trades)
        avg_win_pips = (
            sum(t["pnl_pips"] for t in winners) / len(winners) if winners else 0.0
        )
        avg_loss_pips = (
            sum(t["pnl_pips"] for t in losers) / len(losers) if losers else 0.0
        )

        total_return_pct = (final_capital - initial_capital) / initial_capital

        return {
            "total_trades": len(trades),
            "win_rate": self._win_rate(trades),
            "profit_factor": self._profit_factor(trades),
            "sharpe_ratio": self._sharpe_ratio(equity_curve),
            "sortino_ratio": self._sortino_ratio(equity_curve),
            "calmar_ratio": self._calmar_ratio(equity_curve, initial_capital),
            "max_drawdown": self._max_drawdown(equity_curve),
            "net_profit_pips": net_profit_pips,
            "net_profit_dollars": net_profit_dollars,
            "avg_trade_pips": avg_trade_pips,
            "avg_win_pips": avg_win_pips,
            "avg_loss_pips": avg_loss_pips,
            "equity_curve_r2": self._equity_curve_r2(equity_curve),
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "total_return_pct": total_return_pct,
        }

    def _sharpe_ratio(self, equity_curve: list[float]) -> float:
        """Calculate annualized Sharpe ratio from equity curve."""
        if len(equity_curve) < 2:
            return 0.0

        returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        returns = returns[~np.isnan(returns)]

        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0

        sharpe = np.mean(returns) / np.std(returns)
        annualized = sharpe * np.sqrt(self.trading_hours_per_year)

        return round(annualized, 4)

    def _sortino_ratio(self, equity_curve: list[float]) -> float:
        """Calculate Sortino ratio (downside deviation only)."""
        if len(equity_curve) < 2:
            return 0.0

        returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        returns = returns[~np.isnan(returns)]

        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return 0.0

        sortino = np.mean(returns) / np.std(downside_returns)
        annualized = sortino * np.sqrt(self.trading_hours_per_year)

        return round(annualized, 4)

    def _max_drawdown(self, equity_curve: list[float]) -> float:
        """Calculate maximum drawdown as decimal."""
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max

        return abs(np.min(drawdown))

    def _profit_factor(self, trades: list[dict]) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(t["pnl_pips"] for t in trades if t["pnl_pips"] > 0)
        gross_loss = abs(sum(t["pnl_pips"] for t in trades if t["pnl_pips"] < 0))

        if gross_loss == 0:
            return 999.0

        return round(gross_profit / gross_loss, 4)

    def _win_rate(self, trades: list[dict]) -> float:
        """Calculate win rate (winners / total trades)."""
        if len(trades) == 0:
            return 0.0

        winners = sum(1 for t in trades if t["pnl_pips"] > 0)
        return winners / len(trades)

    def _calmar_ratio(self, equity_curve: list[float], initial_capital: float) -> float:
        """Calculate Calmar ratio (annual return / max drawdown)."""
        if len(equity_curve) < 2:
            return 0.0

        final_capital = equity_curve[-1]
        years = len(equity_curve) / self.trading_hours_per_year

        if years <= 0:
            return 0.0

        annual_return = (final_capital / initial_capital) ** (1 / years) - 1
        max_dd = self._max_drawdown(equity_curve)

        if max_dd == 0:
            return 0.0

        return round(annual_return / max_dd, 4)

    def _equity_curve_r2(self, equity_curve: list[float]) -> float:
        """Calculate R-squared of equity curve (linearity measure)."""
        if len(equity_curve) < 2:
            return 0.0

        x = np.arange(len(equity_curve))
        y = np.array(equity_curve)

        coeffs = np.polyfit(x, y, 1)
        fitted = np.polyval(coeffs, x)

        ss_res = np.sum((y - fitted) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        if ss_tot == 0:
            return 0.0

        r2 = 1 - ss_res / ss_tot

        return round(r2, 4)

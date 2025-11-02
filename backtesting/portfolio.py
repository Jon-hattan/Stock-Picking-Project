"""
Portfolio construction and management for backtesting.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

from data.fetchers import YFinanceFetcher
from config.settings import settings


class Portfolio:
    """Portfolio manager for backtesting stock selections."""

    def __init__(
        self,
        name: str,
        tickers: List[str],
        start_date: str,
        end_date: str,
        equal_weight: bool = True,
        initial_capital: float = 100000.0
    ):
        """
        Initialize portfolio.

        Args:
            name: Portfolio name
            tickers: List of stock tickers in the portfolio
            start_date: Portfolio start date (YYYY-MM-DD)
            end_date: Portfolio end date (YYYY-MM-DD)
            equal_weight: Whether to use equal weighting (default True)
            initial_capital: Initial investment capital
        """
        self.name = name
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.equal_weight = equal_weight
        self.initial_capital = initial_capital

        self.yfinance = YFinanceFetcher()

        # Portfolio data
        self.price_data: Optional[pd.DataFrame] = None
        self.returns: Optional[pd.DataFrame] = None
        self.portfolio_value: Optional[pd.Series] = None
        self.weights: Dict[str, float] = {}

        # Performance metrics
        self.metrics: Dict[str, Any] = {}

    def load_data(self):
        """Load historical price data for all tickers."""
        print(f"Loading price data for {len(self.tickers)} stocks...")

        price_data = {}

        for ticker in self.tickers:
            try:
                df = self.yfinance.get_historical_data(
                    ticker,
                    start_date=self.start_date,
                    end_date=self.end_date
                )

                if not df.empty:
                    price_data[ticker] = df['Close']
                else:
                    print(f"Warning: No data for {ticker}")

            except Exception as e:
                print(f"Error loading data for {ticker}: {e}")

        if not price_data:
            raise ValueError("No price data could be loaded for any ticker")

        # Combine into single DataFrame
        self.price_data = pd.DataFrame(price_data)

        # Forward fill missing data (for stocks that don't trade on certain days)
        self.price_data = self.price_data.fillna(method='ffill')

        # Set equal weights or calculate custom weights
        if self.equal_weight:
            num_stocks = len(self.price_data.columns)
            self.weights = {ticker: 1.0 / num_stocks for ticker in self.price_data.columns}
        else:
            # Custom weighting logic could go here
            raise NotImplementedError("Custom weighting not yet implemented")

        print(f"Loaded data for {len(self.price_data.columns)} stocks")
        print(f"Date range: {self.price_data.index[0]} to {self.price_data.index[-1]}")

    def calculate_returns(self):
        """Calculate daily returns for each stock and the portfolio."""
        if self.price_data is None:
            self.load_data()

        # Calculate daily returns for each stock
        self.returns = self.price_data.pct_change().dropna()

        # Calculate weighted portfolio returns
        weights_series = pd.Series(self.weights)
        self.portfolio_returns = (self.returns * weights_series).sum(axis=1)

        # Calculate portfolio value over time
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        self.portfolio_value = self.initial_capital * cumulative_returns

        print(f"Calculated returns for {len(self.returns)} trading days")

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.

        Returns:
            Dictionary of performance metrics
        """
        if self.portfolio_returns is None:
            self.calculate_returns()

        # Basic return metrics
        total_return = (self.portfolio_value.iloc[-1] / self.initial_capital) - 1
        num_days = len(self.portfolio_returns)
        annualized_return = (1 + total_return) ** (settings.TRADING_DAYS_PER_YEAR / num_days) - 1

        # Risk metrics
        daily_volatility = self.portfolio_returns.std()
        annualized_volatility = daily_volatility * np.sqrt(settings.TRADING_DAYS_PER_YEAR)

        # Risk-adjusted metrics
        excess_returns = self.portfolio_returns.mean() * settings.TRADING_DAYS_PER_YEAR - settings.RISK_FREE_RATE
        sharpe_ratio = excess_returns / annualized_volatility if annualized_volatility > 0 else 0

        # Drawdown analysis
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # Win rate
        winning_days = (self.portfolio_returns > 0).sum()
        win_rate = winning_days / len(self.portfolio_returns)

        self.metrics = {
            "portfolio_name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "num_stocks": len(self.tickers),
            "tickers": self.tickers,

            # Returns
            "total_return": total_return,
            "annualized_return": annualized_return,
            "final_value": self.portfolio_value.iloc[-1],
            "initial_capital": self.initial_capital,

            # Risk
            "daily_volatility": daily_volatility,
            "annualized_volatility": annualized_volatility,
            "max_drawdown": max_drawdown,

            # Risk-adjusted
            "sharpe_ratio": sharpe_ratio,

            # Trading metrics
            "num_trading_days": num_days,
            "win_rate": win_rate,
        }

        return self.metrics

    def get_rolling_sharpe(self, window: int = None) -> pd.Series:
        """
        Calculate rolling Sharpe ratio.

        Args:
            window: Rolling window size in days (defaults to settings)

        Returns:
            Series of rolling Sharpe ratios
        """
        if window is None:
            window = settings.ROLLING_WINDOW_DAYS

        if self.portfolio_returns is None:
            self.calculate_returns()

        # Calculate rolling mean and std
        rolling_mean = self.portfolio_returns.rolling(window=window).mean()
        rolling_std = self.portfolio_returns.rolling(window=window).std()

        # Annualize
        annualized_mean = rolling_mean * settings.TRADING_DAYS_PER_YEAR
        annualized_std = rolling_std * np.sqrt(settings.TRADING_DAYS_PER_YEAR)

        # Calculate rolling Sharpe
        rolling_sharpe = (annualized_mean - settings.RISK_FREE_RATE) / annualized_std

        return rolling_sharpe

    def summary(self) -> str:
        """
        Get a formatted summary of portfolio performance.

        Returns:
            Formatted summary string
        """
        if not self.metrics:
            self.calculate_metrics()

        summary = f"""
Portfolio Performance Summary: {self.name}
{'=' * 70}

Period: {self.start_date} to {self.end_date}
Number of Stocks: {self.metrics['num_stocks']}
Stocks: {', '.join(self.tickers[:5])}{'...' if len(self.tickers) > 5 else ''}

RETURNS:
  Total Return: {self.metrics['total_return'] * 100:+.2f}%
  Annualized Return: {self.metrics['annualized_return'] * 100:+.2f}%
  Final Value: ${self.metrics['final_value']:,.2f}
  Initial Capital: ${self.metrics['initial_capital']:,.2f}

RISK:
  Annualized Volatility: {self.metrics['annualized_volatility'] * 100:.2f}%
  Maximum Drawdown: {self.metrics['max_drawdown'] * 100:.2f}%

RISK-ADJUSTED:
  Sharpe Ratio: {self.metrics['sharpe_ratio']:.3f}

TRADING STATS:
  Trading Days: {self.metrics['num_trading_days']}
  Win Rate: {self.metrics['win_rate'] * 100:.1f}%
{'=' * 70}
"""
        return summary


def compare_portfolios(portfolios: List[Portfolio]) -> pd.DataFrame:
    """
    Compare multiple portfolios.

    Args:
        portfolios: List of Portfolio objects

    Returns:
        DataFrame with comparison metrics
    """
    comparison_data = []

    for portfolio in portfolios:
        if not portfolio.metrics:
            portfolio.calculate_metrics()

        comparison_data.append({
            "Portfolio": portfolio.name,
            "Total Return (%)": portfolio.metrics["total_return"] * 100,
            "Annualized Return (%)": portfolio.metrics["annualized_return"] * 100,
            "Volatility (%)": portfolio.metrics["annualized_volatility"] * 100,
            "Sharpe Ratio": portfolio.metrics["sharpe_ratio"],
            "Max Drawdown (%)": portfolio.metrics["max_drawdown"] * 100,
            "Num Stocks": portfolio.metrics["num_stocks"],
        })

    df = pd.DataFrame(comparison_data)
    return df.set_index("Portfolio")

"""
Price and volume analysis tools for valuation agent.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from config.settings import settings
from data.fetchers import YFinanceFetcher


class PriceAnalysisTool:
    """Tool for analyzing stock price and volume data."""

    def __init__(self):
        """Initialize price analysis tool."""
        self.yfinance = YFinanceFetcher()

    def get_price_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1y"
    ) -> pd.DataFrame:
        """
        Get historical price data.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period if dates not provided (1mo, 3mo, 6mo, 1y, 2y, etc.)

        Returns:
            DataFrame with OHLCV data
        """
        return self.yfinance.get_historical_data(ticker, start_date, end_date, period)

    def calculate_returns(self, prices: pd.Series) -> Dict[str, float]:
        """
        Calculate various return metrics.

        Args:
            prices: Series of closing prices

        Returns:
            Dictionary with return metrics
        """
        if len(prices) < 2:
            return {
                "cumulative_return": 0.0,
                "annualized_return": 0.0,
                "daily_return_mean": 0.0
            }

        # Calculate returns
        daily_returns = prices.pct_change().dropna()
        cumulative_return = (prices.iloc[-1] / prices.iloc[0]) - 1

        # Annualize the return
        num_days = len(prices)
        annualized_return = (
            (1 + cumulative_return) ** (settings.TRADING_DAYS_PER_YEAR / num_days)
        ) - 1

        return {
            "cumulative_return": cumulative_return,
            "annualized_return": annualized_return,
            "daily_return_mean": daily_returns.mean(),
            "total_days": num_days
        }

    def calculate_volatility(self, prices: pd.Series) -> Dict[str, float]:
        """
        Calculate volatility metrics.

        Args:
            prices: Series of closing prices

        Returns:
            Dictionary with volatility metrics
        """
        if len(prices) < 2:
            return {
                "daily_volatility": 0.0,
                "annualized_volatility": 0.0
            }

        # Calculate daily returns
        daily_returns = prices.pct_change().dropna()

        # Calculate volatility
        daily_volatility = daily_returns.std()
        annualized_volatility = daily_volatility * np.sqrt(settings.TRADING_DAYS_PER_YEAR)

        return {
            "daily_volatility": daily_volatility,
            "annualized_volatility": annualized_volatility
        }

    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (defaults to settings)

        Returns:
            Sharpe ratio
        """
        if risk_free_rate is None:
            risk_free_rate = settings.RISK_FREE_RATE

        if len(returns) < 2:
            return 0.0

        # Annualize returns
        mean_return = returns.mean() * settings.TRADING_DAYS_PER_YEAR
        std_return = returns.std() * np.sqrt(settings.TRADING_DAYS_PER_YEAR)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return sharpe

    def analyze_price_trends(
        self,
        ticker: str,
        period: str = "3mo"
    ) -> Dict[str, Any]:
        """
        Comprehensive price trend analysis.

        Args:
            ticker: Stock ticker symbol
            period: Analysis period (1mo, 3mo, 6mo, 1y, etc.)

        Returns:
            Dictionary with comprehensive analysis
        """
        print(f"Analyzing price trends for {ticker} ({period})...")

        df = self.get_price_data(ticker, period=period)

        if df.empty:
            return {
                "ticker": ticker,
                "period": period,
                "error": "No price data available"
            }

        prices = df['Close']
        volume = df['Volume']

        # Calculate metrics
        returns_metrics = self.calculate_returns(prices)
        volatility_metrics = self.calculate_volatility(prices)
        daily_returns = prices.pct_change().dropna()
        sharpe = self.calculate_sharpe_ratio(daily_returns)

        # Price changes
        start_price = prices.iloc[0]
        end_price = prices.iloc[-1]
        price_change_pct = ((end_price - start_price) / start_price) * 100

        # Volume analysis
        avg_volume = volume.mean()
        recent_volume = volume.iloc[-5:].mean()  # Last 5 days
        volume_trend = "increasing" if recent_volume > avg_volume else "decreasing"

        # Trend analysis (simple moving averages)
        sma_20 = prices.rolling(window=20).mean().iloc[-1] if len(prices) >= 20 else end_price
        sma_50 = prices.rolling(window=50).mean().iloc[-1] if len(prices) >= 50 else end_price

        trend = "upward" if end_price > sma_20 > sma_50 else \
                "downward" if end_price < sma_20 < sma_50 else "neutral"

        analysis = {
            "ticker": ticker,
            "period": period,
            "start_date": df.index[0].strftime("%Y-%m-%d"),
            "end_date": df.index[-1].strftime("%Y-%m-%d"),
            "start_price": start_price,
            "end_price": end_price,
            "price_change_pct": price_change_pct,
            "cumulative_return": returns_metrics["cumulative_return"],
            "annualized_return": returns_metrics["annualized_return"],
            "daily_volatility": volatility_metrics["daily_volatility"],
            "annualized_volatility": volatility_metrics["annualized_volatility"],
            "sharpe_ratio": sharpe,
            "avg_volume": avg_volume,
            "recent_volume": recent_volume,
            "volume_trend": volume_trend,
            "price_trend": trend,
            "sma_20": sma_20 if len(prices) >= 20 else None,
            "sma_50": sma_50 if len(prices) >= 50 else None,
        }

        # Add interpretation
        analysis["interpretation"] = self._interpret_analysis(analysis)

        return analysis

    def _interpret_analysis(self, analysis: Dict[str, Any]) -> str:
        """Create human-readable interpretation of the analysis."""
        ticker = analysis["ticker"]
        period = analysis["period"]
        price_change = analysis["price_change_pct"]
        ann_return = analysis["annualized_return"] * 100
        ann_vol = analysis["annualized_volatility"] * 100
        sharpe = analysis["sharpe_ratio"]
        trend = analysis["price_trend"]

        interpretation = f"""
Price Trend Analysis for {ticker} ({period})
{'=' * 50}

Price Performance:
- Price change: {price_change:+.2f}%
- Annualized return: {ann_return:+.2f}%
- Trend: {trend.upper()}

Risk Metrics:
- Annualized volatility: {ann_vol:.2f}%
- Sharpe ratio: {sharpe:.2f}

Volume Analysis:
- Volume trend: {analysis['volume_trend']}

Investment Implication:
"""

        # Add recommendation based on metrics
        if sharpe > 1.0 and trend == "upward":
            interpretation += "POSITIVE - Strong risk-adjusted returns with upward momentum\n"
        elif sharpe < 0 or trend == "downward":
            interpretation += "NEGATIVE - Poor risk-adjusted returns or downward trend\n"
        else:
            interpretation += "NEUTRAL - Mixed signals, requires further analysis\n"

        # Volatility assessment
        if ann_vol > 40:
            interpretation += f"HIGH RISK - Volatility at {ann_vol:.1f}% is significant\n"
        elif ann_vol > 25:
            interpretation += f"MODERATE RISK - Volatility at {ann_vol:.1f}% is elevated\n"
        else:
            interpretation += f"LOW RISK - Volatility at {ann_vol:.1f}% is manageable\n"

        return interpretation.strip()


# Function to create tool for AutoGen
def create_price_analysis_function(price_tool: PriceAnalysisTool):
    """
    Create a function that can be used as an AutoGen tool.

    Args:
        price_tool: Instance of PriceAnalysisTool

    Returns:
        Function that can be registered with AutoGen
    """
    def analyze_stock_valuation(ticker: str, period: str = "3mo") -> str:
        """
        Analyze stock price trends, volatility, and valuation metrics.

        Args:
            ticker: Stock ticker symbol
            period: Analysis period (1mo, 3mo, 6mo, 1y, 2y, etc.)

        Returns:
            Comprehensive valuation analysis with returns, volatility, and trends
        """
        analysis = price_tool.analyze_price_trends(ticker, period)

        if "error" in analysis:
            return f"Error analyzing {ticker}: {analysis['error']}"

        return analysis.get("interpretation", "Analysis not available")

    return analyze_stock_valuation

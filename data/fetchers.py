"""
Data fetcher classes for various financial data APIs.
"""
import os
import time
import requests
import yfinance as yf
import finnhub
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sec_edgar_downloader import Downloader
from pathlib import Path

from config.settings import settings


class RateLimiter:
    """Simple rate limiter to avoid hitting API limits."""

    def __init__(self, max_calls: int, period: int):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def wait_if_needed(self):
        """Wait if we've hit the rate limit."""
        now = time.time()
        # Remove calls outside the current period
        self.calls = [call_time for call_time in self.calls if now - call_time < self.period]

        if len(self.calls) >= self.max_calls:
            # Wait until the oldest call expires
            sleep_time = self.period - (now - self.calls[0]) + 0.1
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.calls = []

        self.calls.append(now)


class SECEdgarFetcher:
    """Fetcher for SEC EDGAR 10-K and 10-Q filings."""

    def __init__(self):
        """Initialize SEC EDGAR fetcher."""
        self.rate_limiter = RateLimiter(
            max_calls=settings.SEC_RATE_LIMIT,
            period=settings.SEC_RATE_PERIOD
        )
        self.download_folder = Path(settings.DATA_CACHE_DIR) / "sec_filings"
        self.download_folder.mkdir(parents=True, exist_ok=True)

        self.downloader = Downloader(
            company_name="AlphaAgents",
            email_address="contact@example.com",
            download_folder=str(self.download_folder)
        )

    def get_filing(self, ticker: str, filing_type: str = "10-K", limit: int = 1) -> Optional[Path]:
        """
        Download SEC filing for a given ticker.

        Args:
            ticker: Stock ticker symbol
            filing_type: Type of filing (10-K or 10-Q)
            limit: Number of most recent filings to download

        Returns:
            Path to the downloaded filing directory
        """
        self.rate_limiter.wait_if_needed()

        try:
            self.downloader.get(filing_type, ticker, limit=limit)
            filing_path = self.download_folder / ticker / filing_type
            return filing_path if filing_path.exists() else None
        except Exception as e:
            print(f"Error downloading {filing_type} for {ticker}: {e}")
            return None

    def get_latest_10k(self, ticker: str) -> Optional[Path]:
        """Get the most recent 10-K filing."""
        return self.get_filing(ticker, "10-K", limit=1)

    def get_latest_10q(self, ticker: str) -> Optional[Path]:
        """Get the most recent 10-Q filing."""
        return self.get_filing(ticker, "10-Q", limit=1)


class FinnhubFetcher:
    """Fetcher for Finnhub financial news and sentiment data."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Finnhub fetcher.

        Args:
            api_key: Finnhub API key (defaults to settings)
        """
        self.api_key = api_key or settings.FINNHUB_API_KEY
        if not self.api_key:
            raise ValueError("Finnhub API key is required")

        self.client = finnhub.Client(api_key=self.api_key)
        self.rate_limiter = RateLimiter(
            max_calls=settings.FINNHUB_RATE_LIMIT,
            period=settings.FINNHUB_RATE_PERIOD
        )

    def get_company_news(
        self,
        ticker: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get company news from Finnhub.

        Args:
            ticker: Stock ticker symbol
            from_date: Start date (YYYY-MM-DD format)
            to_date: End date (YYYY-MM-DD format)

        Returns:
            List of news articles
        """
        self.rate_limiter.wait_if_needed()

        # Default to last 30 days if no dates provided
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            news = self.client.company_news(ticker, _from=from_date, to=to_date)
            return news
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []

    def get_basic_financials(self, ticker: str) -> Dict[str, Any]:
        """
        Get basic financial metrics.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary of financial metrics
        """
        self.rate_limiter.wait_if_needed()

        try:
            financials = self.client.company_basic_financials(ticker, "all")
            return financials
        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return {}


class YFinanceFetcher:
    """Fetcher for Yahoo Finance historical price data."""

    def __init__(self):
        """Initialize Yahoo Finance fetcher."""
        self.rate_limiter = RateLimiter(
            max_calls=settings.YFINANCE_RATE_LIMIT,
            period=settings.YFINANCE_RATE_PERIOD
        )

    def get_historical_data(
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
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            period: Period (if dates not provided): 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

        Returns:
            DataFrame with OHLCV data
        """
        self.rate_limiter.wait_if_needed()

        try:
            stock = yf.Ticker(ticker)
            if start_date and end_date:
                df = stock.history(start=start_date, end=end_date)
            else:
                df = stock.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return pd.DataFrame()

    def get_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get stock information.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary of stock info
        """
        self.rate_limiter.wait_if_needed()

        try:
            stock = yf.Ticker(ticker)
            return stock.info
        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
            return {}

    def get_financials(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Get financial statements.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with income_stmt, balance_sheet, cash_flow
        """
        self.rate_limiter.wait_if_needed()

        try:
            stock = yf.Ticker(ticker)
            return {
                "income_stmt": stock.income_stmt,
                "balance_sheet": stock.balance_sheet,
                "cash_flow": stock.cashflow
            }
        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return {}


class FMPFetcher:
    """Fetcher for Financial Modeling Prep API (optional, for enhanced fundamentals)."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP fetcher.

        Args:
            api_key: FMP API key (defaults to settings)
        """
        self.api_key = api_key or settings.FMP_API_KEY
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.rate_limiter = RateLimiter(
            max_calls=settings.FMP_RATE_LIMIT,
            period=settings.FMP_RATE_PERIOD
        )

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make API request to FMP."""
        if not self.api_key:
            print("Warning: FMP API key not set. Skipping FMP data fetch.")
            return None

        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params["apikey"] = self.api_key

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making FMP request to {endpoint}: {e}")
            return None

    def get_financial_ratios(self, ticker: str) -> Optional[List[Dict]]:
        """Get financial ratios for a company."""
        return self._make_request(f"ratios/{ticker}")

    def get_key_metrics(self, ticker: str) -> Optional[List[Dict]]:
        """Get key metrics for a company."""
        return self._make_request(f"key-metrics/{ticker}")

    def get_income_statement(self, ticker: str, period: str = "annual") -> Optional[List[Dict]]:
        """Get income statement."""
        return self._make_request(f"income-statement/{ticker}", {"period": period})

    def get_balance_sheet(self, ticker: str, period: str = "annual") -> Optional[List[Dict]]:
        """Get balance sheet."""
        return self._make_request(f"balance-sheet-statement/{ticker}", {"period": period})

    def get_cash_flow(self, ticker: str, period: str = "annual") -> Optional[List[Dict]]:
        """Get cash flow statement."""
        return self._make_request(f"cash-flow-statement/{ticker}", {"period": period})


# Factory function to get all fetchers
def get_fetchers() -> Dict[str, Any]:
    """
    Get instances of all data fetchers.

    Returns:
        Dictionary with fetcher instances
    """
    fetchers = {
        "sec": SECEdgarFetcher(),
        "finnhub": FinnhubFetcher() if settings.FINNHUB_API_KEY else None,
        "yfinance": YFinanceFetcher(),
        "fmp": FMPFetcher() if settings.FMP_API_KEY else None
    }

    return {k: v for k, v in fetchers.items() if v is not None}

"""
Fundamental analysis tool for financial metrics and ratios.
"""
from typing import Dict, Any, Optional, List
import pandas as pd

from data.fetchers import YFinanceFetcher, FMPFetcher


class FundamentalAnalysisTool:
    """Tool for analyzing fundamental financial metrics."""

    def __init__(self):
        """Initialize fundamental analysis tool."""
        self.yfinance = YFinanceFetcher()
        self.fmp = FMPFetcher()

    def get_financial_statements(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Get financial statements from yfinance.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with income statement, balance sheet, cash flow
        """
        return self.yfinance.get_financials(ticker)

    def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get company information.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with company info
        """
        return self.yfinance.get_info(ticker)

    def calculate_key_ratios(self, ticker: str) -> Dict[str, Any]:
        """
        Calculate key financial ratios.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with financial ratios
        """
        print(f"Calculating fundamental ratios for {ticker}...")

        # Get company info
        info = self.get_company_info(ticker)

        if not info:
            return {"error": f"No fundamental data available for {ticker}"}

        # Extract key metrics (yfinance provides many calculated metrics)
        ratios = {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),

            # Valuation ratios
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),

            # Profitability ratios
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),

            # Growth metrics
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "revenue": info.get("totalRevenue"),
            "earnings": info.get("netIncomeToCommon"),

            # Financial health
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "debt_to_equity": info.get("debtToEquity"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            "free_cash_flow": info.get("freeCashflow"),
            "operating_cash_flow": info.get("operatingCashflow"),

            # Dividend info
            "dividend_yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),

            # Analyst recommendations
            "target_mean_price": info.get("targetMeanPrice"),
            "recommendation": info.get("recommendationKey"),
            "num_analyst_opinions": info.get("numberOfAnalystOpinions"),
        }

        return ratios

    def analyze_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        Comprehensive fundamental analysis.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with comprehensive fundamental analysis
        """
        ratios = self.calculate_key_ratios(ticker)

        if "error" in ratios:
            return ratios

        # Add interpretation
        ratios["interpretation"] = self._interpret_fundamentals(ratios)
        ratios["score"] = self._score_fundamentals(ratios)

        return ratios

    def _score_fundamentals(self, ratios: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score fundamental metrics (simple scoring system).

        Args:
            ratios: Dictionary of financial ratios

        Returns:
            Dictionary with scores
        """
        scores = {
            "valuation": 0,  # -5 to +5
            "profitability": 0,  # -5 to +5
            "growth": 0,  # -5 to +5
            "financial_health": 0,  # -5 to +5
            "overall": 0  # Average
        }

        # Valuation scoring (lower is better for value investors)
        pe = ratios.get("pe_ratio")
        if pe is not None:
            if pe < 15:
                scores["valuation"] += 2
            elif pe < 25:
                scores["valuation"] += 1
            elif pe > 40:
                scores["valuation"] -= 2

        pb = ratios.get("price_to_book")
        if pb is not None:
            if pb < 1.5:
                scores["valuation"] += 2
            elif pb < 3:
                scores["valuation"] += 1
            elif pb > 5:
                scores["valuation"] -= 2

        # Profitability scoring
        profit_margin = ratios.get("profit_margin")
        if profit_margin is not None:
            if profit_margin > 0.20:  # 20%+
                scores["profitability"] += 2
            elif profit_margin > 0.10:  # 10%+
                scores["profitability"] += 1
            elif profit_margin < 0:  # Negative
                scores["profitability"] -= 3

        roe = ratios.get("roe")
        if roe is not None:
            if roe > 0.20:  # 20%+
                scores["profitability"] += 2
            elif roe > 0.15:  # 15%+
                scores["profitability"] += 1
            elif roe < 0.05:  # < 5%
                scores["profitability"] -= 2

        # Growth scoring
        revenue_growth = ratios.get("revenue_growth")
        if revenue_growth is not None:
            if revenue_growth > 0.20:  # 20%+
                scores["growth"] += 3
            elif revenue_growth > 0.10:  # 10%+
                scores["growth"] += 2
            elif revenue_growth < 0:  # Negative
                scores["growth"] -= 2

        earnings_growth = ratios.get("earnings_growth")
        if earnings_growth is not None:
            if earnings_growth > 0.20:  # 20%+
                scores["growth"] += 2
            elif earnings_growth > 0.10:  # 10%+
                scores["growth"] += 1
            elif earnings_growth < 0:  # Negative
                scores["growth"] -= 2

        # Financial health scoring
        current_ratio = ratios.get("current_ratio")
        if current_ratio is not None:
            if current_ratio > 2.0:
                scores["financial_health"] += 2
            elif current_ratio > 1.5:
                scores["financial_health"] += 1
            elif current_ratio < 1.0:
                scores["financial_health"] -= 2

        debt_to_equity = ratios.get("debt_to_equity")
        if debt_to_equity is not None:
            if debt_to_equity < 0.5:
                scores["financial_health"] += 2
            elif debt_to_equity < 1.0:
                scores["financial_health"] += 1
            elif debt_to_equity > 2.0:
                scores["financial_health"] -= 2

        # Calculate overall score
        score_values = [v for k, v in scores.items() if k != "overall"]
        scores["overall"] = sum(score_values) / len(score_values) if score_values else 0

        return scores

    def _interpret_fundamentals(self, ratios: Dict[str, Any]) -> str:
        """Create human-readable interpretation."""
        ticker = ratios["ticker"]
        company = ratios.get("company_name", ticker)
        sector = ratios.get("sector", "Unknown")

        interpretation = f"""
Fundamental Analysis for {company} ({ticker})
{'=' * 60}
Sector: {sector}

VALUATION METRICS:
"""

        # Valuation
        pe = ratios.get("pe_ratio")
        if pe:
            interpretation += f"- P/E Ratio: {pe:.2f}"
            if pe < 15:
                interpretation += " (Undervalued)\n"
            elif pe < 25:
                interpretation += " (Fair value)\n"
            else:
                interpretation += " (Potentially overvalued)\n"

        pb = ratios.get("price_to_book")
        if pb:
            interpretation += f"- Price/Book: {pb:.2f}\n"

        ps = ratios.get("price_to_sales")
        if ps:
            interpretation += f"- Price/Sales: {ps:.2f}\n"

        # Profitability
        interpretation += "\nPROFITABILITY:\n"

        profit_margin = ratios.get("profit_margin")
        if profit_margin:
            interpretation += f"- Net Profit Margin: {profit_margin * 100:.2f}%\n"

        operating_margin = ratios.get("operating_margin")
        if operating_margin:
            interpretation += f"- Operating Margin: {operating_margin * 100:.2f}%\n"

        roe = ratios.get("roe")
        if roe:
            interpretation += f"- Return on Equity: {roe * 100:.2f}%\n"

        # Growth
        interpretation += "\nGROWTH:\n"

        rev_growth = ratios.get("revenue_growth")
        if rev_growth:
            interpretation += f"- Revenue Growth: {rev_growth * 100:.+.2f}%\n"

        earnings_growth = ratios.get("earnings_growth")
        if earnings_growth:
            interpretation += f"- Earnings Growth: {earnings_growth * 100:.+.2f}%\n"

        # Financial Health
        interpretation += "\nFINANCIAL HEALTH:\n"

        current_ratio = ratios.get("current_ratio")
        if current_ratio:
            interpretation += f"- Current Ratio: {current_ratio:.2f}"
            interpretation += " (Strong)\n" if current_ratio > 1.5 else " (Weak)\n"

        debt_equity = ratios.get("debt_to_equity")
        if debt_equity:
            interpretation += f"- Debt/Equity: {debt_equity:.2f}"
            interpretation += " (Low debt)\n" if debt_equity < 1.0 else " (High debt)\n"

        fcf = ratios.get("free_cash_flow")
        if fcf:
            interpretation += f"- Free Cash Flow: ${fcf / 1e9:.2f}B\n"

        return interpretation.strip()


# Function to create tool for AutoGen
def create_fundamental_analysis_function(fundamental_tool: FundamentalAnalysisTool):
    """
    Create a function that can be used as an AutoGen tool.

    Args:
        fundamental_tool: Instance of FundamentalAnalysisTool

    Returns:
        Function that can be registered with AutoGen
    """
    def analyze_fundamentals(ticker: str) -> str:
        """
        Analyze fundamental financial metrics and ratios for a stock.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Comprehensive fundamental analysis with valuation, profitability, growth, and health metrics
        """
        analysis = fundamental_tool.analyze_fundamentals(ticker)

        if "error" in analysis:
            return f"Error analyzing {ticker}: {analysis['error']}"

        return analysis.get("interpretation", "Analysis not available")

    return analyze_fundamentals

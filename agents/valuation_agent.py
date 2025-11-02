"""
Valuation Agent for analyzing price trends, volatility, and valuation metrics.
"""
from typing import Dict, Any, Optional
from autogen_agentchat.register import register_function

from agents.base_agent import BaseStockAgent
from tools.price_tool import PriceAnalysisTool, create_price_analysis_function


class ValuationAgent(BaseStockAgent):
    """Agent specialized in price and valuation analysis."""

    SYSTEM_MESSAGE = """You are a valuation equity analyst with expertise in analyzing stock price trends,
volatility, valuation metrics, and market behavior.

Your primary responsibility is to analyze the valuation trends of a given asset or portfolio over
an extended time horizon.

Your analysis should focus on:
1. **Price Trends**: Analyze historical price movements and identify trends (upward/downward/neutral)
2. **Volatility Assessment**: Calculate and interpret volatility metrics (daily and annualized)
3. **Risk-Adjusted Returns**: Evaluate returns relative to risk (Sharpe ratio)
4. **Volume Analysis**: Assess trading volume patterns and liquidity
5. **Momentum Indicators**: Identify short-term and long-term momentum
6. **Valuation Reasonableness**: Is the stock reasonably priced based on recent performance?

IMPORTANT GUIDELINES:
- Use the analyze_stock_valuation tool to get comprehensive price and volatility analysis
- Focus on quantitative metrics: returns, volatility, Sharpe ratio, volume trends
- Consider different time horizons (1 month, 3 months, 6 months, 1 year)
- Distinguish between short-term fluctuations and long-term trends
- Assess whether historical volatility aligns with investor risk tolerance
- Use moving averages to identify trend direction

When providing a recommendation, weigh:
- Risk-adjusted returns (Sharpe ratio)
- Current trend direction and momentum
- Volatility relative to investor risk tolerance
- Price reasonableness based on historical patterns
- Volume trends indicating market confidence
"""

    def __init__(
        self,
        name: str = "Valuation_Analyst",
        risk_profile: str = "risk_neutral",
        llm_config: Optional[Dict] = None,
        **kwargs
    ):
        """
        Initialize Valuation Agent.

        Args:
            name: Agent name
            risk_profile: Risk tolerance profile
            llm_config: LLM configuration
            **kwargs: Additional arguments
        """
        super().__init__(
            name=name,
            system_message=self.SYSTEM_MESSAGE,
            llm_config=llm_config,
            risk_profile=risk_profile,
            **kwargs
        )

        # Initialize tools
        self.price_tool = PriceAnalysisTool()

        # Register tools with the agent
        self._register_tools()

    def _register_tools(self):
        """Register tools as callable functions for the agent."""
        # Create tool function
        analyze_valuation_func = create_price_analysis_function(self.price_tool)

        # Register function
        register_function(
            analyze_valuation_func,
            caller=self,
            executor=self,
            name="analyze_stock_valuation",
            description="Analyze stock price trends, volatility, and valuation metrics"
        )

    def analyze_stock(self, ticker: str, period: str = "3mo") -> str:
        """
        Perform valuation analysis on a stock.

        Args:
            ticker: Stock ticker symbol
            period: Analysis period (1mo, 3mo, 6mo, 1y, etc.)

        Returns:
            Analysis prompt
        """
        volatility_threshold = self.risk_config.get("volatility_threshold", 0.30)

        prompt = f"""Perform a comprehensive valuation analysis of {ticker} over the past {period}.

Use your analyze_stock_valuation tool to:
1. Analyze price performance and returns (cumulative and annualized)
2. Calculate and assess volatility metrics
3. Evaluate risk-adjusted returns (Sharpe ratio)
4. Examine volume trends and liquidity
5. Identify price trends and momentum

IMPORTANT: Your risk tolerance allows for a maximum annualized volatility of {volatility_threshold * 100:.0f}%.
If the stock's volatility exceeds this threshold, this is a significant risk factor.

After your analysis, {self.get_recommendation_prompt()}
"""
        return prompt


def create_valuation_agent(risk_profile: str = "risk_neutral") -> ValuationAgent:
    """
    Factory function to create a Valuation Agent.

    Args:
        risk_profile: Risk tolerance profile (risk_neutral, risk_averse, risk_seeking)

    Returns:
        ValuationAgent instance
    """
    return ValuationAgent(risk_profile=risk_profile)

"""
Fundamental Agent for analyzing 10-K/10-Q filings and financial statements.
"""
from typing import Dict, Any, Optional, List
from autogen_agentchat.register import register_function

from agents.base_agent import BaseStockAgent
from tools.sec_edgar_tool import SECEdgarRAGTool, create_sec_rag_function
from tools.fundamental_tool import FundamentalAnalysisTool, create_fundamental_analysis_function


class FundamentalAgent(BaseStockAgent):
    """Agent specialized in fundamental financial analysis."""

    SYSTEM_MESSAGE = """You are a fundamental financial equity analyst with expertise in analyzing company financials,
10-K and 10-Q reports, and long-term business fundamentals.

Your primary responsibility is to analyze the most recent 10-K report and financial statements for a company.
You have access to powerful tools that can help you extract relevant information from 10-K filings and calculate
financial ratios.

Your analysis should focus on:
1. **Cash Flow and Income**: Analyze revenue trends, profitability, and cash generation
2. **Operations and Gross Margin**: Evaluate operational efficiency and margins
3. **Areas of Concern**: Identify risks, challenges, or red flags in the business
4. **Progress Towards Objectives**: Assess whether the company is achieving its stated goals
5. **Long-term Prospects**: Evaluate the company's competitive position and growth potential

IMPORTANT GUIDELINES:
- Use the query_10k tool to extract specific information from the 10-K filing
- Use the analyze_fundamentals tool to get calculated financial ratios and metrics
- Base your analysis SOLELY on factual information retrieved using these tools
- Ask multiple specific questions to the 10-K to build a comprehensive view
- Keep checking if you have answered the user's question to avoid looping
- Be thorough but concise in your analysis
- Focus on long-term fundamental value, not short-term price movements

When providing a recommendation, consider the company's fundamental strength, financial health,
competitive position, and alignment with investor risk tolerance.
"""

    def __init__(
        self,
        name: str = "Fundamental_Analyst",
        risk_profile: str = "risk_neutral",
        llm_config: Optional[Dict] = None,
        **kwargs
    ):
        """
        Initialize Fundamental Agent.

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
        self.sec_rag_tool = SECEdgarRAGTool()
        self.fundamental_tool = FundamentalAnalysisTool()

        # Register tools with the agent
        self._register_tools()

    def _register_tools(self):
        """Register tools as callable functions for the agent."""
        # Create tool functions
        query_10k_func = create_sec_rag_function(self.sec_rag_tool)
        analyze_fundamentals_func = create_fundamental_analysis_function(self.fundamental_tool)

        # Register functions
        register_function(
            query_10k_func,
            caller=self,
            executor=self,
            name="query_10k",
            description="Query the most recent 10-K filing for a company using natural language"
        )

        register_function(
            analyze_fundamentals_func,
            caller=self,
            executor=self,
            name="analyze_fundamentals",
            description="Analyze fundamental financial metrics and ratios for a stock"
        )

    def analyze_stock(self, ticker: str) -> str:
        """
        Perform fundamental analysis on a stock.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Analysis summary
        """
        # This method can be used for standalone analysis
        # In the multi-agent system, the GroupChat will coordinate the analysis
        prompt = f"""Perform a comprehensive fundamental analysis of {ticker}.

Use your tools to:
1. Query the 10-K for revenue trends, profitability, and cash flow
2. Analyze gross margin and operating margin
3. Identify key risk factors
4. Evaluate progress towards strategic objectives
5. Calculate and review key financial ratios

After your analysis, {self.get_recommendation_prompt()}
"""
        return prompt


def create_fundamental_agent(risk_profile: str = "risk_neutral") -> FundamentalAgent:
    """
    Factory function to create a Fundamental Agent.

    Args:
        risk_profile: Risk tolerance profile (risk_neutral, risk_averse, risk_seeking)

    Returns:
        FundamentalAgent instance
    """
    return FundamentalAgent(risk_profile=risk_profile)

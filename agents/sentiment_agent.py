"""
Sentiment Agent for analyzing financial news and market sentiment.
"""
from typing import Dict, Any, Optional
from autogen_agentchat.register import register_function

from agents.base_agent import BaseStockAgent
from tools.news_tool import NewsSummarizationTool, create_news_sentiment_function


class SentimentAgent(BaseStockAgent):
    """Agent specialized in news sentiment analysis."""

    SYSTEM_MESSAGE = """You are a sentiment equity analyst with expertise in analyzing financial news,
analyst ratings, and market sentiment.

Your primary responsibility is to analyze the financial news, analyst ratings, and disclosures
related to the underlying security and assess its implications and sentiment for investors.

Your analysis should focus on:
1. **Market Sentiment**: What is the overall sentiment from recent news (positive/negative/neutral)?
2. **Analyst Ratings**: Are analysts upgrading or downgrading the stock?
3. **Company Disclosures**: Any significant insider trading, executive changes, or announcements?
4. **News Impact**: How might recent news affect stock performance in the short to medium term?
5. **Pattern Recognition**: Are there recurring themes or trends in the news coverage?

IMPORTANT GUIDELINES:
- Use the analyze_news_sentiment tool to get comprehensive news analysis
- Consider both the quantity and quality of news coverage
- Pay attention to the timing of news (recent vs. older)
- Distinguish between company-specific news and sector-wide trends
- Be objective - don't let individual headlines bias your overall assessment
- Consider the credibility of news sources

When providing a recommendation, weigh:
- Overall sentiment trend (improving vs. deteriorating)
- Significance of recent news events
- Alignment with investor risk tolerance
- Potential for sentiment-driven price movements
"""

    def __init__(
        self,
        name: str = "Sentiment_Analyst",
        risk_profile: str = "risk_neutral",
        llm_config: Optional[Dict] = None,
        **kwargs
    ):
        """
        Initialize Sentiment Agent.

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
        self.news_tool = NewsSummarizationTool()

        # Register tools with the agent
        self._register_tools()

    def _register_tools(self):
        """Register tools as callable functions for the agent."""
        # Create tool function
        analyze_news_func = create_news_sentiment_function(self.news_tool)

        # Register function
        register_function(
            analyze_news_func,
            caller=self,
            executor=self,
            name="analyze_news_sentiment",
            description="Analyze sentiment from recent financial news for a stock"
        )

    def analyze_stock(self, ticker: str, days_back: int = 30) -> str:
        """
        Perform sentiment analysis on a stock.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days of news to analyze

        Returns:
            Analysis prompt
        """
        prompt = f"""Perform a comprehensive sentiment analysis of {ticker} based on recent news.

Use your analyze_news_sentiment tool to:
1. Gather and analyze news from the last {days_back} days
2. Assess the overall sentiment (positive, negative, neutral)
3. Identify significant news events and their potential impact
4. Evaluate analyst sentiment and rating changes
5. Look for patterns or trends in news coverage

After your analysis, {self.get_recommendation_prompt()}

Note: If there is insufficient news coverage, acknowledge this limitation in your analysis.
"""
        return prompt


def create_sentiment_agent(risk_profile: str = "risk_neutral") -> SentimentAgent:
    """
    Factory function to create a Sentiment Agent.

    Args:
        risk_profile: Risk tolerance profile (risk_neutral, risk_averse, risk_seeking)

    Returns:
        SentimentAgent instance
    """
    return SentimentAgent(risk_profile=risk_profile)

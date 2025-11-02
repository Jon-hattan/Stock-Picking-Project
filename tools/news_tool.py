"""
News summarization tool with reflection-enhanced prompting for sentiment analysis.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI

from config.settings import settings
from data.fetchers import FinnhubFetcher


class NewsSummarizationTool:
    """Tool for summarizing financial news and extracting sentiment."""

    def __init__(self):
        """Initialize news summarization tool."""
        self.finnhub = FinnhubFetcher()
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_news(
        self,
        ticker: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent news for a ticker.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back

        Returns:
            List of news articles
        """
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        news = self.finnhub.get_company_news(ticker, from_date, to_date)
        return news

    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, str]:
        """
        Summarize a single news article with reflection-enhanced prompting.

        Args:
            article: News article dictionary

        Returns:
            Dictionary with summary and sentiment
        """
        headline = article.get("headline", "")
        summary_text = article.get("summary", "")
        source = article.get("source", "Unknown")
        date = datetime.fromtimestamp(article.get("datetime", 0)).strftime("%Y-%m-%d")

        # Reflection-enhanced prompt
        prompt = f"""You are a financial analyst analyzing news articles for investment insights.

Article Information:
- Headline: {headline}
- Date: {date}
- Source: {source}
- Summary: {summary_text}

Your task is to:
1. First, summarize the key points of this article in 2-3 sentences
2. Then, critically evaluate: What is the sentiment (positive, negative, or neutral) toward the stock?
3. Finally, provide a concise recommendation on whether this news suggests buying, selling, or holding the stock

Think through each step carefully before providing your final summary and recommendation.

Provide your response in this format:
SUMMARY: [Your 2-3 sentence summary]
SENTIMENT: [Positive/Negative/Neutral]
RECOMMENDATION: [Buy/Sell/Hold]
REASONING: [Brief explanation of your recommendation]
"""

        try:
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )

            analysis = response.choices[0].message.content
            return {
                "headline": headline,
                "date": date,
                "source": source,
                "analysis": analysis,
                "original_summary": summary_text
            }

        except Exception as e:
            print(f"Error summarizing article: {e}")
            return {
                "headline": headline,
                "date": date,
                "source": source,
                "analysis": "Error processing article",
                "original_summary": summary_text
            }

    def analyze_news_sentiment(
        self,
        ticker: str,
        days_back: int = 30,
        max_articles: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze overall sentiment from recent news.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            max_articles: Maximum number of articles to analyze

        Returns:
            Dictionary with overall sentiment analysis
        """
        print(f"Fetching news for {ticker} (last {days_back} days)...")
        news_articles = self.get_news(ticker, days_back)

        if not news_articles:
            return {
                "ticker": ticker,
                "num_articles": 0,
                "overall_sentiment": "neutral",
                "recommendation": "hold",
                "summary": f"No recent news found for {ticker} in the last {days_back} days."
            }

        # Limit to most recent articles
        news_articles = sorted(
            news_articles,
            key=lambda x: x.get("datetime", 0),
            reverse=True
        )[:max_articles]

        print(f"Analyzing {len(news_articles)} news articles...")

        # Summarize each article
        article_summaries = []
        for article in news_articles:
            summary = self.summarize_article(article)
            article_summaries.append(summary)

        # Aggregate sentiment
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        recommendation_counts = {"buy": 0, "sell": 0, "hold": 0}

        for summary in article_summaries:
            analysis = summary.get("analysis", "").lower()

            # Count sentiments
            if "sentiment: positive" in analysis:
                sentiment_counts["positive"] += 1
            elif "sentiment: negative" in analysis:
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1

            # Count recommendations
            if "recommendation: buy" in analysis:
                recommendation_counts["buy"] += 1
            elif "recommendation: sell" in analysis:
                recommendation_counts["sell"] += 1
            else:
                recommendation_counts["hold"] += 1

        # Determine overall sentiment
        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        overall_recommendation = max(recommendation_counts, key=recommendation_counts.get)

        return {
            "ticker": ticker,
            "num_articles": len(news_articles),
            "date_range": f"{days_back} days",
            "overall_sentiment": overall_sentiment,
            "sentiment_breakdown": sentiment_counts,
            "overall_recommendation": overall_recommendation,
            "recommendation_breakdown": recommendation_counts,
            "article_summaries": article_summaries,
            "summary_text": self._create_summary_text(
                ticker, article_summaries, overall_sentiment, overall_recommendation
            )
        }

    def _create_summary_text(
        self,
        ticker: str,
        summaries: List[Dict],
        sentiment: str,
        recommendation: str
    ) -> str:
        """Create a human-readable summary text."""
        summary = f"News Sentiment Analysis for {ticker}\n"
        summary += f"=" * 50 + "\n\n"
        summary += f"Analyzed {len(summaries)} recent news articles\n"
        summary += f"Overall Sentiment: {sentiment.upper()}\n"
        summary += f"Overall Recommendation: {recommendation.upper()}\n\n"
        summary += "Recent Headlines:\n"

        for i, article_summary in enumerate(summaries[:5], 1):
            summary += f"\n{i}. {article_summary['headline']} ({article_summary['date']})\n"
            summary += f"   Source: {article_summary['source']}\n"
            if "SUMMARY:" in article_summary['analysis']:
                # Extract just the summary part
                parts = article_summary['analysis'].split("SENTIMENT:")
                if parts:
                    clean_summary = parts[0].replace("SUMMARY:", "").strip()
                    summary += f"   {clean_summary}\n"

        return summary


# Function to create tool for AutoGen
def create_news_sentiment_function(news_tool: NewsSummarizationTool):
    """
    Create a function that can be used as an AutoGen tool.

    Args:
        news_tool: Instance of NewsSummarizationTool

    Returns:
        Function that can be registered with AutoGen
    """
    def analyze_news_sentiment(ticker: str, days_back: int = 30) -> str:
        """
        Analyze sentiment from recent financial news for a stock.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days of news to analyze (default: 30)

        Returns:
            Summary of news sentiment and investment recommendation
        """
        result = news_tool.analyze_news_sentiment(ticker, days_back)
        return result.get("summary_text", "No news analysis available.")

    return analyze_news_sentiment

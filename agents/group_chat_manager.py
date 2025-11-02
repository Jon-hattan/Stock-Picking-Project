"""
Group Chat Manager for coordinating multi-agent collaboration and debate.
"""
from typing import List, Dict, Any, Optional
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.teams import GroupChat, GroupChatManager

from config.settings import settings
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.valuation_agent import ValuationAgent


class AlphaAgentsGroupChat:
    """Manager for multi-agent stock analysis with collaboration and debate."""

    def __init__(
        self,
        risk_profile: str = "risk_neutral",
        mode: str = "collaboration"
    ):
        """
        Initialize AlphaAgents group chat.

        Args:
            risk_profile: Risk tolerance profile for all agents
            mode: 'collaboration' or 'debate'
        """
        self.risk_profile = risk_profile
        self.mode = mode

        # Create specialist agents
        self.fundamental_agent = FundamentalAgent(risk_profile=risk_profile)
        self.sentiment_agent = SentimentAgent(risk_profile=risk_profile)
        self.valuation_agent = ValuationAgent(risk_profile=risk_profile)

        # Create user proxy for initiating conversations
        self.user_proxy = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )

        # Create group chat
        self.agents = [
            self.fundamental_agent,
            self.sentiment_agent,
            self.valuation_agent
        ]

        self.group_chat = None
        self.manager = None

        self._setup_group_chat()

    def _setup_group_chat(self):
        """Set up the group chat with appropriate configuration."""
        if self.mode == "collaboration":
            system_message = self._get_collaboration_system_message()
            max_round = 10
        else:  # debate mode
            system_message = self._get_debate_system_message()
            max_round = settings.MAX_DEBATE_ROUNDS * 3  # Each agent gets multiple turns

        self.group_chat = GroupChat(
            agents=self.agents,
            messages=[],
            max_round=max_round,
            speaker_selection_method="round_robin"
        )

        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config={"config_list": settings.AUTOGEN_CONFIG_LIST},
            system_message=system_message
        )

    def _get_collaboration_system_message(self) -> str:
        """Get system message for collaboration mode."""
        return f"""You are coordinating a group of equity analysts to perform comprehensive stock analysis.

The team consists of:
1. **Fundamental Analyst**: Analyzes 10-K filings, financial statements, and long-term business fundamentals
2. **Sentiment Analyst**: Analyzes financial news, analyst ratings, and market sentiment
3. **Valuation Analyst**: Analyzes price trends, volatility, and valuation metrics

COLLABORATION PROTOCOL:
- Each analyst must contribute their specialized analysis at least {settings.MIN_AGENT_TURNS} times
- Analysts should build on each other's insights
- After all analysts have contributed, consolidate their inputs into a comprehensive report
- The report should synthesize all three perspectives

When all analysts have provided their analysis, create a final summary report that includes:
1. Executive Summary
2. Fundamental Analysis highlights
3. Sentiment Analysis highlights
4. Valuation Analysis highlights
5. Synthesis of all perspectives
6. Overall investment outlook

Reply "TERMINATE" when the comprehensive report is complete.
"""

    def _get_debate_system_message(self) -> str:
        """Get system message for debate mode."""
        return f"""You are coordinating a group of equity analysts to debate whether to BUY or SELL a stock.

The team consists of:
1. **Fundamental Analyst**: Analyzes based on company fundamentals
2. **Sentiment Analyst**: Analyzes based on market sentiment and news
3. **Valuation Analyst**: Analyzes based on price trends and risk metrics

DEBATE PROTOCOL:
- Each analyst must present their perspective at least {settings.MIN_AGENT_TURNS} times
- Analysts may disagree based on their specialized viewpoints
- Analysts should address concerns raised by others
- Continue the discussion until consensus is reached on BUY or SELL
- You must invoke all agents before deciding to terminate

CONSENSUS CRITERIA:
- At least 2 out of 3 analysts must agree on BUY or SELL
- Dissenting analysts must acknowledge the majority view
- If no consensus after {settings.MAX_DEBATE_ROUNDS} rounds, default to HOLD/SELL (conservative approach)

When consensus is reached, summarize:
1. Final decision (BUY or SELL)
2. Voting breakdown
3. Key reasons supporting the decision
4. Dissenting views (if any)
5. Confidence level

Reply "TERMINATE" when consensus is reached and decision is documented.
"""

    def analyze_stock_collaboration(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze a stock using collaboration mode.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with analysis results and conversation history
        """
        print(f"\n{'=' * 70}")
        print(f"MULTI-AGENT COLLABORATION: Analyzing {ticker}")
        print(f"Risk Profile: {self.risk_profile}")
        print(f"{'=' * 70}\n")

        # Create initial message
        initial_message = f"""Please perform a comprehensive stock analysis of {ticker}.

Each analyst should:
1. Use your specialized tools to gather data
2. Perform your analysis from your perspective
3. Provide insights and recommendations

Fundamental Analyst: Analyze the company's 10-K filing and financial metrics.
Sentiment Analyst: Analyze recent news and market sentiment.
Valuation Analyst: Analyze price trends, volatility, and returns.

After all analyses are complete, consolidate into a comprehensive report.
"""

        # Initiate group chat
        self.user_proxy.initiate_chat(
            self.manager,
            message=initial_message
        )

        # Extract results
        messages = self.group_chat.messages
        conversation_history = [
            {"speaker": msg.get("name", "Unknown"), "content": msg.get("content", "")}
            for msg in messages
        ]

        # Get final summary (usually the last message from manager)
        final_summary = messages[-1].get("content", "No summary available") if messages else "No analysis performed"

        return {
            "ticker": ticker,
            "mode": "collaboration",
            "risk_profile": self.risk_profile,
            "conversation_history": conversation_history,
            "final_summary": final_summary,
            "num_messages": len(messages)
        }

    def analyze_stock_debate(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze a stock using debate mode to reach BUY/SELL consensus.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with debate results and final decision
        """
        print(f"\n{'=' * 70}")
        print(f"MULTI-AGENT DEBATE: Analyzing {ticker}")
        print(f"Risk Profile: {self.risk_profile}")
        print(f"{'=' * 70}\n")

        # Create initial message
        initial_message = f"""The investment committee needs to decide whether to BUY or SELL {ticker}.

Each analyst must:
1. Conduct your specialized analysis using your tools
2. Provide a clear BUY or SELL recommendation with reasoning
3. Respond to other analysts' perspectives
4. Work towards consensus

Risk Profile: {self.risk_profile}

Fundamental Analyst: Start by analyzing the company fundamentals.
Sentiment Analyst: Analyze market sentiment.
Valuation Analyst: Analyze valuation and price trends.

Continue discussion until you reach consensus on BUY or SELL.
"""

        # Initiate group chat
        self.user_proxy.initiate_chat(
            self.manager,
            message=initial_message
        )

        # Extract results
        messages = self.group_chat.messages
        conversation_history = [
            {"speaker": msg.get("name", "Unknown"), "content": msg.get("content", "")}
            for msg in messages
        ]

        # Parse final decision
        final_decision = self._parse_debate_decision(messages)

        return {
            "ticker": ticker,
            "mode": "debate",
            "risk_profile": self.risk_profile,
            "conversation_history": conversation_history,
            "final_decision": final_decision,
            "num_rounds": len(messages) // 3,  # Approximate number of debate rounds
        }

    def _parse_debate_decision(self, messages: List[Dict]) -> Dict[str, Any]:
        """
        Parse the final decision from debate messages.

        Args:
            messages: List of conversation messages

        Returns:
            Dictionary with decision details
        """
        # Count BUY/SELL recommendations from each agent
        recommendations = {
            "Fundamental_Analyst": None,
            "Sentiment_Analyst": None,
            "Valuation_Analyst": None
        }

        # Look through messages in reverse (most recent first)
        for msg in reversed(messages):
            speaker = msg.get("name", "")
            content = msg.get("content", "").upper()

            if speaker in recommendations and recommendations[speaker] is None:
                if "RECOMMENDATION: BUY" in content or "RECOMMEND BUY" in content:
                    recommendations[speaker] = "BUY"
                elif "RECOMMENDATION: SELL" in content or "RECOMMEND SELL" in content:
                    recommendations[speaker] = "SELL"

        # Count votes
        votes = {"BUY": 0, "SELL": 0, "UNKNOWN": 0}
        for rec in recommendations.values():
            if rec:
                votes[rec] += 1
            else:
                votes["UNKNOWN"] += 1

        # Determine consensus
        if votes["BUY"] >= 2:
            decision = "BUY"
            consensus = True
        elif votes["SELL"] >= 2:
            decision = "SELL"
            consensus = True
        else:
            decision = "SELL"  # Conservative default
            consensus = False

        # Get final summary (last message)
        final_summary = messages[-1].get("content", "") if messages else ""

        return {
            "decision": decision,
            "consensus_reached": consensus,
            "votes": votes,
            "individual_recommendations": recommendations,
            "final_summary": final_summary
        }


def create_alpha_agents_chat(
    risk_profile: str = "risk_neutral",
    mode: str = "collaboration"
) -> AlphaAgentsGroupChat:
    """
    Factory function to create an AlphaAgents group chat.

    Args:
        risk_profile: Risk tolerance profile
        mode: 'collaboration' or 'debate'

    Returns:
        AlphaAgentsGroupChat instance
    """
    return AlphaAgentsGroupChat(risk_profile=risk_profile, mode=mode)

"""
Base agent class for AlphaAgents.
"""
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent

from config.settings import settings


class BaseStockAgent(AssistantAgent):
    """Base class for stock analysis agents."""

    def __init__(
        self,
        name: str,
        system_message: str,
        llm_config: Optional[Dict] = None,
        risk_profile: str = "risk_neutral",
        **kwargs
    ):
        """
        Initialize base stock agent.

        Args:
            name: Agent name
            system_message: System message defining agent role
            llm_config: LLM configuration
            risk_profile: Risk tolerance profile
            **kwargs: Additional arguments for AssistantAgent
        """
        # Get risk profile configuration
        risk_config = settings.get_risk_profile(risk_profile)

        # Enhance system message with risk profile
        enhanced_message = f"""{system_message}

RISK PROFILE: {risk_profile.replace('_', ' ').upper()}
{risk_config['prompt_modifier']}
"""

        # Default LLM config if not provided
        if llm_config is None:
            llm_config = {
                "config_list": settings.AUTOGEN_CONFIG_LIST,
                "temperature": settings.LLM_TEMPERATURE,
                "timeout": 120,
            }

        super().__init__(
            name=name,
            system_message=enhanced_message,
            llm_config=llm_config,
            **kwargs
        )

        self.risk_profile = risk_profile
        self.risk_config = risk_config

    def get_recommendation_prompt(self) -> str:
        """Get prompt for final recommendation based on risk profile."""
        volatility_threshold = self.risk_config.get("volatility_threshold", 0.30)

        return f"""
Based on your analysis, provide a clear BUY or SELL recommendation.

Consider:
- Your risk tolerance profile: {self.risk_profile}
- Maximum acceptable volatility: {volatility_threshold * 100:.0f}%
- Your specialized perspective (fundamental/sentiment/valuation)

Provide your recommendation in this format:
RECOMMENDATION: [BUY or SELL]
CONFIDENCE: [HIGH/MEDIUM/LOW]
REASONING: [2-3 sentences explaining your decision]
"""

"""
Configuration settings for AlphaAgents stock picking system.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Central configuration class for AlphaAgents."""

    # ==================== API Keys ====================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    FMP_API_KEY: str = os.getenv("FMP_API_KEY", "")  # Financial Modeling Prep (optional)

    # ==================== LLM Configuration ====================
    LLM_MODEL: str = "gpt-4o"  # As used in the AlphaAgents paper
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # Embedding model for RAG
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ==================== API Rate Limits ====================
    # Finnhub free tier: 60 requests/minute
    FINNHUB_RATE_LIMIT: int = 60
    FINNHUB_RATE_PERIOD: int = 60  # seconds

    # FMP free tier: 250 requests/day
    FMP_RATE_LIMIT: int = 250
    FMP_RATE_PERIOD: int = 86400  # seconds (1 day)

    # SEC EDGAR: 10 requests/second
    SEC_RATE_LIMIT: int = 10
    SEC_RATE_PERIOD: int = 1  # second

    # yfinance (unofficial - be conservative)
    YFINANCE_RATE_LIMIT: int = 100
    YFINANCE_RATE_PERIOD: int = 3600  # 1 hour

    # ==================== SEC EDGAR Configuration ====================
    SEC_USER_AGENT: str = "AlphaAgents Research Project contact@example.com"

    # ==================== Risk Tolerance Profiles ====================
    RISK_PROFILES: Dict[str, Dict[str, Any]] = {
        "risk_neutral": {
            "description": "Balanced approach to risk and return",
            "prompt_modifier": (
                "You are analyzing this stock for a risk-neutral investor who seeks "
                "a balanced approach between risk and return. Consider both upside "
                "potential and downside risk equally in your analysis."
            ),
            "volatility_threshold": 0.30,  # Accept up to 30% annualized volatility
        },
        "risk_averse": {
            "description": "Conservative approach prioritizing capital preservation",
            "prompt_modifier": (
                "You are analyzing this stock for a risk-averse investor who prioritizes "
                "capital preservation and stability over high returns. Be cautious with "
                "volatile stocks and emphasize downside protection."
            ),
            "volatility_threshold": 0.20,  # Only accept up to 20% annualized volatility
        },
        "risk_seeking": {
            "description": "Aggressive approach seeking high returns",
            "prompt_modifier": (
                "You are analyzing this stock for a risk-seeking investor who is comfortable "
                "with high volatility in pursuit of higher returns. Focus on growth potential "
                "and momentum indicators."
            ),
            "volatility_threshold": 0.50,  # Accept up to 50% annualized volatility
        },
    }

    # Default risk profile
    DEFAULT_RISK_PROFILE: str = "risk_neutral"

    # ==================== Agent Configuration ====================
    # AutoGen configuration
    AUTOGEN_CONFIG_LIST: list = [
        {
            "model": LLM_MODEL,
            "api_key": OPENAI_API_KEY,
            "temperature": LLM_TEMPERATURE,
        }
    ]

    # Maximum number of debate rounds
    MAX_DEBATE_ROUNDS: int = 5

    # Minimum number of times each agent must speak
    MIN_AGENT_TURNS: int = 2

    # ==================== RAG Configuration ====================
    # Chunk size for document splitting (10-K/10-Q reports)
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Number of relevant chunks to retrieve
    RAG_TOP_K: int = 5

    # Vector store configuration
    VECTOR_STORE_PATH: str = "./data/vector_store"

    # ==================== Backtesting Configuration ====================
    # Number of trading days per year (for annualization)
    TRADING_DAYS_PER_YEAR: int = 252

    # Risk-free rate (use 1-month Treasury rate - update as needed)
    RISK_FREE_RATE: float = 0.05  # 5% annual

    # Rolling window for Sharpe ratio (in trading days)
    ROLLING_WINDOW_DAYS: int = 20  # ~1 month

    # Benchmark composition (equal weight)
    PORTFOLIO_EQUAL_WEIGHT: bool = True

    # ==================== Data Storage ====================
    # Cache directory for downloaded data
    DATA_CACHE_DIR: str = "./data/cache"

    # Logs directory for agent conversations
    LOGS_DIR: str = "./logs"

    # Results directory for backtesting outputs
    RESULTS_DIR: str = "./results"

    # ==================== Validation ====================
    @classmethod
    def validate(cls) -> bool:
        """Validate that required API keys are set."""
        missing_keys = []

        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")

        if not cls.FINNHUB_API_KEY:
            missing_keys.append("FINNHUB_API_KEY")

        if missing_keys:
            print(f"Warning: Missing required API keys: {', '.join(missing_keys)}")
            print("Please set them in your .env file or environment variables.")
            return False

        return True

    @classmethod
    def get_risk_profile(cls, profile_name: str = None) -> Dict[str, Any]:
        """Get risk profile configuration."""
        if profile_name is None:
            profile_name = cls.DEFAULT_RISK_PROFILE

        if profile_name not in cls.RISK_PROFILES:
            raise ValueError(
                f"Unknown risk profile: {profile_name}. "
                f"Available profiles: {list(cls.RISK_PROFILES.keys())}"
            )

        return cls.RISK_PROFILES[profile_name]


# Singleton instance
settings = Settings()

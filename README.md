# AlphaAgents: Multi-Agent Stock Analysis System

A complete implementation of the **AlphaAgents** framework from the paper "AlphaAgents: Large Language Model based Multi-Agents for Equity Portfolio Constructions" (BlackRock, 2025).

This system uses three specialized AI agents that collaborate and debate to analyze stocks, providing comprehensive fundamental, sentiment, and valuation analysis for portfolio construction.

## Overview

AlphaAgents implements a multi-agent system where three specialized agents work together:

- **Fundamental Agent**: Analyzes 10-K/10-Q SEC filings and financial statements
- **Sentiment Agent**: Analyzes financial news and market sentiment
- **Valuation Agent**: Analyzes price trends, volatility, and risk-adjusted returns

The agents can operate in two modes:
1. **Collaboration Mode**: Agents work together to create comprehensive stock analysis reports
2. **Debate Mode**: Agents debate to reach consensus on BUY/SELL recommendations

## Features

✅ **Three Specialized Agents** with role-based prompting
✅ **RAG-powered 10-K/10-Q Analysis** using SEC EDGAR filings
✅ **News Sentiment Analysis** with reflection-enhanced prompting
✅ **Price & Volatility Analysis** with risk-adjusted metrics
✅ **Multi-Agent Collaboration** using Microsoft AutoGen
✅ **Debate Mechanism** for consensus-based stock selection
✅ **Risk Tolerance Profiles** (risk-neutral, risk-averse, risk-seeking)
✅ **Portfolio Backtesting** with Sharpe ratio and performance metrics
✅ **Free API Tier Support** (SEC EDGAR, Finnhub, yfinance)

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (required)
- Finnhub API key (required - free tier available)
- FMP API key (optional - for enhanced fundamentals)

### Step 1: Clone or Download

```bash
cd "Stock Picking Project"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys

1. Copy the template file:
```bash
copy .env.template .env
```

2. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_key_here
FINNHUB_API_KEY=your_finnhub_key_here
FMP_API_KEY=your_fmp_key_here  # Optional
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Finnhub (free): https://finnhub.io/register
- FMP (free tier): https://site.financialmodelingprep.com/developer/docs

## Quick Start

### Example 1: Analyze a Single Stock (Collaboration Mode)

```python
from agents.group_chat_manager import create_alpha_agents_chat

# Create multi-agent chat
chat = create_alpha_agents_chat(risk_profile="risk_neutral", mode="collaboration")

# Analyze stock
result = chat.analyze_stock_collaboration("AAPL")

print(result['final_summary'])
```

### Example 2: Analyze a Single Stock (Debate Mode)

```python
# Create debate chat
chat = create_alpha_agents_chat(risk_profile="risk_neutral", mode="debate")

# Run debate to get BUY/SELL decision
result = chat.analyze_stock_debate("MSFT")

print(f"Decision: {result['final_decision']['decision']}")
print(f"Votes: {result['final_decision']['votes']}")
```

### Example 3: Run from Command Line

```bash
# Analyze a stock using collaboration mode
python main.py --ticker AAPL --mode collaboration --risk risk_neutral

# Analyze a stock using debate mode
python main.py --ticker MSFT --mode debate --risk risk_averse

# Run backtest example
python main.py --backtest
```

## Project Structure

```
Stock Picking Project/
├── main.py                      # Main entry point with examples
├── requirements.txt             # Python dependencies
├── .env.template                # API key template
├── README.md                    # This file
│
├── config/
│   └── settings.py             # Configuration management
│
├── agents/
│   ├── base_agent.py           # Base agent class
│   ├── fundamental_agent.py    # Fundamental analysis agent
│   ├── sentiment_agent.py      # Sentiment analysis agent
│   ├── valuation_agent.py      # Valuation analysis agent
│   └── group_chat_manager.py   # Multi-agent orchestration
│
├── tools/
│   ├── sec_edgar_tool.py       # SEC filing RAG tool
│   ├── news_tool.py            # News sentiment tool
│   ├── price_tool.py           # Price/volume analysis tool
│   └── fundamental_tool.py     # Financial metrics tool
│
├── data/
│   └── fetchers.py             # API client wrappers
│
├── backtesting/
│   ├── portfolio.py            # Portfolio construction
│   └── metrics.py              # Performance metrics
│
└── utils/
    └── (utilities)
```

## Usage Guide

### 1. Single Stock Analysis

Analyze a stock with all three agents working together:

```python
from main import analyze_single_stock

result = analyze_single_stock(
    ticker="NVDA",
    mode="collaboration",
    risk_profile="risk_neutral"
)
```

### 2. Stock Selection Pipeline

Run multi-agent debate on multiple stocks to select a portfolio:

```python
from main import run_stock_selection_pipeline

stock_universe = ["AAPL", "MSFT", "GOOGL", "META", "NVDA"]

selected_stocks = run_stock_selection_pipeline(
    stock_universe=stock_universe,
    risk_profile="risk_neutral"
)

print(f"Selected: {selected_stocks}")
```

### 3. Backtesting

Backtest portfolio performance:

```python
from backtesting.portfolio import Portfolio
from backtesting.metrics import create_backtest_report

# Create portfolios
benchmark = Portfolio(
    name="Benchmark",
    tickers=["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
    start_date="2024-02-01",
    end_date="2024-05-31"
)

# Load data and calculate metrics
benchmark.load_data()
benchmark.calculate_returns()
benchmark.calculate_metrics()

# Print summary
print(benchmark.summary())

# Generate comprehensive report with visualizations
report = create_backtest_report([benchmark])
```

## Risk Profiles

The system supports three risk tolerance levels:

### Risk Neutral (Default)
- Balanced approach to risk and return
- Max volatility: 30% annualized
- Suitable for: Most investors

### Risk Averse
- Conservative approach prioritizing capital preservation
- Max volatility: 20% annualized
- Suitable for: Conservative investors, near-retirement

### Risk Seeking
- Aggressive approach seeking high returns
- Max volatility: 50% annualized
- Suitable for: Growth-focused, long-term investors

Example:
```python
chat = create_alpha_agents_chat(risk_profile="risk_averse", mode="debate")
```

## Data Sources & APIs

### Free APIs Used:
- **SEC EDGAR**: Official 10-K/10-Q filings (free, unlimited)
- **Finnhub**: Financial news and sentiment (free: 60 req/min)
- **Yahoo Finance** (yfinance): Historical prices (free, rate-limited)

### Optional Paid APIs:
- **Financial Modeling Prep**: Enhanced fundamentals ($49/month)

### Cost Summary:
- **Zero-cost setup**: $0/month (using free tiers)
- **OpenAI API costs**: ~$10-20 for development/testing
- **Production setup**: ~$49/month (with FMP subscription)

## Backtesting Metrics

The system calculates comprehensive performance metrics:

- **Returns**: Total, annualized, cumulative
- **Risk**: Volatility, maximum drawdown
- **Risk-Adjusted**: Sharpe ratio, rolling Sharpe
- **Trading Stats**: Win rate, number of trading days

Visualizations include:
- Cumulative returns comparison
- Rolling Sharpe ratio
- Risk-return scatter plot

## Examples

### Example: Full Workflow

```python
from config.settings import settings
from agents.group_chat_manager import create_alpha_agents_chat
from backtesting.portfolio import Portfolio
from backtesting.metrics import create_backtest_report

# 1. Validate environment
if not settings.validate():
    print("Please configure API keys!")
    exit(1)

# 2. Analyze stocks and get recommendations
stock_universe = ["AAPL", "MSFT", "NVDA", "GOOGL", "META"]
buy_recommendations = []

chat = create_alpha_agents_chat(risk_profile="risk_neutral", mode="debate")

for ticker in stock_universe:
    result = chat.analyze_stock_debate(ticker)
    if result['final_decision']['decision'] == "BUY":
        buy_recommendations.append(ticker)

print(f"Selected: {buy_recommendations}")

# 3. Construct and backtest portfolio
portfolio = Portfolio(
    name="Multi-Agent Portfolio",
    tickers=buy_recommendations,
    start_date="2024-02-01",
    end_date="2024-05-31"
)

portfolio.load_data()
portfolio.calculate_returns()
print(portfolio.summary())

# 4. Generate report
report = create_backtest_report([portfolio])
```

## Troubleshooting

### Common Issues

**1. "Missing API key" error**
- Make sure you've created a `.env` file from `.env.template`
- Verify your API keys are correct and active

**2. "No data available" for stock**
- Check ticker symbol is correct
- Some stocks may not have complete data in free APIs
- Try a different date range

**3. Rate limit errors**
- Free API tiers have limits (Finnhub: 60/min, yfinance: ~100/hour)
- The system has built-in rate limiting, but heavy usage may hit limits
- Consider upgrading to paid tiers for production use

**4. AutoGen installation issues**
- Make sure you're using Python 3.8+
- Try: `pip install --upgrade pyautogen openai`

## Limitations

- **Free APIs**: Rate limits and potential reliability issues (especially yfinance)
- **10-K Analysis**: RAG quality depends on filing structure and complexity
- **News Coverage**: Limited to stocks with regular news coverage
- **Computation Time**: Multi-agent debates can take 2-5 minutes per stock
- **LLM Costs**: Each stock analysis costs ~$0.10-0.50 in OpenAI API credits

## Future Enhancements

Potential improvements to consider:

- [ ] Add Technical Analysis Agent
- [ ] Add Macro Economist Agent
- [ ] Implement custom portfolio weighting (beyond equal weight)
- [ ] Add portfolio optimization (Mean-Variance, Black-Litterman)
- [ ] Implement more sophisticated consensus mechanisms
- [ ] Add support for other LLM providers (Anthropic Claude, etc.)
- [ ] Create web interface for easier interaction
- [ ] Add caching to reduce API costs

## References

Based on the paper:
**"AlphaAgents: Large Language Model based Multi-Agents for Equity Portfolio Constructions"**
Authors: Tianjiao Zhao, Jingrao Lyu, Stokes Jones, Harrison Garber, Stefano Pasquali, Dhagash Mehta
Organization: BlackRock, Inc.
Year: 2025

## License

This is an educational implementation for research and learning purposes.

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments and docstrings
3. Consult the original AlphaAgents paper for methodology details

---

**Built with**: Python, AutoGen, OpenAI GPT-4o, LangChain, and free financial data APIs

**Status**: ✅ Complete implementation ready for testing and experimentation

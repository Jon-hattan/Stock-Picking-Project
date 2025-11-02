# Quick Start Guide - AlphaAgents

Get up and running with AlphaAgents in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

This will install:
- AutoGen (multi-agent framework)
- OpenAI SDK
- Financial data APIs (yfinance, finnhub-python, sec-edgar-downloader)
- LangChain (for RAG)
- Data processing libraries (pandas, numpy)
- Visualization libraries (matplotlib, seaborn)

## Step 2: Get API Keys (3 minutes)

### Required APIs (Free):

**1. OpenAI API Key** (Required - costs ~$0.10-0.50 per stock analysis)
- Go to: https://platform.openai.com/api-keys
- Sign up or log in
- Click "Create new secret key"
- Copy the key

**2. Finnhub API Key** (Required - FREE tier: 60 requests/minute)
- Go to: https://finnhub.io/register
- Sign up with your email
- Copy your API key from the dashboard

### Optional API (Free tier available):

**3. Financial Modeling Prep** (Optional - FREE tier: 250 requests/day)
- Go to: https://site.financialmodelingprep.com/developer/docs
- Sign up for free account
- Get your API key

## Step 3: Configure Environment (1 minute)

1. Copy the template:
```bash
copy .env.template .env
```

2. Open `.env` in a text editor and paste your keys:
```
OPENAI_API_KEY=sk-your-key-here
FINNHUB_API_KEY=your-finnhub-key-here
FMP_API_KEY=your-fmp-key-here
```

## Step 4: Test the System

### Option A: Run Examples (Recommended)

```bash
python main.py
```

This will run two examples:
1. Collaboration analysis of AAPL
2. Debate analysis of MSFT

### Option B: Analyze a Specific Stock

```bash
# Collaboration mode
python main.py --ticker NVDA --mode collaboration

# Debate mode (get BUY/SELL decision)
python main.py --ticker TSLA --mode debate --risk risk_neutral
```

### Option C: Run Backtesting Example

```bash
python main.py --backtest
```

## What to Expect

### First Run (Collaboration Mode):
```
==================================================================
EXAMPLE 1: Single Stock Analysis (Collaboration)
==================================================================

Analyzing AAPL using multi-agent collaboration
Risk Profile: risk_neutral
==================================================================

Downloading 10-K for AAPL...
Fetching news for AAPL (last 30 days)...
Analyzing price trends for AAPL (3mo)...

[Agents will collaborate and produce a comprehensive report]

✓ Analysis complete!
Number of messages: 12
```

### First Run (Debate Mode):
```
==================================================================
EXAMPLE 2: Single Stock Analysis (Debate)
==================================================================

Analyzing MSFT using multi-agent debate
Risk Profile: risk_neutral
==================================================================

[Agents will debate until consensus is reached]

✓ Debate complete!
Final Decision: BUY
Consensus Reached: True
Votes: {'BUY': 3, 'SELL': 0, 'UNKNOWN': 0}
```

## Understanding the Output

Each agent will:

**Fundamental Agent:**
- Downloads and analyzes 10-K filing
- Calculates financial ratios
- Provides fundamental perspective

**Sentiment Agent:**
- Fetches recent news articles
- Analyzes sentiment
- Provides market sentiment perspective

**Valuation Agent:**
- Analyzes price trends
- Calculates volatility and Sharpe ratio
- Provides valuation perspective

**Final Output:**
- Comprehensive report (collaboration mode)
- BUY/SELL decision with reasoning (debate mode)

## Next Steps

### Analyze Your Own Stock Portfolio

Create a Python script:

```python
from agents.group_chat_manager import create_alpha_agents_chat

# Your stocks to analyze
my_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

# Create debate chat
chat = create_alpha_agents_chat(risk_profile="risk_neutral", mode="debate")

# Analyze each stock
recommendations = {}
for ticker in my_stocks:
    result = chat.analyze_stock_debate(ticker)
    decision = result['final_decision']['decision']
    recommendations[ticker] = decision
    print(f"{ticker}: {decision}")

# Show BUY recommendations
buy_list = [t for t, d in recommendations.items() if d == "BUY"]
print(f"\nRecommended to BUY: {buy_list}")
```

### Run a Backtest

```python
from backtesting.portfolio import Portfolio

# Create portfolio from your picks
portfolio = Portfolio(
    name="My Portfolio",
    tickers=["AAPL", "MSFT", "NVDA"],  # Your BUY recommendations
    start_date="2024-01-01",
    end_date="2024-06-01"
)

# Analyze performance
portfolio.load_data()
portfolio.calculate_returns()
print(portfolio.summary())
```

### Try Different Risk Profiles

```python
# Conservative analysis
chat_conservative = create_alpha_agents_chat(
    risk_profile="risk_averse",
    mode="debate"
)

# Aggressive analysis
chat_aggressive = create_alpha_agents_chat(
    risk_profile="risk_seeking",
    mode="debate"
)
```

## Common Issues & Solutions

### Issue: "Missing API key" error
**Solution:** Make sure you created `.env` file (not `.env.template`) and added your keys

### Issue: "No data available" for a stock
**Solution:** Try a different ticker or check that it's a valid US stock symbol

### Issue: Rate limit errors
**Solution:** The free Finnhub tier allows 60 requests/minute. If analyzing many stocks, add a delay between analyses.

### Issue: Takes too long
**Solution:** Multi-agent analysis takes 2-5 minutes per stock. This is normal. For faster testing, use collaboration mode instead of debate mode.

## Cost Estimate

For typical usage:
- **OpenAI API**: ~$0.10-0.50 per stock analysis
- **Analyzing 10 stocks**: ~$1-5 in OpenAI credits
- **Finnhub**: FREE (up to 60 req/min)
- **SEC EDGAR**: FREE (unlimited)
- **yfinance**: FREE (with rate limits)

**Total for learning/testing:** $5-20 in OpenAI credits

## Tips for Best Results

1. **Start small:** Test with 1-2 stocks first
2. **Use debate mode:** Gets you actionable BUY/SELL decisions
3. **Compare risk profiles:** Try analyzing the same stock with different risk profiles
4. **Check the conversation history:** Review how agents debated to understand their reasoning
5. **Backtest your selections:** Validate agent recommendations with historical data

## Getting Help

1. **Read the full README.md** for detailed documentation
2. **Check the code comments** - every function is documented
3. **Review the AlphaAgents paper** (included as PDF) for methodology
4. **Common questions:**
   - How to change LLM model? Edit `config/settings.py` → `LLM_MODEL`
   - How to add more stocks? Just add to the ticker list
   - How to save results? Results are automatically saved to `./results/`

## You're Ready!

You now have a complete multi-agent stock analysis system. Start analyzing stocks and building portfolios!

```bash
# Let's go!
python main.py --ticker YOUR_FAVORITE_STOCK --mode debate
```

Happy investing! 🚀📈

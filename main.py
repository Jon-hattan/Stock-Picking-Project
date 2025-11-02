"""
AlphaAgents: Multi-Agent Stock Analysis and Portfolio Construction

This is the main entry point for the AlphaAgents system.
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from agents.group_chat_manager import create_alpha_agents_chat
from backtesting.portfolio import Portfolio
from backtesting.metrics import create_backtest_report


def validate_environment():
    """Validate that API keys are configured."""
    print("Validating environment...")

    if not settings.validate():
        print("\nERROR: Missing required API keys!")
        print("\nPlease set up your API keys:")
        print("1. Copy .env.template to .env")
        print("2. Fill in your API keys in the .env file")
        print("\nRequired:")
        print("  - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)")
        print("  - FINNHUB_API_KEY (get from https://finnhub.io/register)")
        print("\nOptional:")
        print("  - FMP_API_KEY (get from https://site.financialmodelingprep.com/developer/docs)")
        return False

    print(" Environment validated successfully")
    return True


def analyze_single_stock(
    ticker: str,
    mode: str = "collaboration",
    risk_profile: str = "risk_neutral"
) -> Dict[str, Any]:
    """
    Analyze a single stock using multi-agent system.

    Args:
        ticker: Stock ticker symbol
        mode: 'collaboration' or 'debate'
        risk_profile: 'risk_neutral', 'risk_averse', or 'risk_seeking'

    Returns:
        Dictionary with analysis results
    """
    print(f"\n{'='*70}")
    print(f"Analyzing {ticker} using multi-agent {mode}")
    print(f"Risk Profile: {risk_profile}")
    print(f"{'='*70}\n")

    # Create multi-agent chat
    chat = create_alpha_agents_chat(risk_profile=risk_profile, mode=mode)

    # Run analysis
    if mode == "collaboration":
        result = chat.analyze_stock_collaboration(ticker)
    else:  # debate
        result = chat.analyze_stock_debate(ticker)

    return result


def run_backtest_example():
    """
    Run a backtest example comparing different agent portfolios.

    This example demonstrates how to:
    1. Analyze multiple stocks using the multi-agent system
    2. Construct portfolios based on agent recommendations
    3. Backtest portfolio performance
    4. Compare results across different strategies
    """
    print("\n" + "="*70)
    print("RUNNING BACKTEST EXAMPLE")
    print("="*70 + "\n")

    # Example stock universe (15 tech stocks as in the paper)
    stock_universe = [
        "AAPL", "MSFT", "GOOGL", "META", "NVDA",
        "TSLA", "AMD", "NFLX", "ADBE", "CRM",
        "INTC", "CSCO", "ORCL", "QCOM", "TXN"
    ]

    # Backtest period (Feb-May 2024 as in the paper)
    start_date = "2024-02-01"
    end_date = "2024-05-31"

    print(f"Stock Universe: {len(stock_universe)} stocks")
    print(f"Period: {start_date} to {end_date}")
    print(f"\nStocks: {', '.join(stock_universe)}\n")

    # In a real implementation, you would:
    # 1. Run multi-agent analysis on each stock (this takes time!)
    # 2. Collect BUY/SELL recommendations
    # 3. Construct portfolios based on recommendations

    # For this example, we'll create sample portfolios

    # Benchmark: All stocks equally weighted
    benchmark = Portfolio(
        name="Benchmark (Equal Weight)",
        tickers=stock_universe,
        start_date=start_date,
        end_date=end_date
    )

    # Example: Multi-agent portfolio (subset of stocks based on BUY recommendations)
    # In practice, these would be determined by running the debate mechanism
    multi_agent_picks = ["AAPL", "MSFT", "NVDA", "META", "AMD", "CRM", "ADBE"]

    multi_agent_portfolio = Portfolio(
        name="Multi-Agent Portfolio",
        tickers=multi_agent_picks,
        start_date=start_date,
        end_date=end_date
    )

    # Example: Valuation-only portfolio
    valuation_picks = stock_universe  # In practice, based on valuation agent only

    valuation_portfolio = Portfolio(
        name="Valuation Agent Portfolio",
        tickers=valuation_picks,
        start_date=start_date,
        end_date=end_date
    )

    # List of portfolios to compare
    portfolios = [benchmark, multi_agent_portfolio, valuation_portfolio]

    # Load data and calculate metrics
    print("Loading portfolio data and calculating metrics...\n")
    for portfolio in portfolios:
        try:
            portfolio.load_data()
            portfolio.calculate_returns()
            portfolio.calculate_metrics()
        except Exception as e:
            print(f"Error processing {portfolio.name}: {e}")

    # Create comprehensive report
    print("\n" + "="*70)
    print("GENERATING BACKTEST REPORT")
    print("="*70 + "\n")

    report = create_backtest_report(portfolios)

    print(f"\n Backtest complete!")
    print(f" Results saved to: {report['output_dir']}")

    return report


def run_stock_selection_pipeline(
    stock_universe: List[str],
    risk_profile: str = "risk_neutral"
) -> List[str]:
    """
    Run the full stock selection pipeline using multi-agent debate.

    Args:
        stock_universe: List of tickers to analyze
        risk_profile: Risk tolerance profile

    Returns:
        List of tickers with BUY recommendations
    """
    print(f"\n{'='*70}")
    print(f"STOCK SELECTION PIPELINE")
    print(f"Risk Profile: {risk_profile}")
    print(f"Analyzing {len(stock_universe)} stocks")
    print(f"{'='*70}\n")

    buy_recommendations = []

    for i, ticker in enumerate(stock_universe, 1):
        print(f"\n[{i}/{len(stock_universe)}] Analyzing {ticker}...")

        try:
            # Run debate to get BUY/SELL decision
            result = analyze_single_stock(ticker, mode="debate", risk_profile=risk_profile)

            decision = result.get("final_decision", {}).get("decision", "SELL")

            print(f"Decision for {ticker}: {decision}")

            if decision == "BUY":
                buy_recommendations.append(ticker)
                print(f" Added {ticker} to portfolio")

        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            continue

    print(f"\n{'='*70}")
    print(f"SELECTION COMPLETE")
    print(f"{'='*70}")
    print(f"\nSelected {len(buy_recommendations)} stocks for portfolio:")
    print(f"{', '.join(buy_recommendations)}")

    return buy_recommendations


def main():
    """Main function."""
    print("\n" + "="*70)
    print("AlphaAgents: Multi-Agent Stock Analysis System")
    print("="*70 + "\n")

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    # Example 1: Single stock analysis (collaboration mode)
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Stock Analysis (Collaboration)")
    print("="*70)

    result = analyze_single_stock("AAPL", mode="collaboration", risk_profile="risk_neutral")

    print("\n Analysis complete!")
    print(f"Number of messages: {result['num_messages']}")
    print(f"\nFinal Summary:\n{result['final_summary'][:500]}...")  # First 500 chars

    # Example 2: Single stock analysis (debate mode)
    print("\n\n" + "="*70)
    print("EXAMPLE 2: Single Stock Analysis (Debate)")
    print("="*70)

    result = analyze_single_stock("MSFT", mode="debate", risk_profile="risk_neutral")

    print("\n Debate complete!")
    decision = result.get("final_decision", {})
    print(f"Final Decision: {decision.get('decision', 'Unknown')}")
    print(f"Consensus Reached: {decision.get('consensus_reached', False)}")
    print(f"Votes: {decision.get('votes', {})}")

    # Example 3: Backtest (optional - commented out to save time)
    # Uncomment to run full backtest
    """
    print("\n\n" + "="*70)
    print("EXAMPLE 3: Backtesting")
    print("="*70)

    report = run_backtest_example()
    """

    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Check if running in example mode or custom mode
    import argparse

    parser = argparse.ArgumentParser(description="AlphaAgents Stock Analysis System")
    parser.add_argument("--ticker", type=str, help="Stock ticker to analyze")
    parser.add_argument("--mode", choices=["collaboration", "debate"], default="collaboration",
                       help="Analysis mode")
    parser.add_argument("--risk", choices=["risk_neutral", "risk_averse", "risk_seeking"],
                       default="risk_neutral", help="Risk profile")
    parser.add_argument("--backtest", action="store_true", help="Run backtest example")

    args = parser.parse_args()

    # Validate environment first
    if not validate_environment():
        sys.exit(1)

    if args.ticker:
        # Analyze specific ticker
        result = analyze_single_stock(args.ticker, mode=args.mode, risk_profile=args.risk)
        print("\n Analysis complete!")

    elif args.backtest:
        # Run backtest
        report = run_backtest_example()

    else:
        # Run all examples
        main()

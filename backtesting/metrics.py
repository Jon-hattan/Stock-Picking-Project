"""
Additional backtesting metrics and visualization functions.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
from pathlib import Path

from backtesting.portfolio import Portfolio
from config.settings import settings


def plot_cumulative_returns(portfolios: List[Portfolio], save_path: Optional[str] = None):
    """
    Plot cumulative returns for multiple portfolios.

    Args:
        portfolios: List of Portfolio objects
        save_path: Optional path to save the plot
    """
    plt.figure(figsize=(12, 6))

    for portfolio in portfolios:
        if portfolio.portfolio_value is None:
            portfolio.calculate_returns()

        cumulative_return = (portfolio.portfolio_value / portfolio.initial_capital - 1) * 100
        plt.plot(cumulative_return.index, cumulative_return.values, label=portfolio.name, linewidth=2)

    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Return (%)', fontsize=12)
    plt.title('Cumulative Return Comparison', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def plot_rolling_sharpe(portfolios: List[Portfolio], window: int = 20, save_path: Optional[str] = None):
    """
    Plot rolling Sharpe ratio for multiple portfolios.

    Args:
        portfolios: List of Portfolio objects
        window: Rolling window size in days
        save_path: Optional path to save the plot
    """
    plt.figure(figsize=(12, 6))

    for portfolio in portfolios:
        rolling_sharpe = portfolio.get_rolling_sharpe(window=window)
        plt.plot(rolling_sharpe.index, rolling_sharpe.values, label=portfolio.name, linewidth=2)

    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'Rolling Sharpe Ratio ({window}-day)', fontsize=12)
    plt.title(f'Rolling Sharpe Ratio Comparison ({window}-day window)', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def plot_risk_return(portfolios: List[Portfolio], save_path: Optional[str] = None):
    """
    Plot risk-return scatter plot.

    Args:
        portfolios: List of Portfolio objects
        save_path: Optional path to save the plot
    """
    plt.figure(figsize=(10, 8))

    returns = []
    volatilities = []
    names = []
    sharpes = []

    for portfolio in portfolios:
        if not portfolio.metrics:
            portfolio.calculate_metrics()

        returns.append(portfolio.metrics["annualized_return"] * 100)
        volatilities.append(portfolio.metrics["annualized_volatility"] * 100)
        names.append(portfolio.name)
        sharpes.append(portfolio.metrics["sharpe_ratio"])

    # Create scatter plot
    scatter = plt.scatter(volatilities, returns, s=200, c=sharpes, cmap='RdYlGn', alpha=0.7, edgecolors='black')

    # Add labels
    for i, name in enumerate(names):
        plt.annotate(name, (volatilities[i], returns[i]),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=10, fontweight='bold')

    plt.xlabel('Annualized Volatility (%)', fontsize=12)
    plt.ylabel('Annualized Return (%)', fontsize=12)
    plt.title('Risk-Return Profile', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Sharpe Ratio', fontsize=11)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def create_backtest_report(
    portfolios: List[Portfolio],
    output_dir: str = None
) -> Dict[str, Any]:
    """
    Create comprehensive backtest report with visualizations.

    Args:
        portfolios: List of Portfolio objects
        output_dir: Directory to save plots and report

    Returns:
        Dictionary with report data
    """
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path(settings.RESULTS_DIR)
        output_path.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("BACKTESTING REPORT")
    print("=" * 70 + "\n")

    # Calculate metrics for all portfolios
    for portfolio in portfolios:
        if not portfolio.metrics:
            portfolio.calculate_metrics()
        print(portfolio.summary())

    # Comparison table
    from backtesting.portfolio import compare_portfolios
    comparison_df = compare_portfolios(portfolios)
    print("\nPORTFOLIO COMPARISON:")
    print("=" * 70)
    print(comparison_df.to_string())
    print()

    # Save comparison to CSV
    comparison_csv_path = output_path / "portfolio_comparison.csv"
    comparison_df.to_csv(comparison_csv_path)
    print(f"Comparison table saved to {comparison_csv_path}")

    # Generate plots
    print("\nGenerating visualizations...")

    cumulative_returns_path = output_path / "cumulative_returns.png"
    plot_cumulative_returns(portfolios, save_path=str(cumulative_returns_path))

    rolling_sharpe_path = output_path / "rolling_sharpe.png"
    plot_rolling_sharpe(portfolios, save_path=str(rolling_sharpe_path))

    risk_return_path = output_path / "risk_return.png"
    plot_risk_return(portfolios, save_path=str(risk_return_path))

    print(f"\nAll visualizations saved to {output_path}")

    # Create report dictionary
    report = {
        "portfolios": [p.metrics for p in portfolios],
        "comparison": comparison_df.to_dict(),
        "output_dir": str(output_path),
        "plots": {
            "cumulative_returns": str(cumulative_returns_path),
            "rolling_sharpe": str(rolling_sharpe_path),
            "risk_return": str(risk_return_path)
        }
    }

    return report


# Optional import check
from typing import Optional

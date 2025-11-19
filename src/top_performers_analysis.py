"""
Top Performers Analysis - Focus on Highest Performing Strategies
Creates ranked list of best strategy-stock combinations
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load results
df = pd.read_csv("results/strategy_metrics.csv")

# Clean and filter
df = df.dropna(subset=['Total Return [%]', 'Sharpe Ratio'])
strategies_only = df[df['Strategy'] != 'Benchmark'].copy()

# Add benchmark comparison for each stock
benchmark_data = df[df['Strategy'] == 'Benchmark'][['Ticker', 'Total Return [%]', 'Sharpe Ratio']].copy()
benchmark_data.columns = ['Ticker', 'Benchmark_Return', 'Benchmark_Sharpe']

strategies_only = strategies_only.merge(benchmark_data, on='Ticker', how='left')
strategies_only['Beat_Market'] = strategies_only['Total Return [%]'] > strategies_only['Benchmark_Return']
strategies_only['Outperformance'] = strategies_only['Total Return [%]'] - strategies_only['Benchmark_Return']

# =====================================================
# FILTER CRITERIA - Only the best!
# =====================================================
top_strategies = strategies_only[
    (strategies_only['Sharpe Ratio'] > 0.5) &  # Decent risk-adjusted return
    (strategies_only['Beat_Market'] == True) &  # Must beat benchmark
    (strategies_only['Total Return [%]'] > 0)   # Must be profitable
].copy()

# Calculate composite score
# Higher = Better
top_strategies['Composite_Score'] = (
    top_strategies['Sharpe Ratio'] * 0.4 +           # Risk-adjusted return (40%)
    (top_strategies['Total Return [%]'] / 100) * 0.3 +  # Raw return (30%)
    (top_strategies['Outperformance'] / 100) * 0.2 +    # Market beat (20%)
    (-top_strategies['Max Drawdown [%]'] / 100) * 0.1   # Risk control (10%)
)

# Sort by composite score
top_strategies = top_strategies.sort_values('Composite_Score', ascending=False).reset_index(drop=True)
top_strategies['Rank'] = range(1, len(top_strategies) + 1)

# =====================================================
# CREATE FOCUSED TOP PERFORMERS DASHBOARD
# =====================================================

# Select columns for display
display_cols = [
    'Rank', 'Ticker', 'Strategy', 'Total Return [%]', 'Sharpe Ratio',
    'Sortino Ratio', 'Max Drawdown [%]', 'Calmar Ratio',
    'Outperformance', 'Total Trades', 'Win Rate [%]', 'Composite_Score'
]

top_n = 25  # Show top 25
top_display = top_strategies.head(top_n)[display_cols].copy()

# Round for display
top_display = top_display.round({
    'Total Return [%]': 2,
    'Sharpe Ratio': 3,
    'Sortino Ratio': 3,
    'Max Drawdown [%]': 2,
    'Calmar Ratio': 3,
    'Outperformance': 2,
    'Win Rate [%]': 1,
    'Composite_Score': 3
})

# =====================================================
# BUILD DASHBOARD
# =====================================================

fig = make_subplots(
    rows=3, cols=1,
    row_heights=[0.50, 0.30, 0.20],
    subplot_titles=(
        f"Top {top_n} Strategy-Stock Combinations (Ranked by Composite Score)",
        "Performance Distribution by Strategy Type",
        "Best Stocks by Strategy"
    ),
    specs=[[{"type": "table"}],
           [{"type": "bar"}],
           [{"type": "table"}]],
    vertical_spacing=0.08
)

# Main ranking table
fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Rank</b>", "<b>Stock</b>", "<b>Strategy</b>", "<b>Return %</b>",
                    "<b>Sharpe</b>", "<b>Sortino</b>", "<b>Max DD %</b>", "<b>Calmar</b>",
                    "<b>vs Market %</b>", "<b>Trades</b>", "<b>Win %</b>", "<b>Score</b>"],
            fill_color="#0A2F35",
            font=dict(color="white", size=11),
            align="center",
            height=30
        ),
        cells=dict(
            values=[top_display[col].values for col in top_display.columns],
            fill_color=[["#1A1A2E" if i % 2 == 0 else "#252540" for i in range(len(top_display))]],
            font=dict(color="#E0E0E0", size=10),
            align="center",
            height=26
        )
    ),
    row=1, col=1
)

# Strategy distribution (bar chart)
strategy_counts = top_strategies.head(top_n).groupby('Strategy').agg({
    'Ticker': 'count',
    'Sharpe Ratio': 'mean',
    'Total Return [%]': 'mean'
}).reset_index()

strategy_colors = {'Trend': '#00CED1', 'High_Vol': '#9370DB', 'Low_Vol': '#20B2AA'}

fig.add_trace(
    go.Bar(
        x=strategy_counts['Strategy'],
        y=strategy_counts['Ticker'],
        name='Count in Top 25',
        marker=dict(color=[strategy_colors.get(s, '#808080') for s in strategy_counts['Strategy']]),
        text=strategy_counts['Ticker'],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Top 25 Count: %{y}<br><extra></extra>"
    ),
    row=2, col=1
)

# Best stock per strategy
best_per_strategy = []
for strategy in ['Trend', 'High_Vol', 'Low_Vol']:
    best = top_strategies[top_strategies['Strategy'] == strategy].head(1)
    if len(best) > 0:
        best_per_strategy.append({
            'Strategy': strategy,
            'Best_Stock': best.iloc[0]['Ticker'],
            'Return': f"{best.iloc[0]['Total Return [%]']:.2f}%",
            'Sharpe': f"{best.iloc[0]['Sharpe Ratio']:.3f}",
            'Rank': int(best.iloc[0]['Rank'])
        })

best_df = pd.DataFrame(best_per_strategy)

fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Strategy</b>", "<b>Best Stock</b>", "<b>Return</b>", "<b>Sharpe</b>", "<b>Overall Rank</b>"],
            fill_color="#0A2F35",
            font=dict(color="white", size=12),
            align="center",
            height=30
        ),
        cells=dict(
            values=[best_df[col].values for col in best_df.columns],
            fill_color="#1A1A2E",
            font=dict(color="#E0E0E0", size=11),
            align="center",
            height=28
        )
    ),
    row=3, col=1
)

# Layout
fig.update_layout(
    title={
        'text': "<b>Top Performing Strategies: AI/Tech Analysis</b><br><sub>Filtered for: Positive Returns + Beat Market + Sharpe > 0.5</sub>",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20, 'color': '#0A2F35'}
    },
    height=1200,
    showlegend=False,
    paper_bgcolor='#F5F7FA',
    plot_bgcolor='white',
    margin=dict(l=60, r=60, t=100, b=60)
)

fig.update_yaxes(title="Number in Top 25", row=2, col=1)

# Save
fig.write_html("top_performers.html", include_plotlyjs="cdn")

# Also save detailed CSV for drill-down
top_strategies.to_csv("results/top_performers_detailed.csv", index=False)

print("\n" + "="*70)
print(f"[SUCCESS] Top performers analysis complete!")
print(f"Total qualifying strategies: {len(top_strategies)}")
print(f"Dashboard: top_performers.html")
print(f"Detailed data: results/top_performers_detailed.csv")
print("="*70)
print("\nTop 5 Best Strategies:")
print(top_strategies.head(5)[['Rank', 'Ticker', 'Strategy', 'Total Return [%]', 'Sharpe Ratio', 'Composite_Score']].to_string(index=False))

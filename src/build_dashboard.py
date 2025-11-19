"""
Build Master Performance Dashboard
Analyzes all strategy results and creates recruiter-friendly summary
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Load results
df = pd.read_csv("results/strategy_metrics.csv")

# Clean data
df = df.dropna(subset=['Total Return [%]', 'Sharpe Ratio'])

# Add beat_market column
benchmark_returns = df[df['Strategy'] == 'Benchmark'].set_index('Ticker')['Total Return [%]']
df['Beat_Market'] = df.apply(
    lambda row: 'Yes' if row['Strategy'] != 'Benchmark' and
                         row['Total Return [%]'] > benchmark_returns.get(row['Ticker'], 0)
                else 'No',
    axis=1
)

# Calculate outperformance
df['Market_Outperf'] = df.apply(
    lambda row: row['Total Return [%]'] - benchmark_returns.get(row['Ticker'], 0)
                if row['Strategy'] != 'Benchmark' else 0,
    axis=1
)

# =====================================================
# 1. TOP 20 HIGHEST RETURN OUTPERFORMERS
# =====================================================
# Filter for only strategies that beat the market
outperformers = df[(df['Strategy'] != 'Benchmark') & (df['Beat_Market'] == 'Yes')].copy()

# Rank by Total Return (highest first)
top10 = outperformers.nlargest(20, 'Total Return [%]')[
    ['Ticker', 'Strategy', 'Total Return [%]', 'Sharpe Ratio', 'Max Drawdown [%]',
     'Beat_Market', 'Market_Outperf']
].copy()

top10['Rank'] = range(1, len(top10) + 1)
top10 = top10[['Rank', 'Ticker', 'Strategy', 'Total Return [%]', 'Sharpe Ratio',
               'Max Drawdown [%]', 'Beat_Market', 'Market_Outperf']]

# =====================================================
# 2. STRATEGY SUMMARY
# =====================================================
strategy_summary = df[df['Strategy'] != 'Benchmark'].groupby('Strategy').agg({
    'Beat_Market': lambda x: (x == 'Yes').sum(),
    'Total Return [%]': 'mean',
    'Sharpe Ratio': 'mean',
    'Ticker': 'count'
}).round(2)

strategy_summary.columns = ['Wins', 'Avg Return %', 'Avg Sharpe', 'Count']
strategy_summary = strategy_summary.reset_index()

# =====================================================
# 3. CREATE DASHBOARD
# =====================================================
fig = make_subplots(
    rows=4, cols=1,
    row_heights=[0.35, 0.15, 0.35, 0.15],
    subplot_titles=("Top 20 Highest Return Strategies (Beat Market Only - Ranked by Total Return %)",
                    "Strategy Performance Summary",
                    "Risk vs Return: All Strategies",
                    "Key Findings"),
    specs=[[{"type": "table"}],
           [{"type": "table"}],
           [{"type": "scatter"}],
           [{"type": "table"}]],
    vertical_spacing=0.06
)

# Top 10 Table
fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Rank</b>", "<b>Stock</b>", "<b>Strategy</b>", "<b>Return %</b>",
                    "<b>Sharpe</b>", "<b>Max DD %</b>", "<b>Beat Market?</b>", "<b>Outperform %</b>"],
            fill_color="#0A2F35",
            font=dict(color="white", size=12),
            align="center",
            height=32
        ),
        cells=dict(
            values=[top10[col].values for col in top10.columns],
            fill_color=[["#1A1A2E" if i % 2 == 0 else "#2A2A3E" for i in range(len(top10))]],
            font=dict(color="#E0E0E0", size=11),
            align="center",
            height=28,
            format=[[".0f"], None, None, [".2f"], [".3f"], [".2f"], None, [".2f"]]
        )
    ),
    row=1, col=1
)

# Strategy Summary Table
fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Strategy</b>", "<b>Wins vs Market</b>", "<b>Avg Return %</b>",
                    "<b>Avg Sharpe</b>", "<b>Stocks Tested</b>"],
            fill_color="#0A2F35",
            font=dict(color="white", size=12),
            align="center",
            height=32
        ),
        cells=dict(
            values=[strategy_summary[col].values for col in strategy_summary.columns],
            fill_color="#1A1A2E",
            font=dict(color="#E0E0E0", size=11),
            align="center",
            height=28
        )
    ),
    row=2, col=1
)

# Risk vs Return Scatter
strategies_plot = df[df['Strategy'] != 'Benchmark'].copy()
strategy_colors = {
    'Trend': '#00CED1',
    'High_Vol': '#9370DB',
    'Low_Vol': '#20B2AA'
}

for strategy in ['Trend', 'High_Vol', 'Low_Vol']:
    strategy_data = strategies_plot[strategies_plot['Strategy'] == strategy]
    fig.add_trace(
        go.Scatter(
            x=strategy_data['Max Drawdown [%]'].abs(),
            y=strategy_data['Total Return [%]'],
            mode='markers',
            name=strategy.replace('_', ' '),
            marker=dict(
                size=strategy_data['Sharpe Ratio'].abs() * 10,
                color=strategy_colors.get(strategy, '#808080'),
                opacity=0.6,
                line=dict(width=1, color='white')
            ),
            text=strategy_data['Ticker'],
            hovertemplate="<b>%{text}</b><br>" +
                          "Return: %{y:.1f}%<br>" +
                          "Max DD: %{x:.1f}%<br>" +
                          "<extra></extra>"
        ),
        row=3, col=1
    )

# Key Findings
total_wins = (df[df['Strategy'] != 'Benchmark']['Beat_Market'] == 'Yes').sum()
total_tested = len(df[df['Strategy'] != 'Benchmark'])
win_rate = (total_wins / total_tested * 100) if total_tested > 0 else 0

best_combo = top10.iloc[0]
trend_wins = strategy_summary[strategy_summary['Strategy'] == 'Trend']['Wins'].values[0]

findings = pd.DataFrame({
    'Finding': [
        f"[+] {win_rate:.0f}% of strategy-stock combinations beat buy-and-hold ({total_wins}/{total_tested})",
        f"[+] Best performer: {best_combo['Ticker']} with {best_combo['Strategy']} strategy ({best_combo['Total Return [%]']:.1f}% return, {best_combo['Sharpe Ratio']:.2f} Sharpe)",
        f"[+] Trend strategy beat market on {trend_wins} stocks (most consistent)",
        f"[+] Analysis period: Jan 2022 - Nov 2024 (AI transformation era)"
    ]
})

fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Key Insights from AI/Tech Strategy Analysis</b>"],
            fill_color="#0A2F35",
            font=dict(color="white", size=13),
            align="left",
            height=32
        ),
        cells=dict(
            values=[findings['Finding'].values],
            fill_color="#1A1A2E",
            font=dict(color="#E0E0E0", size=12),
            align="left",
            height=32
        )
    ),
    row=4, col=1
)

# Layout
fig.update_layout(
    title={
        'text': "<b>AI/Tech Quantitative Strategy Analysis</b><br><sub>Performance Dashboard: 40 Stocks × 3 Strategies (2022-2024)</sub>",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 22, 'color': '#0A2F35'}
    },
    height=1400,
    showlegend=True,
    paper_bgcolor='#F5F7FA',
    plot_bgcolor='white',
    margin=dict(l=60, r=60, t=120, b=60)
)

fig.update_xaxes(title="Max Drawdown (%)", row=3, col=1, gridcolor='#E0E0E0')
fig.update_yaxes(title="Total Return (%)", row=3, col=1, gridcolor='#E0E0E0')

# Save
fig.write_html("performance_dashboard.html", include_plotlyjs="cdn")
print("\n" + "="*70)
print("[SUCCESS] Master dashboard created: performance_dashboard.html")
print("="*70)

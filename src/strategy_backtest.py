"""
AI/Tech Quantitative Strategy Analysis Platform

Outputs:
- analysis/<TICKER>_analysis.html (professional strategy performance dashboards)
- results/strategy_metrics.csv (comprehensive performance data)
- performance_dashboard.html (master comparison dashboard)
"""

# ==========================================================
# IMPORTS
# ==========================================================
import os
import re
import pandas as pd
import vectorbt as vbt
import pandas_ta as ta
import yfinance as yf

from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ==========================================================
# CONFIG
# ==========================================================
TICKERS = [
    # AI Chip Leaders
    "NVDA",   # NVIDIA - AI GPU leader
    "AMD",    # AMD - AI chips, MI300
    "AVGO",   # Broadcom - AI infrastructure
    "QCOM",   # Qualcomm - AI edge computing
    "INTC",   # Intel - AI chips
    "ARM",    # ARM Holdings - AI chip architecture

    # Big Tech AI Giants
    "MSFT",   # Microsoft - OpenAI partnership, Copilot
    "GOOGL",  # Google - Gemini, DeepMind
    "META",   # Meta - LLaMA, AI research
    "AAPL",   # Apple - Apple Intelligence
    "AMZN",   # Amazon - AWS AI, Bedrock
    "TSLA",   # Tesla - Full Self Driving, Optimus

    # Cloud/AI Infrastructure
    "ORCL",   # Oracle - Cloud AI
    "CRM",    # Salesforce - Einstein AI
    "NOW",    # ServiceNow - AI automation
    "SNOW",   # Snowflake - AI data platform

    # AI Software/Analytics
    "PLTR",   # Palantir - AI analytics platform
    "ADBE",   # Adobe - Firefly AI, creative tools
    "PANW",   # Palo Alto - AI security
    "CRWD",   # CrowdStrike - AI cybersecurity
    "DDOG",   # Datadog - AI monitoring

    # Banks/Finance with AI
    "JPM",    # JPMorgan - AI trading, operations
    "GS",     # Goldman Sachs - AI trading
    "MS",     # Morgan Stanley - AI advisor tools
    "BAC",    # Bank of America - Erica AI assistant
    "C",      # Citigroup - AI operations

    # Other AI Players
    "UBER",   # Uber - AI routing, autonomous
    "ABNB",   # Airbnb - AI pricing, matching
    "NFLX",   # Netflix - AI recommendations
    "SHOP",   # Shopify - AI commerce tools
    "SQ",     # Block - AI payments, Cash App

    # AI/Tech Sector ETFs & Indexes
    "SPY",    # S&P 500 ETF
    "QQQ",    # Nasdaq 100 ETF (tech heavy)
    "XLK",    # Technology Select Sector SPDR
    "VGT",    # Vanguard Information Technology ETF
    "SOXX",   # iShares Semiconductor ETF
    "IGV",    # iShares Expanded Tech-Software ETF
    "WCLD",   # WisdomTree Cloud Computing Fund
    "ARKK",   # ARK Innovation ETF (AI exposure)
    "BOTZ",   # Global X Robotics & AI ETF
    "IRBO"    # iShares Robotics and AI ETF
]

START_DATE = "2022-01-01"
INITIAL_CASH = 10_000
COMMISSION = 0.002
SIZE_PERCENT = 1

METRICS = ["total_return", "max_dd", "sharpe_ratio", "sortino_ratio", "calmar_ratio"]

# Extended metrics for detailed reporting
EXTENDED_METRICS = [
    "total_return", "annualized_return", "max_dd", "sharpe_ratio",
    "sortino_ratio", "calmar_ratio", "total_trades", "win_rate",
    "avg_winning_trade", "avg_losing_trade", "profit_factor",
    "best_return", "worst_return"
]

ANALYSIS_DIR = "analysis"
RESULTS_DIR = "results"
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def safe_filename(s):
    return re.sub(r"[^\w\-_\. ]", "_", s)

def getportfolio_stats(pf, metrics):
    try:
        s = pf.stats(metrics=metrics)
        return s.to_dict()
    except:
        return {m: None for m in metrics}

def get_first_trade_date(pf):
    try:
        df = pf.trades.records_readable
        if df is None or df.empty:
            return None
        for c in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[c]):
                return df[c].min()
        return None
    except:
        return None


def align_weekly_to_daily(series, daily_index, start):
    aligned = series.reindex(daily_index, method="ffill")
    return aligned.loc[start:]


def get_extended_stats(pf):
    """Get extended portfolio statistics using VectorBT's stats method"""
    stats = {}

    try:
        # Use the working metrics from the original code
        base_metrics = ["total_return", "max_dd", "sharpe_ratio", "sortino_ratio", "calmar_ratio"]
        base_stats = pf.stats(metrics=base_metrics).to_dict()  # CONVERT TO DICT!

        # Map to our extended stats dictionary - USE THE ACTUAL KEYS VECTORBT RETURNS!
        stats['total_return'] = base_stats.get('Total Return [%]', None)
        stats['max_dd'] = base_stats.get('Max Drawdown [%]', None)
        stats['sharpe_ratio'] = base_stats.get('Sharpe Ratio', None)
        stats['sortino_ratio'] = base_stats.get('Sortino Ratio', None)
        stats['calmar_ratio'] = base_stats.get('Calmar Ratio', None)

        # Calculate annualized return from total return and duration
        try:
            total_ret = stats['total_return']
            if total_ret is not None:
                # Get portfolio duration in years
                idx = pf.wrapper.index
                years = (idx[-1] - idx[0]).days / 365.25
                stats['annualized_return'] = ((1 + total_ret/100) ** (1/years) - 1) * 100 if years > 0 else None
            else:
                stats['annualized_return'] = None
        except:
            stats['annualized_return'] = None

        # Trade statistics
        try:
            trades = pf.trades.records_readable
            if trades is not None and len(trades) > 0:
                stats['total_trades'] = len(trades)

                # Calculate win rate
                wins = trades[trades['PnL'] > 0]
                stats['win_rate'] = (len(wins) / len(trades) * 100) if len(trades) > 0 else 0

                # Average winning/losing trades
                if len(wins) > 0:
                    stats['avg_winning_trade'] = (wins['Return'].mean() * 100) if 'Return' in wins.columns else None
                else:
                    stats['avg_winning_trade'] = None

                losses = trades[trades['PnL'] < 0]
                if len(losses) > 0:
                    stats['avg_losing_trade'] = (losses['Return'].mean() * 100) if 'Return' in losses.columns else None
                else:
                    stats['avg_losing_trade'] = None

                # Profit factor
                total_wins = wins['PnL'].sum() if len(wins) > 0 else 0
                total_losses = abs(losses['PnL'].sum()) if len(losses) > 0 else 0
                stats['profit_factor'] = (total_wins / total_losses) if total_losses > 0 else None

                # Best and worst trades
                if 'Return' in trades.columns:
                    stats['best_return'] = trades['Return'].max() * 100
                    stats['worst_return'] = trades['Return'].min() * 100
                else:
                    stats['best_return'] = None
                    stats['worst_return'] = None
            else:
                # No trades
                stats['total_trades'] = 0
                stats['win_rate'] = None
                stats['avg_winning_trade'] = None
                stats['avg_losing_trade'] = None
                stats['profit_factor'] = None
                stats['best_return'] = None
                stats['worst_return'] = None
        except:
            stats['total_trades'] = None
            stats['win_rate'] = None
            stats['avg_winning_trade'] = None
            stats['avg_losing_trade'] = None
            stats['profit_factor'] = None
            stats['best_return'] = None
            stats['worst_return'] = None

    except Exception as e:
        # Return None for all metrics
        for metric in EXTENDED_METRICS:
            stats[metric] = None

    return stats


def format_stat_value(metric_name, value):
    """Format metric values for display"""
    if value is None or pd.isna(value):
        return "N/A"

    # Percentage metrics
    if metric_name in ["total_return", "annualized_return", "max_dd", "win_rate",
                       "avg_winning_trade", "avg_losing_trade", "best_return", "worst_return"]:
        return f"{value:.2f}%"

    # Count metrics
    elif metric_name in ["total_trades"]:
        return f"{int(value)}"

    # Ratio metrics
    elif metric_name in ["sharpe_ratio", "sortino_ratio", "calmar_ratio", "profit_factor"]:
        return f"{value:.3f}"

    else:
        return f"{value:.2f}"


# ==========================================================
# DATA DOWNLOADERS
# ==========================================================
def download_weekly(ticker):
    df = yf.download(ticker, start=START_DATE, progress=False,multi_level_index=False)
    if df.empty:
        return None

    df = df.rename(columns={c:c.title() for c in df.columns})

    required = {"Open","High","Low","Close","Volume"}
    if not required.issubset(df.columns):
        return None

    weekly = df.resample("W").agg({
        "Open":"first",
        "High":"max",
        "Low":"min",
        "Close":"last",
        "Volume":"sum"
    }).dropna()

    return weekly


# ==========================================================
# STRATEGY BUILDERS
# ==========================================================
def build_weekly_trend_strategy(close, high, low):

    dc = ta.donchian(high=high, low=low, close=close, upper_length=10, lower_length=10)
    upper = dc["DCU_10_10"]

    st = ta.supertrend(high, low, close, length=20, multiplier=1.0)
    st_line = st["SUPERT_20_1.0"]
    st_dir = st["SUPERTd_20_1.0"]

    ema21 = ta.ema(close, length=21)
    ema50 = ta.ema(close, length=50)

    entries = (
        (close > upper.shift(1)) &
        (st_dir == 1) &
        (ema21 > ema50)
    ).fillna(False)

    exits = (
        (close < st_line) &
        (st_dir == -1)
    ).fillna(False)

    pf = vbt.Portfolio.from_signals(
        close, entries, exits,
        init_cash=INITIAL_CASH,
        freq="W",
        size=SIZE_PERCENT,
        fees=COMMISSION,
        size_type="percent"
    )

    return pf, st_dir


def build_daily_volatility_strategies(ticker, weekly_supertrend_dir):

    df = yf.download(ticker, start=START_DATE, progress=False,multi_level_index=False)
    if df.empty:
        return None, None, None, None, None

    df = df.rename(columns={c:c.title() for c in df.columns})
    close = df["Close"]; high = df["High"]; low = df["Low"]

    atr = vbt.IndicatorFactory.from_pandas_ta("atr").run(high, low, close, length=20).atrr
    atr_pct = (atr / close) * 100

    fast = vbt.MA.run(atr_pct, window=6, ewm=True).ma
    slow = vbt.MA.run(atr_pct, window=25, ewm=True).ma

    st_daily = weekly_supertrend_dir.reindex(close.index, method="ffill").fillna(0)

    entries = fast.vbt.crossed_above(slow)
    exits = fast.vbt.crossed_below(slow)

    high_vol = vbt.Portfolio.from_signals(
        close,
        entries & (st_daily == -1),
        exits,
        init_cash=INITIAL_CASH,
        freq="1D",
        fees=COMMISSION,
        size=SIZE_PERCENT,
        size_type="percent"
    )

    low_vol = vbt.Portfolio.from_signals(
        close,
        exits & (st_daily == -1),
        entries,
        init_cash=INITIAL_CASH,
        freq="1D",
        size=SIZE_PERCENT,
        size_type="percent"
    )

    return high_vol, low_vol, close, entries, exits


# ==========================================================
# MAIN ANALYSIS ENGINE
# ==========================================================
print("="*70)
print("AI/TECH QUANTITATIVE STRATEGY ANALYSIS")
print(f"Universe: {len(TICKERS)} tickers | Period: {START_DATE} - Present")
print("="*70)

all_results = []

for ticker in TICKERS:

    print(f"\n[{TICKERS.index(ticker)+1}/{len(TICKERS)}] Analyzing {ticker}...")

    weekly = download_weekly(ticker)
    if weekly is None:
        continue

    close_w, high_w, low_w = weekly["Close"], weekly["High"], weekly["Low"]

    # Weekly trend
    pf_trend, weekly_dir = build_weekly_trend_strategy(close_w, high_w, low_w)

    # Daily volatility
    high_vol, low_vol, close_d, ent_d, ex_d = build_daily_volatility_strategies(ticker, weekly_dir)
    if close_d is None:
        continue

    # First trade date logic
    first_dates = [
        get_first_trade_date(pf_trend),
        get_first_trade_date(high_vol),
        get_first_trade_date(low_vol)
    ]
    first_dates = [d for d in first_dates if d is not None]
    if not first_dates:
        continue

    start = min(first_dates)

    if start not in close_d.index:
        idxs = close_d.index[close_d.index >= start]
        if len(idxs)==0:
            continue
        start = idxs[0]

    bench_close = close_d.loc[start:]
    benchmark = vbt.Portfolio.from_holding(
        bench_close,
        init_cash=INITIAL_CASH,
        freq="1D"
    )

    # Save stats
    trend_stats = getportfolio_stats(pf_trend, METRICS)
    high_stats = getportfolio_stats(high_vol, METRICS)
    low_stats  = getportfolio_stats(low_vol, METRICS)
    ben_stats  = getportfolio_stats(benchmark, METRICS)

    all_results.append({
        "Ticker": ticker,
        "Trend": trend_stats,
        "High_Vol": high_stats,
        "Low_Vol": low_stats,
        "Benchmark": ben_stats
    })

    # ==========================================================
    # BUILD EQUITY + DRAWOWN FIGURE
    # ==========================================================
    trend_eq = align_weekly_to_daily(pf_trend.value(), close_d.index, start)
    high_eq  = high_vol.value().loc[start:]
    low_eq   = low_vol.value().loc[start:]
    ben_eq   = benchmark.value().loc[start:]

    df_equity = pd.DataFrame({
        "Trend": trend_eq,
        "High Vol": high_eq,
        "Low Vol": low_eq,
        "Benchmark": ben_eq
    }).ffill().bfill()

    df_dd = pd.DataFrame({
        "Trend": align_weekly_to_daily(pf_trend.drawdown(), close_d.index, start),
        "High Vol": high_vol.drawdown().loc[start:],
        "Low Vol": low_vol.drawdown().loc[start:],
        "Benchmark": benchmark.drawdown().loc[start:]
    }).reindex(df_equity.index).fillna(0)

    # Get extended statistics for all strategies
    trend_extended = get_extended_stats(pf_trend)
    high_extended = get_extended_stats(high_vol)
    low_extended = get_extended_stats(low_vol)
    bench_extended = get_extended_stats(benchmark)

    # Plot with 3 rows: equity, drawdown, statistics
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=False,
        row_heights=[0.45, 0.25, 0.30], vertical_spacing=0.08,
        subplot_titles=(f"{ticker} — Equity Curves", "Drawdowns", "Performance Statistics"),
        specs=[[{"type": "scatter"}], [{"type": "scatter"}], [{"type": "table"}]]
    )

    # Modern professional color scheme
    colors = {
        "Trend": "#00CED1",      # Dark Turquoise - momentum strategies
        "High Vol": "#9370DB",   # Medium Purple - volatility plays
        "Low Vol": "#20B2AA",    # Light Sea Green - defensive
        "Benchmark": "#FFD700"   # Gold - reference
    }

    for col in df_equity.columns:
        fig.add_trace(
            go.Scatter(x=df_equity.index, y=df_equity[col],
                       name=col, mode="lines",
                       line=dict(color=colors[col])),
            row=1, col=1
        )

    for col in df_dd.columns:
        fig.add_trace(
            go.Scatter(x=df_dd.index, y=df_dd[col],
                       name=col, mode="lines",
                       line=dict(color=colors[col]),
                       showlegend=False),
            row=2, col=1
        )

    # Build statistics table
    metric_labels = {
        "total_return": "Total Return",
        "annualized_return": "Annual Return",
        "max_dd": "Max Drawdown",
        "sharpe_ratio": "Sharpe Ratio",
        "sortino_ratio": "Sortino Ratio",
        "calmar_ratio": "Calmar Ratio",
        "total_trades": "Total Trades",
        "win_rate": "Win Rate",
        "avg_winning_trade": "Avg Win",
        "avg_losing_trade": "Avg Loss",
        "profit_factor": "Profit Factor",
        "best_return": "Best Trade",
        "worst_return": "Worst Trade"
    }

    # Build table data
    table_metrics = []
    table_trend = []
    table_high = []
    table_low = []
    table_bench = []

    for metric in EXTENDED_METRICS:
        table_metrics.append(metric_labels.get(metric, metric))
        table_trend.append(format_stat_value(metric, trend_extended.get(metric)))
        table_high.append(format_stat_value(metric, high_extended.get(metric)))
        table_low.append(format_stat_value(metric, low_extended.get(metric)))
        table_bench.append(format_stat_value(metric, bench_extended.get(metric)))

    # Add professional statistics table
    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>Metric</b>", "<b>Trend</b>", "<b>High Vol</b>", "<b>Low Vol</b>", "<b>Benchmark</b>"],
                fill_color="#0A2F35",
                font=dict(color="#FFFFFF", size=13),
                align="left",
                height=32
            ),
            cells=dict(
                values=[table_metrics, table_trend, table_high, table_low, table_bench],
                fill_color=["#1A1A2E", "#0F3A47", "#2E1A47", "#0F473A", "#473A0F"],
                font=dict(color="#E0E0E0", size=12),
                align="left",
                height=26
            )
        ),
        row=3, col=1
    )

    fig.update_layout(
        template="plotly_white",  # Light theme for professional look
        height=1100,
        hovermode="x unified",
        title={
            'text': f"<b>{ticker}</b> | Quantitative Strategy Analysis",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#0A2F35'}
        },
        margin=dict(l=60, r=60, t=90, b=60),
        paper_bgcolor='#F5F7FA',
        plot_bgcolor='white'
    )

    fig.update_yaxes(title="Portfolio Value ($)", row=1,col=1)
    fig.update_yaxes(title="Drawdown", tickformat=".0%", row=2,col=1)
    fig.update_xaxes(title="Date", row=2,col=1)

    out = os.path.join(ANALYSIS_DIR, f"{safe_filename(ticker)}_analysis.html")
    fig.write_html(out, include_plotlyjs="cdn")

    print(f"Completed: {ticker} | {out}")


# ==========================================================
# SUMMARY TABLE
# ==========================================================
rows = []
for r in all_results:
    t = r["Ticker"]
    for strat in ["Trend", "High_Vol", "Low_Vol", "Benchmark"]:
        d = {"Ticker": t, "Strategy": strat}
        d.update(r[strat])
        rows.append(d)

df_summary = pd.DataFrame(rows)
output_csv = os.path.join(RESULTS_DIR, "strategy_metrics.csv")
df_summary.to_csv(output_csv, index=False)

print(f"\nAnalysis Complete | Results: {output_csv}\n")

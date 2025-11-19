# Fortress 2.0 - Multi-Strategy Quantitative Trading Framework

A systematic trading framework that backtests three distinct strategies across 41 AI/Tech stocks from 2022-2024. Built with VectorBT and pandas-ta.

## Overview

This framework analyzes the AI transformation era (Jan 2022 - Nov 2024) using three complementary strategies:
- **Trend Following** (Weekly timeframe)
- **High Volatility Breakout** (Daily timeframe)
- **Low Volatility Mean Reversion** (Daily timeframe)

### Universe
41 AI/Tech tickers across semiconductors, cloud, AI, fintech, and tech ETFs including:
- Semiconductors: NVDA, AMD, AVGO, QCOM, INTC, ARM
- Cloud/AI: MSFT, GOOGL, META, AMZN, ORCL, CRM, NOW, SNOW, PLTR
- Cybersecurity: PANW, CRWD, DDOG
- Tech ETFs: SPY, QQQ, XLK, VGT, SOXX, IGV, WCLD, ARKK, BOTZ, IRBO

## Strategy Explanations

### 1. Trend Strategy (Weekly Timeframe)

**Philosophy**: Capture sustained uptrends in weekly price action

**Entry Conditions** (ALL must be true):
- Price breaks above 10-period Donchian Channel upper band
- Supertrend indicator is bullish (direction = 1)
- 21-period EMA is above 50-period EMA (medium-term trend confirmation)

**Exit Conditions** (ANY triggers exit):
- Price closes below Supertrend line
- Supertrend flips to bearish (direction = -1)

**Use Case**: Best for capturing major bull runs with lower trade frequency and larger position holding periods.

---

### 2. High Vol Strategy (Daily Timeframe)

**Philosophy**: Enter when volatility is EXPANDING during bearish trends (mean reversion play)

**How It Works**:
- Calculates ATR% (Average True Range as percentage of closing price)
- Fast EMA of ATR% (6-period) vs Slow EMA of ATR% (25-period)
- Trades volatility expansion/contraction cycles

**Entry Conditions** (ALL must be true):
- Fast ATR% crosses ABOVE Slow ATR% (volatility is increasing)
- Weekly Supertrend is bearish (direction = -1)

**Exit Conditions**:
- Fast ATR% crosses BELOW Slow ATR% (volatility is decreasing)

**Why This Works**:
When volatility expands during bearish periods, it often signals oversold conditions or panic selling. This strategy enters when fear is high (high volatility) and exits when volatility normalizes, capturing the mean reversion bounce.

**Use Case**: Counter-trend trading during market corrections or bearish periods. Captures short-term bounces when fear/volatility spikes.

---

### 3. Low Vol Strategy (Daily Timeframe)

**Philosophy**: Enter when volatility is COMPRESSING during bearish trends (anticipating breakouts)

**How It Works**:
- Uses same ATR% indicators as High Vol strategy
- Opposite entry/exit logic - trades volatility compression

**Entry Conditions** (ALL must be true):
- Fast ATR% crosses BELOW Slow ATR% (volatility is decreasing)
- Weekly Supertrend is bearish (direction = -1)

**Exit Conditions**:
- Fast ATR% crosses ABOVE Slow ATR% (volatility is increasing)

**Why This Works**:
Volatility compression (low vol) during bearish trends often precedes breakout moves. When volatility contracts, it indicates consolidation and price coiling. This strategy enters during the quiet period and exits when volatility expands (breakout happens).

**Use Case**: Captures breakout moves after consolidation periods. Enters during calm, exits during explosive moves.

---

## Key Differences: High Vol vs Low Vol

| Aspect | High Vol Strategy | Low Vol Strategy |
|--------|-------------------|------------------|
| **Entry Signal** | Volatility EXPANDING (fast > slow) | Volatility COMPRESSING (fast < slow) |
| **Exit Signal** | Volatility DECREASING (fast < slow) | Volatility INCREASING (fast > slow) |
| **Market State** | Enters during fear/panic | Enters during consolidation |
| **Trade Type** | Mean reversion bounce | Breakout anticipation |
| **Holding Period** | Shorter (quick bounce) | Variable (until breakout) |
| **Risk Profile** | Higher (catching falling knife) | Lower (entering during calm) |

Both strategies only trade during bearish weekly trends (Supertrend = -1), making them counter-trend strategies that complement the bullish Trend strategy.

---

## Project Structure

```
Fortress2/
├── src/
│   ├── strategy_backtest.py        # Main backtest engine
│   ├── build_dashboard.py          # Performance summary dashboard
│   └── top_performers_analysis.py  # Top strategies analysis
├── results/
│   ├── strategy_metrics.csv        # All strategy results
│   └── top_performers_detailed.csv # Filtered best performers
├── analysis/
│   └── [TICKER]_analysis.html      # Individual stock reports
├── performance_dashboard.html       # Master dashboard
└── top_performers.html             # Top 25 strategies dashboard
```

## Installation

```bash
# Create conda environment
conda create -n fortress_env python=3.10
conda activate fortress_env

# Install dependencies
pip install vectorbt pandas pandas-ta yfinance plotly
```

## Usage

```bash
# 1. Run backtests (generates results/strategy_metrics.csv)
python src/strategy_backtest.py

# 2. Build performance dashboard
python src/build_dashboard.py

# 3. Generate top performers analysis
python src/top_performers_analysis.py
```

## Output

### Dashboards
- **performance_dashboard.html**: Top 20 highest return outperformers, strategy summary, risk/return scatter
- **top_performers.html**: Top 25 ranked by composite score (Sharpe + Return + Outperformance)
- **analysis/[TICKER]_analysis.html**: Individual stock deep-dive with equity curves and trade analysis

### CSV Exports
- **results/strategy_metrics.csv**: Complete results for all 41 tickers × 3 strategies
- **results/top_performers_detailed.csv**: Filtered strategies that beat benchmarks

## Performance Metrics

Each strategy is evaluated on:
- Total Return %
- Sharpe Ratio (risk-adjusted return)
- Sortino Ratio (downside risk-adjusted)
- Calmar Ratio (return/max drawdown)
- Max Drawdown %
- Win Rate %
- Profit Factor
- Total Trades

## Configuration

Key parameters in `strategy_backtest.py`:

```python
START_DATE = "2022-01-01"
INITIAL_CASH = 100_000
SIZE_PERCENT = 95  # 95% position sizing
COMMISSION = 0.001  # 0.1% per trade

# Trend Strategy (Weekly)
- Donchian: 10 periods
- Supertrend: 20-period, 1.0 multiplier
- EMAs: 21 and 50

# Volatility Strategies (Daily)
- ATR: 20-period
- Fast EMA: 6-period
- Slow EMA: 25-period
```

## Results Highlights

The framework identifies:
- Strategies that outperformed buy-and-hold benchmarks
- Risk-adjusted returns across different market conditions
- Best strategy-stock combinations for each approach
- Performance during the AI transformation era (2022-2024)

## Technology Stack

- **VectorBT**: High-performance backtesting engine
- **pandas-ta**: Technical indicators (Supertrend, Donchian, ATR, EMAs)
- **yfinance**: Market data
- **Plotly**: Interactive HTML dashboards
- **pandas**: Data manipulation and analysis

## Author

Quantitative trading framework for analyzing systematic strategies across AI/tech sectors.

---

Generated with data through November 2024

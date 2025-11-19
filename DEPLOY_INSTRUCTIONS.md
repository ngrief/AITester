# GitHub Pages Deployment Instructions

## Enable GitHub Pages

Follow these steps to deploy your interactive dashboard:

### 1. Go to Repository Settings
- Navigate to: https://github.com/ngrief/AITester
- Click **Settings** tab (top right)

### 2. Enable GitHub Pages
- Scroll down to **Pages** section (left sidebar)
- Under **Source**, select:
  - Branch: **master** (or **main**)
  - Folder: **/ (root)**
- Click **Save**

### 3. Wait for Deployment
- GitHub will build and deploy your site (takes 1-2 minutes)
- You'll see a message: "Your site is live at https://ngrief.github.io/AITester/"

### 4. Access Your Live Dashboard
Once deployed, your dashboard will be available at:

**Main Landing Page:**
https://ngrief.github.io/AITester/

**Direct Dashboard Link:**
https://ngrief.github.io/AITester/performance_dashboard.html

---

## What Gets Deployed?

✅ **index.html** - Professional landing page with project overview
✅ **performance_dashboard.html** - Interactive Plotly dashboard (Top 20 performers)
✅ **analysis/** - Individual stock analysis pages (40 HTML files)
✅ **results/** - CSV data files

---

## LinkedIn Post Ideas

### Option 1: Share Landing Page
```
🚀 Just backtested 3 systematic trading strategies across 41 AI/Tech stocks!

Analyzed the AI transformation era (2022-2024) using:
📈 Trend Following (weekly)
💥 High Volatility (mean reversion)
🎯 Low Volatility (breakout anticipation)

Interactive dashboard → https://ngrief.github.io/AITester/

#QuantitativeFinance #TradingStrategies #Python #VectorBT
```

### Option 2: Share Direct Dashboard
```
📊 Fortress 2.0 Results: Multi-Strategy Analysis of AI/Tech Stocks

Backtested NVDA, AMD, MSFT, META, GOOGL + 36 more stocks using 3 systematic strategies.

See which approaches beat buy-and-hold →
https://ngrief.github.io/AITester/performance_dashboard.html

Built with VectorBT & Python

#AlgoTrading #DataScience #FinTech
```

### Option 3: Technical Deep-Dive
```
🔬 Breaking down volatility-based trading strategies:

High Vol: Enter when volatility EXPANDS during downtrends (catch panic bounces)
Low Vol: Enter when volatility COMPRESSES (anticipate breakouts)

Both complement traditional trend following.

Full analysis of 41 AI/Tech stocks (2022-2024) →
https://ngrief.github.io/AITester/

#QuantDev #SystematicTrading #Python
```

---

## For LinkedIn Image Posts

If you still want static images for LinkedIn:

### Quick Screenshot Method:
1. Open: https://ngrief.github.io/AITester/performance_dashboard.html
2. Press **F12** (DevTools)
3. Press **Ctrl + Shift + P**
4. Type "screenshot"
5. Select "Capture full size screenshot"
6. Saves as PNG automatically

**Recommended crop:** Top 20 table + scatter plot section
**Format:** PNG (1200x627px or 1200x1200px)

---

## Troubleshooting

**Site not loading?**
- Wait 2-3 minutes after enabling Pages
- Check GitHub Actions tab for build status
- Clear browser cache and try again

**404 Error?**
- Verify Pages is enabled from **master** branch, **root** folder
- Check that index.html exists in repository root

**Dashboard not interactive?**
- Make sure you're viewing the HTML, not the raw file
- Plotly requires JavaScript enabled in browser

---

## Update Dashboard

To update the dashboard with new data:

```bash
cd "/c/Users/ntrie/OneDrive/Documents/Data Projects/Quant Software/Fortress2"

# Run new backtest
python src/strategy_backtest.py

# Rebuild dashboards
python src/build_dashboard.py

# Commit and push
git add performance_dashboard.html results/ analysis/
git commit -m "Update dashboard with latest data"
git push

# GitHub Pages will automatically redeploy in ~2 minutes
```

---

**Live Site:** https://ngrief.github.io/AITester/
**Repository:** https://github.com/ngrief/AITester

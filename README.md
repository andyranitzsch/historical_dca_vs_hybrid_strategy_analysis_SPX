# Historical DCA vs Hybrid Strategy Analysis - S&P 500

A comprehensive data-driven analysis comparing Dollar-Cost Averaging (DCA) against hybrid "buy-the-dip" strategies using 75 years of S&P 500 historical data (1950-2025).

## 🎯 Key Finding

**DCA beats hybrid strategies in 94% of 462 tested scenarios.**

Trying to time the market by waiting for dips—even severe 30% crashes—consistently underperforms simple, regular investing.

## 📊 Analysis Overview

We tested **462 scenarios** varying:
- **11 start periods** (1950-2020)
- **7 buy days per month** (1st, 5th, 10th, 15th, 20th, 25th, 28th)
- **6 hybrid strategies** (deploy cash at -5%, -10%, -15%, -20%, -25%, -30% drops)

### Strategy Comparison

**DCA (Dollar-Cost Averaging):**
- Invest full monthly budget ($1,000) consistently

**Hybrid (Buy-the-Dip):**
- Invest 50% monthly ($500)
- Hold 50% in cash at 3% risk-free rate
- Deploy all cash when market drops X% from 52-week high (252 trading days)

## 📈 Results Summary

| Metric | DCA | Best Hybrid |
|--------|-----|-------------|
| **Win Rate** | 93.9% | 6.1% |
| **Avg CAGR** | 6.14% | 5.88% |
| **Outperformance** | +0.26% | - |

### Performance by Drop Threshold

| Drop % | Hybrid Win Rate | CAGR vs DCA |
|--------|----------------|-------------|
| 5% | 0% | -0.20% |
| 10% | 0% | -0.29% |
| 15% | 0% | -0.21% |
| 20% | 9% | -0.26% |
| 25% | 9% | -0.21% |
| 30% | 18% | -0.37% |

**Even waiting for 30% crashes only wins 18% of the time!**

## 💡 Key Insights

1. **Buy day doesn't matter** - Investing on the 1st vs 28th differs by only 0.01% CAGR
2. **Opportunity cost kills returns** - Holding cash at 3% while markets grow at 8-10% compounds negatively
3. **Major dips are rare** - Only 3-7 events with 20%+ drops occur in 30 years
4. **Time in market > Timing the market** - Confirmed across all time periods

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Analysis

```bash
# Basic comparison (1995-2025, 20% drop threshold)
python sp500_cagr_sim.py "^spx_d.csv" --start 1995-01-01 --drop 0.20

# Custom parameters
python sp500_cagr_sim.py "^spx_d.csv" \
  --start 2000-01-01 \
  --end 2020-12-31 \
  --budget 1000 \
  --buy-day 15 \
  --rf 0.03 \
  --drop 0.15

# See all options
python sp500_cagr_sim.py --help
```

### Parameters

- `--start`: Start date (YYYY-MM-DD)
- `--end`: End date (YYYY-MM-DD, optional)
- `--budget`: Monthly investment amount (default: 1000)
- `--buy-day`: Day of month to buy (default: 15)
- `--rf`: Risk-free annual rate (default: 0.03 for 3%)
- `--drop`: Drop percentage to trigger lump buy (default: 0.20 for 20%)

## 📁 Repository Contents

### Core Files
- `sp500_cagr_sim.py` - Main simulation script
- `^spx_d.csv` - S&P 500 historical daily data (1789-2025)
- `requirements.txt` - Python dependencies

### Reports
- `DCA_vs_Hybrid_Report.md` - Full professional report
- `DCA_Infographic_Summary.md` - Visual/social media friendly summary
- `DCA_vs_Hybrid_Summary.txt` - Plain text summary

### Results Data
- `comprehensive_results.csv` - 77 scenarios (start year × buy day)
- `ultimate_results.csv` - 462 scenarios (start year × buy day × drop %)

## 📖 Understanding the Results

### Why "11% S&P Return" vs Our 6-8% CAGR?

| Return Type | Value | What It Means |
|------------|-------|---------------|
| Average Annual Return | ~10-11% | Simple arithmetic mean (what headlines quote) |
| Market CAGR | ~8-9% | Real compounded return accounting for volatility |
| DCA CAGR | ~6-8% | Return measured against total contributions over time |

The 2-3% gap is due to:
1. **Volatility drag** (CAGR < average return)
2. **DCA methodology** (comparing final value to ALL contributions, not just initial investment)

### Real Example (1995-2025)

**Scenario:** Invest $1,000/month for 30 years

| Strategy | Contributions | Final Value | CAGR |
|----------|--------------|-------------|------|
| **DCA** | $370,000 | $1,758,866 | 5.20% |
| **Hybrid (20% drop)** | $370,000 | $1,648,603 | 4.98% |

**Cost of timing:** $110,263 lost

## 🛠️ Methodology

1. **Data Source:** S&P 500 daily closing prices (1950-2025) from [Stooq.com](https://stooq.com/q/d/?s=%5Espx)
2. **Backtesting:** Historical simulation with no lookahead bias
3. **Hybrid Trigger Logic:**
   - Track 252 trading days (≈52-week) rolling high
   - When new high is set, "arm" the trigger
   - Deploy all cash when price drops X% from that high
   - Reset after deployment
   - *Note: Uses trading days (market open days), not calendar days*
4. **CAGR Calculation:** `(final_value / total_contributed)^(1/years) - 1`

## 📊 Visualization Ideas

The data in the CSV files can be used to create:
- Heatmaps showing CAGR by start year and drop percentage
- Time series of equity curves comparing strategies
- Distribution plots of CAGR differences
- Win rate analysis by decade

## 🔬 Addendum: What Happens if Risk-Free Interest Rate is Higher?

The base analysis assumes a 3% annual return on cash held by the hybrid strategy. But what if you could earn more on cash reserves? Here's the sensitivity analysis:

### Interest Rate Impact (1995-2025 scenario)

| Risk-Free Rate | DCA CAGR | Hybrid CAGR | Winner | Difference |
|----------------|----------|-------------|--------|------------|
| 3.0% | 5.20% | 4.98% | **DCA** | DCA +0.22% |
| 4.0% | 5.20% | 5.04% | **DCA** | DCA +0.16% |
| 6.0% | 5.20% | 5.18% | **DCA** | DCA +0.02% |
| **6.5%** | 5.20% | **5.22%** | **Hybrid** | Hybrid +0.02% |

### 🎯 Break-Even Point: ~6.0-6.5%

The hybrid strategy only wins when cash earns **above 6% annually**—a rate rarely sustained in modern markets.

### 📉 Historical Reality Check

**Average US Treasury Bill rates by decade:**
- 1950s-1970s: 2-5%
- 1980s: 10-15% (inflation crisis—exceptional period)
- 1990s-2000s: 3-5%
- 2010s: 0-2% (near-zero rates)
- 2020s: 0-5%

**Long-term average (1950-2025): ~4%**

### 💡 Key Takeaway

Even with a generous 4% assumption (above historical average), **DCA still outperforms by 0.16% annually**. The hybrid strategy only becomes competitive at unrealistic, unsustainable cash rates above 6%.

This reinforces the core finding: **time in the market beats timing the market**, even when "waiting for dips" earns solid returns.

**To test different rates yourself:**
```bash
python sp500_cagr_sim.py "^spx_d.csv" --start 1995-01-01 --rf 0.04  # Test with 4%
python sp500_cagr_sim.py "^spx_d.csv" --start 1995-01-01 --rf 0.06  # Test with 6%
```

## ⚠️ Disclaimer

This analysis is for **educational purposes only** and is not financial advice. Past performance does not guarantee future results. Always consult with a qualified financial advisor before making investment decisions.

## 📝 License

MIT License - Feel free to use this code and data for your own analysis.

## 🤝 Contributing

Contributions welcome! Ideas for improvement:
- Add more index comparisons (NASDAQ, Russell 2000)
- Test different hybrid allocation ratios (60/40, 70/30)
- Include dividend reinvestment
- Add transaction costs and taxes
- Test international markets

## 📬 Contact

Questions or suggestions? Open an issue or submit a pull request!

---

**Built with Python, pandas, and numpy | Analysis completed: October 2025**


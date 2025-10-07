
"""
S&P 500 CAGR: DCA vs Hybrid
---------------------------
Input CSV columns required: Date, Open, High, Low, Close, Volume
Only Close is used.

How it works
- DCA: invest monthly_budget on the first trading day on/after `buy_day` each month.
- Hybrid: invest 50% monthly, keep 50% in cash accruing risk-free; deploy all cash
  on the first day Close drops below threshold (e.g., 80% = 20% drop) of the rolling 
  252-trading-day high after a new high.

CAGR is computed vs total contributions: (final_equity / total_contributed)**(1/years) - 1

Usage:
    python sp500_cagr_sim.py data.csv --start 1995-01-01 --end 2025-01-01 --budget 1000 --buy-day 15 --rf 0.03 --drop 0.20

Parameters:
    --start: Start date (YYYY-MM-DD)
    --end: End date (YYYY-MM-DD, optional)
    --budget: Monthly investment amount (default: 1000)
    --buy-day: Day of month to buy (default: 15)
    --rf: Risk-free annual rate (default: 0.03 for 3%)
    --drop: Drop percentage to trigger lump buy (default: 0.20 for 20%)
"""

import argparse
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

@dataclass
class Result:
    final_value: float
    total_contributed: float
    years: float
    cagr: float
    max_drawdown: float
    num_lump_events: int
    as_of: str

def _load(csv_path: str, start: Optional[str], end: Optional[str] = None) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in ["Date", "Close"]:
        if col not in df.columns:
            raise ValueError("CSV must have 'Date' and 'Close' columns.")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").dropna(subset=["Close"]).reset_index(drop=True)
    if start:
        df = df[df["Date"] >= pd.to_datetime(start)].reset_index(drop=True)
    if end:
        df = df[df["Date"] <= pd.to_datetime(end)].reset_index(drop=True)
    if len(df) < TRADING_DAYS_PER_YEAR:
        raise ValueError("Need at least ~1 year of daily data.")
    return df

def _daily_rf(annual: float) -> float:
    return (1.0 + annual) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0

def _monthly_buy_dates(trading_days: pd.Series, buy_day: int) -> pd.DatetimeIndex:
    by_month = {}
    months = sorted(set((d.year, d.month) for d in trading_days))
    month_to_days = {}
    for d in trading_days:
        month_to_days.setdefault((d.year, d.month), []).append(d)
        if d.day >= buy_day:
            by_month.setdefault((d.year, d.month), d)
    for mk in months:
        if mk not in by_month:
            by_month[mk] = month_to_days[mk][-1]
    return pd.DatetimeIndex(sorted(by_month.values()))

def _trigger_flags(prices: pd.Series, drop_pct: float = 0.20) -> pd.Series:
    """
    Detect trigger points when price drops from rolling high.
    
    Args:
        prices: Series of closing prices
        drop_pct: Percentage drop to trigger (e.g., 0.20 for 20% drop)
    """
    threshold = 1.0 - drop_pct  # e.g., 0.20 drop = 0.80 threshold
    highs = prices.rolling(TRADING_DAYS_PER_YEAR, min_periods=1).max()
    triggered = np.zeros(len(prices), dtype=bool)
    armed = False
    last_high = -np.inf
    for i, (p, h) in enumerate(zip(prices.values, highs.values)):
        if p >= h and p > last_high:
            armed = True
            last_high = p
        if armed and p <= threshold * h:
            triggered[i] = True
            armed = False
    return pd.Series(triggered, index=prices.index)

def _max_dd(equity: np.ndarray) -> float:
    peak = np.maximum.accumulate(equity)
    # Avoid division by zero when peak is 0
    with np.errstate(divide='ignore', invalid='ignore'):
        dd = np.where(peak > 0, (peak - equity) / peak, 0)
    return float(np.max(dd))

def simulate_dca(df: pd.DataFrame, budget: float, buy_day: int, rf_annual: float) -> Result:
    dates = df["Date"]
    prices = df["Close"].astype(float).to_numpy()
    buy_dates = _monthly_buy_dates(dates, buy_day)
    daily_rf = _daily_rf(rf_annual)

    shares = 0.0
    cash = 0.0
    contrib = 0.0
    eq_curve = []

    for i, dt in enumerate(dates):
        cash *= (1.0 + daily_rf)
        if dt in buy_dates:
            contrib += budget
            shares += budget / prices[i]
        eq_curve.append(shares * prices[i] + cash)

    eq = np.array(eq_curve)
    years = (dates.iloc[-1] - dates.iloc[0]).days / 365.25
    final_val = float(eq[-1])
    cagr = (final_val / contrib) ** (1 / years) - 1 if contrib > 0 else np.nan
    return Result(final_val, contrib, years, cagr, _max_dd(eq), 0, dates.iloc[-1].date().isoformat())

def simulate_hybrid(df: pd.DataFrame, budget: float, buy_day: int, rf_annual: float, drop_pct: float = 0.20) -> Result:
    dates = df["Date"]
    prices = df["Close"].astype(float).to_numpy()
    buy_dates = _monthly_buy_dates(dates, buy_day)
    triggers = _trigger_flags(df["Close"], drop_pct)
    daily_rf = _daily_rf(rf_annual)

    shares = 0.0
    cash = 0.0
    contrib = 0.0
    lumps = 0
    eq_curve = []

    for i, dt in enumerate(dates):
        cash *= (1.0 + daily_rf)
        if dt in buy_dates:
            now = budget * 0.5
            later = budget * 0.5
            contrib += budget
            shares += now / prices[i]
            cash += later
        if triggers.iloc[i] and cash > 0:
            shares += cash / prices[i]
            cash = 0.0
            lumps += 1
        eq_curve.append(shares * prices[i] + cash)

    eq = np.array(eq_curve)
    years = (dates.iloc[-1] - dates.iloc[0]).days / 365.25
    final_val = float(eq[-1])
    cagr = (final_val / contrib) ** (1 / years) - 1 if contrib > 0 else np.nan
    return Result(final_val, contrib, years, cagr, _max_dd(eq), lumps, dates.iloc[-1].date().isoformat())

def run(csv_path: str, start: Optional[str], end: Optional[str], budget: float, buy_day: int, rf: float, drop_pct: float = 0.20):
    df = _load(csv_path, start, end)
    dca = simulate_dca(df, budget, buy_day, rf)
    hyb = simulate_hybrid(df, budget, buy_day, rf, drop_pct)
    return dca, hyb

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Compare DCA vs Hybrid investment strategies")
    ap.add_argument("csv", help="Path to CSV file with Date and Close columns")
    ap.add_argument("--start", type=str, default=None, help="Start date (YYYY-MM-DD)")
    ap.add_argument("--end", type=str, default=None, help="End date (YYYY-MM-DD)")
    ap.add_argument("--budget", type=float, default=1000.0, help="Monthly investment budget")
    ap.add_argument("--buy-day", type=int, default=15, help="Day of month to buy (1-31)")
    ap.add_argument("--rf", type=float, default=0.03, help="Risk-free annual rate (e.g., 0.03 for 3%%)")
    ap.add_argument("--drop", type=float, default=0.20, help="Drop percentage to trigger lump buy (e.g., 0.20 for 20%%)")
    args = ap.parse_args()

    dca, hyb = run(args.csv, args.start, args.end, args.budget, args.buy_day, args.rf, args.drop)
    print(f"As-of: {dca.as_of}")
    print(f"Years: {dca.years:.2f}")
    print(f"Drop trigger: {args.drop:.0%}")
    print("--- DCA ---")
    print(f"Final ${dca.final_value:,.2f} | Contrib ${dca.total_contributed:,.2f} | CAGR {dca.cagr:.4%} | MaxDD {dca.max_drawdown:.2%}")
    print("--- Hybrid ---")
    print(f"Final ${hyb.final_value:,.2f} | Contrib ${hyb.total_contributed:,.2f} | CAGR {hyb.cagr:.4%} | MaxDD {hyb.max_drawdown:.2%} | Lump events {hyb.num_lump_events}")

if __name__ == "__main__":
    main()

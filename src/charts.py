"""Charts: sentiment vs price, forecast vs actual, walk-forward equity.

All charts are drawn from the actual CSV outputs of this run, never
from invented values. Matplotlib only; no seaborn dependency.
"""
import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def chart_sentiment_vs_price(bars_csv: str, out: str) -> None:
    df = pd.read_csv(bars_csv, parse_dates=["date"])
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(df["date"], df["close"], color="#1f77b4", lw=1.2, label="BTC close (USD)")
    ax1.set_ylabel("BTC close (USD)")
    ax2 = ax1.twinx()
    ax2.plot(df["date"], df["sentiment_mean_7d"], color="#d62728", lw=1.2,
             label="7-day mean sentiment (-1..+1)")
    ax2.set_ylabel("7-day mean sentiment")
    ax2.set_ylim(-1, 1)
    ax1.set_title("Bitcoin: 7-day mean tweet sentiment vs. close price")
    ax1.set_xlabel("Date (daily bars, sample period)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def chart_forecast_vs_actual(pred_csv: str, horizon: int, out: str) -> None:
    pred = pd.read_csv(pred_csv, parse_dates=["date"])
    sub = pred[pred["horizon"] == horizon].sort_values("date")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(sub["date"], sub["actual_close"], color="#1f77b4", lw=1.2, label="Actual close")
    ax.plot(sub["date"], sub["pred_close"], color="#ff7f0e", lw=1.0, label="Walk-forward predicted close")
    ax.set_title(f"Walk-forward forecast vs. actual -- horizon n+{horizon} (out-of-sample only)")
    ax.set_ylabel("BTC close (USD)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def chart_equity(pred_csv: str, out: str) -> None:
    """Equity curves for the LAGGED, executable backtest only.

    Signal on day t comes from the h=1 prediction made on day t-1;
    realised return is the clean 1-day return on day t (h=0 actual).
    The naive same-day curve is deliberately NOT plotted: it is
    inflated by the sample's same-day label alignment (see report).
    """
    pred = pd.read_csv(pred_csv, parse_dates=["date"])
    h0 = pred[pred["horizon"] == 0].sort_values("date").reset_index(drop=True)
    h1 = pred[pred["horizon"] == 1].sort_values("date").reset_index(drop=True)
    signal = h1["pred_return"].shift(1).to_numpy()
    mask = ~pd.isna(signal)
    dates = h0["date"][mask]
    strat = np.where(signal[mask] > 0, h0["actual_return"][mask].to_numpy(), 0.0)
    bh = h0["actual_return"][mask].to_numpy()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, np.exp(np.cumsum(strat)), label="Lagged sentiment-signal strategy (long/flat)")
    ax.plot(dates, np.exp(np.cumsum(bh)), label="Buy-and-hold BTC (same period)")
    ax.set_title("Out-of-sample equity curves -- lagged, executable signal only")
    ax.set_ylabel("Growth of $1 (log-return compounding, before fees)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", default="data/joined_daily_bars.csv")
    ap.add_argument("--pred", default="data/predictions_walkforward.csv")
    ap.add_argument("--outdir", default="charts")
    args = ap.parse_args()
    chart_sentiment_vs_price(args.bars, f"{args.outdir}/sentiment_vs_price.png")
    chart_forecast_vs_actual(args.pred, 1, f"{args.outdir}/forecast_vs_actual_h1.png")
    chart_forecast_vs_actual(args.pred, 5, f"{args.outdir}/forecast_vs_actual_h5.png")
    chart_equity(args.pred, f"{args.outdir}/walkforward_cumulative.png")
    print("charts written to", args.outdir)


if __name__ == "__main__":
    main()

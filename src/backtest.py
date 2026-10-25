"""Trading-signal backtests from out-of-sample predictions.

Horizon indexing (read this before using any number here):
  In src/features.py, a row dated ``t`` aggregates sentiment for day
  ``t`` and sets ``prev_close = close_{t-1}``. ``target_close_h{h}``
  is ``close_{t+h}`` and ``target_return_h{h}`` is
  ``log(close_{t+h}) - log(prev_close)``. So from the last observed
  close, the look-ahead is h+1 days, not h days. The h=1 predicted
  return therefore spans TWO days and must never be treated as a
  1-day return.

Two backtests are reported, and the distinction matters:

1. NAIVE same-day backtest (NOT a credible trading result):
   Signal on row t from that row's h=0 prediction, realised return
   = actual_return_h0 on the same row. This is inflated in this
   sample because the dataset's daily sentiment label agrees with
   the same day's price-return sign on ~94% of days (see the report:
   99.9% of days have all 10 sampled tweets sharing one label).
   That alignment is a property of how the sample was labelled /
   sampled, not evidence of a tradable edge. It is reported only so
   a reviewer can see the artefact, with this warning attached.

2. LAGGED (executable) backtest -- the honest predictive test:
   At the end of day t-1, take the model's h=1 prediction made on
   row t-1 (which uses only sentiment up to t-1 and prices up to
   t-2). If it is positive, hold BTC during day t; otherwise hold
   cash. Realised return on day t is the clean 1-day return
   log(close_t / close_{t-1}), i.e. actual_return_h0 on row t.
   No same-day sentiment is used. No leverage, no shorting, no
   fees/slippage modelled.

Benchmark in each case: buy-and-hold BTC over the same rows.

Metrics (daily crypto bars, 365 days/year, risk-free rate 0):
  Sharpe  = mean / std * sqrt(365)
  Sortino = mean / downside-deviation * sqrt(365)
  Max Drawdown = worst peak-to-trough fall of exp(cumulative log-return).
A metric with a zero denominator is reported as null, never invented.
"""
import argparse
import json

import numpy as np
import pandas as pd


def sharpe(rets: np.ndarray) -> float | None:
    sd = rets.std(ddof=1)
    return float(rets.mean() / sd * np.sqrt(365)) if sd > 0 else None


def sortino(rets: np.ndarray) -> float | None:
    downside = rets[rets < 0]
    dd = float(np.sqrt(np.mean(downside ** 2))) if len(downside) else 0.0
    return float(rets.mean() / dd * np.sqrt(365)) if dd > 0 else None


def max_drawdown(log_rets: np.ndarray) -> float:
    equity = np.exp(np.cumsum(log_rets))
    peak = np.maximum.accumulate(equity)
    return float(np.min(equity / peak - 1.0))


def block(rets: np.ndarray, bh: np.ndarray) -> dict:
    return {
        "sharpe_ratio": sharpe(rets),
        "sortino_ratio": sortino(rets),
        "max_drawdown": max_drawdown(rets),
        "total_log_return": float(rets.sum()),
        "buy_and_hold_same_period": {
            "sharpe_ratio": sharpe(bh),
            "sortino_ratio": sortino(bh),
            "max_drawdown": max_drawdown(bh),
            "total_log_return": float(bh.sum()),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="data/predictions_walkforward.csv")
    ap.add_argument("--out", default="data/backtest.json")
    args = ap.parse_args()
    pred = pd.read_csv(args.pred, parse_dates=["date"]).sort_values(["horizon", "date"])
    h0 = pred[pred["horizon"] == 0].sort_values("date").reset_index(drop=True)
    h1 = pred[pred["horizon"] == 1].sort_values("date").reset_index(drop=True)

    # 1. Naive same-day (inflated -- see module docstring).
    naive_strat = np.where(h0["pred_return"].to_numpy() > 0,
                           h0["actual_return"].to_numpy(), 0.0)
    naive = block(naive_strat, h0["actual_return"].to_numpy())
    naive["n_test_days"] = int(len(h0))
    naive["period_start"] = str(h0["date"].min().date())
    naive["period_end"] = str(h0["date"].max().date())
    naive["warning"] = (
        "INFLATED BY SAMPLE CONSTRUCTION: daily sentiment sign agrees "
        "with same-day return sign on ~94% of days in this sample. "
        "Do NOT use this block as a trading result."
    )

    # 2. Lagged, executable: signal from row t-1 (h=1 prediction),
    #    realised 1-day return on row t (h=0 actual).
    merged = h0[["date", "actual_return"]].copy()
    merged["signal_pred_return"] = h1["pred_return"].shift(1).to_numpy()
    lagged = merged.dropna(subset=["signal_pred_return"]).reset_index(drop=True)
    lag_strat = np.where(lagged["signal_pred_return"].to_numpy() > 0,
                         lagged["actual_return"].to_numpy(), 0.0)
    lag = block(lag_strat, lagged["actual_return"].to_numpy())
    lag["n_test_days"] = int(len(lagged))
    lag["period_start"] = str(lagged["date"].min().date())
    lag["period_end"] = str(lagged["date"].max().date())
    lag["signal"] = (
        "long BTC on day t when the h=1 prediction made on day t-1 is "
        "positive, else cash; no leverage, no shorting, no fees/slippage"
    )
    lag["hit_rate_long_days"] = float((lagged["signal_pred_return"] > 0).mean())

    result = {
        "naive_same_day_backtest": naive,
        "lagged_executable_backtest": lag,
        "headline_metrics": (
            "Use lagged_executable_backtest for any honest claim about "
            "predictive skill. The naive block is reported only to expose "
            "the same-day label alignment artefact in this sample."
        ),
    }
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

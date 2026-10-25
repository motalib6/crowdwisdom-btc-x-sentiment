"""Join sentiment + price into daily bars and build sentiment+price-only features.

Leakage rules (documented, enforced by construction):
- Features for day ``t`` use ONLY information dated <= ``t``.
- Price features use the previous day's close (``prev_close``) and
  returns computed from closes up to ``t-1`` -- never ``close_t``.
  The target for horizon ``h`` is ``close_{t+h}``. So h=0 predicts
  today's close from yesterday's price + today's aggregated sentiment.
  This is a nowcast at daily granularity: the sample has date-only
  timestamps, so intraday ordering of tweets vs. the close cannot be
  resolved, and that limitation is stated in the report.
- Sentiment features use the daily mean sentiment, rolling means,
  and post volume for days <= ``t`` only (pandas rolling/shift).

Features (sentiment + price ONLY -- no other external data):
  sentiment_mean, sentiment_mean_3d, sentiment_mean_7d,
  sentiment_change_1d, post_volume, pos_share, neg_share,
  prev_close, log_return_1d, log_return_3d, log_return_7d,
  volatility_7d (std of daily log returns), ma_ratio_7d, ma_ratio_30d

Output: data/joined_daily_bars.csv (one row per calendar day with
both a price bar and at least one tweet) and a SQLite database with
tables ``tweets``, ``price_bars`` and ``daily_bars``.
"""
import argparse
import sqlite3

import numpy as np
import pandas as pd

FEATURES = [
    "sentiment_mean", "sentiment_mean_3d", "sentiment_mean_7d",
    "sentiment_change_1d", "post_volume", "pos_share", "neg_share",
    "prev_close", "log_return_1d", "log_return_3d", "log_return_7d",
    "volatility_7d", "ma_ratio_7d", "ma_ratio_30d",
]
HORIZONS = [0, 1, 2, 3, 4, 5]


def build_daily_bars(tweets_csv: str, price_csv: str) -> pd.DataFrame:
    tw = pd.read_csv(tweets_csv, parse_dates=["date"])
    pr = pd.read_csv(price_csv, parse_dates=["date"])
    daily = (
        tw.groupby("date")
        .agg(
            sentiment_mean=("sentiment_score", "mean"),
            post_volume=("sentiment_score", "size"),
            pos_share=("sentiment_score", lambda s: (s > 0).mean()),
            neg_share=("sentiment_score", lambda s: (s < 0).mean()),
        )
        .reset_index()
    )
    df = pr.merge(daily, on="date", how="inner").sort_values("date").reset_index(drop=True)
    # Price features from closes up to t-1 only.
    df["prev_close"] = df["close"].shift(1)
    df["log_close"] = np.log(df["close"])
    df["log_return_1d"] = df["log_close"].shift(1) - df["log_close"].shift(2)
    df["log_return_3d"] = df["log_close"].shift(1) - df["log_close"].shift(4)
    df["log_return_7d"] = df["log_close"].shift(1) - df["log_close"].shift(8)
    df["volatility_7d"] = (
        df["log_close"].diff().shift(1).rolling(7).std()
    )
    df["ma_ratio_7d"] = df["prev_close"] / df["close"].shift(1).rolling(7).mean()
    df["ma_ratio_30d"] = df["prev_close"] / df["close"].shift(1).rolling(30).mean()
    # Sentiment features, days <= t only.
    df["sentiment_mean_3d"] = df["sentiment_mean"].rolling(3).mean()
    df["sentiment_mean_7d"] = df["sentiment_mean"].rolling(7).mean()
    df["sentiment_change_1d"] = df["sentiment_mean"] - df["sentiment_mean"].shift(1)
    for h in HORIZONS:
        df[f"target_close_h{h}"] = df["close"].shift(-h)
        df[f"target_return_h{h}"] = np.log(df[f"target_close_h{h}"]) - np.log(df["prev_close"])
    df = df.dropna(subset=FEATURES + [f"target_close_h{h}" for h in HORIZONS])
    return df.reset_index(drop=True)


def write_sqlite(df: pd.DataFrame, tweets_csv: str, price_csv: str, db_path: str) -> None:
    tw = pd.read_csv(tweets_csv)
    pr = pd.read_csv(price_csv)
    with sqlite3.connect(db_path) as con:
        tw.to_sql("tweets", con, if_exists="replace", index=False)
        pr.to_sql("price_bars", con, if_exists="replace", index=False)
        df.to_sql("daily_bars", con, if_exists="replace", index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tweets", default="data/raw/tweets.csv")
    ap.add_argument("--price", default="data/raw/btc_price_daily.csv")
    ap.add_argument("--out", default="data/joined_daily_bars.csv")
    ap.add_argument("--db", default="data/crowdwisdom.db")
    args = ap.parse_args()
    df = build_daily_bars(args.tweets, args.price)
    df.to_csv(args.out, index=False)
    write_sqlite(df, args.tweets, args.price, args.db)
    print(f"daily bars: {len(df)} rows, {df['date'].min()} to {df['date'].max()} -> {args.out}")
    print(f"features: {FEATURES}")
    print(f"sqlite: {args.db} (tweets, price_bars, daily_bars)")


if __name__ == "__main__":
    main()

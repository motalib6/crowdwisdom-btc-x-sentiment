"""Fetch BTC-USD daily price bars from the Coinbase Exchange public API.

No API key is required for this endpoint. The API returns candles as
[time, low, high, open, close, volume] (note: this order is Coinbase's,
it is NOT the usual OHLC order). This module re-orders them correctly.

Usage:
    python -m src.ingest_price --start 2015-01-01 --end 2019-12-31 \
        --out data/raw/btc_price_daily.csv

Coinbase caps a single candles request, so the range is fetched in
300-day chunks and concatenated. All timestamps are UTC, daily bars.
"""
import argparse
import time

import pandas as pd
import requests

API_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
HEADERS = {"User-Agent": "crowdwisdom-btc-pipeline/1.0"}


def fetch_chunk(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    params = {
        "granularity": 86400,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    rows = resp.json()
    # Coinbase candle order: [time, low, high, open, close, volume]
    df = pd.DataFrame(rows, columns=["ts", "low", "high", "open", "close", "volume"])
    df["date"] = pd.to_datetime(df["ts"], unit="s", utc=True).dt.date
    return df[["date", "open", "high", "low", "close", "volume"]]


def fetch_price(start: str, end: str) -> pd.DataFrame:
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    chunks, cur = [], start_ts
    while cur <= end_ts:
        nxt = min(cur + pd.Timedelta(days=300), end_ts)
        chunks.append(fetch_chunk(cur, nxt))
        cur = nxt + pd.Timedelta(days=1)
        time.sleep(0.2)  # be polite to a free public endpoint
    df = pd.concat(chunks, ignore_index=True)
    df = df.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--end", default="2019-12-31")
    ap.add_argument("--out", default="data/raw/btc_price_daily.csv")
    args = ap.parse_args()
    df = fetch_price(args.start, args.end)
    df.to_csv(args.out, index=False)
    print(f"price bars: {len(df)} rows, {df['date'].min()} to {df['date'].max()} -> {args.out}")


if __name__ == "__main__":
    main()

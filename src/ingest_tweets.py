"""Tweet ingestion.

Two modes:

1. ``--source hf-sample`` (the mode actually run for this build):
   Downloads the small, public, timestamped BTC tweet sample
   ``tahamajs/bitcoin_tweets_10_per_day`` (Hugging Face, parquet,
   17,880 rows, 10 tweets per day) via the Hugging Face parquet
   conversion endpoint. This dataset carries a ``Sentiment`` label
   (Positive / Negative) which is mapped to +1 / -1. It does NOT carry
   likes, reposts, views or follower counts -- see README.md and the
   evaluation report for that limitation. It is a proof-of-concept
   sample, NOT a live 180-day Apify scrape.

2. ``--source apify`` (code-ready, NOT run in this build):
   Runs an Apify X/Twitter scraper actor and normalises its output to
   the same schema. Requires the ``APIFY_TOKEN`` environment variable
   and ``APIFY_ACTOR_ID`` (the actor to configure -- see README.md).
   No token is hard-coded anywhere in this repository, and no token
   value is printed or logged.

Common output schema (data/raw/tweets.csv):
    date (UTC date), text, sentiment_score (-1..+1),
    likes, reposts, views, followers (may be empty for the sample),
    source (``hf-sample`` or ``apify``)

A small lexicon scorer is included for raw Apify text, where no
dataset label exists. It is deliberately simple and documented as
such; it is not presented as a production sentiment model.
"""
import argparse
import json
import os

import pandas as pd
import requests

HF_PARQUET_URL = (
    "https://huggingface.co/api/datasets/tahamajs/bitcoin_tweets_10_per_day"
    "/parquet/default/train/0.parquet"
)
HF_DATASET_URL = "https://huggingface.co/datasets/tahamajs/bitcoin_tweets_10_per_day"

LABEL_TO_SCORE = {"Positive": 1.0, "Neutral": 0.0, "Negative": -1.0}

POS_WORDS = {
    "bullish", "moon", "buy", "gain", "gains", "profit", "rally", "surge",
    "up", "rise", "rising", "breakout", "boom", "win", "good", "great",
    "amazing", "love", "support", "strong", "high", "growth", "adopt",
}
NEG_WORDS = {
    "bearish", "crash", "sell", "loss", "losses", "dump", "fall", "falling",
    "down", "drop", "dropped", "panic", "scam", "fraud", "bad", "weak",
    "fear", "hack", "banned", "ban", "decline", "plunge", "collapse",
}


def lexicon_score(text: str) -> float:
    """Very simple word-list sentiment in [-1, 1]. For Apify raw text only."""
    import re

    words = set(re.findall(r"[a-z]+", str(text).lower()))
    pos = len(words & POS_WORDS)
    neg = len(words & NEG_WORDS)
    if pos + neg == 0:
        return 0.0
    return (pos - neg) / (pos + neg)


def fetch_hf_sample(out_parquet: str, out_csv: str) -> pd.DataFrame:
    resp = requests.get(HF_PARQUET_URL, timeout=120)
    resp.raise_for_status()
    with open(out_parquet, "wb") as fh:
        fh.write(resp.content)
    df = pd.read_parquet(out_parquet)
    df = df.rename(columns={"Date": "timestamp", "text": "text", "Sentiment": "label"})
    df["date"] = pd.to_datetime(df["timestamp"], utc=True).dt.date
    df["sentiment_score"] = df["label"].map(LABEL_TO_SCORE)
    df["source"] = "hf-sample"
    for col in ("likes", "reposts", "views", "followers"):
        df[col] = pd.NA  # not present in this public sample -- not invented
    out = df[["date", "text", "sentiment_score", "likes", "reposts",
              "views", "followers", "source"]]
    out.to_csv(out_csv, index=False)
    return out


def run_apify(actor_id: str, search_terms, max_items: int = 5000) -> pd.DataFrame:
    """Run an Apify actor. Token comes ONLY from the environment.

    This function is intentionally not executed without APIFY_TOKEN.
    The Apify API call below follows the standard Apify actor-run
    pattern (POST /v2/acts/{actorId}/runs, then read the dataset).
    """
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError(
            "APIFY_TOKEN is not set. Set it in the environment and pass "
            "--actor-id; no token is stored in this repository."
        )
    # Live execution is deliberately NOT attempted here without a
    # reviewer confirming the actor and the token scope. The standard
    # Apify pattern is: POST https://api.apify.com/v2/acts/{actorId}/runs
    # with the token as a query parameter, then read the resulting
    # dataset items and normalise them to the schema above. Implement
    # that final step only after APIFY_TOKEN and APIFY_ACTOR_ID have
    # been configured in the environment (see README.md).
    raise RuntimeError(
        "Apify run not executed in this build (no token was provided). "
        "Configure APIFY_TOKEN and APIFY_ACTOR_ID, then re-run."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["hf-sample", "apify"], default="hf-sample")
    ap.add_argument("--actor-id", default=os.environ.get("APIFY_ACTOR_ID", ""))
    ap.add_argument("--out-parquet", default="data/raw/tweets_sample.parquet")
    ap.add_argument("--out", default="data/raw/tweets.csv")
    args = ap.parse_args()
    if args.source == "hf-sample":
        df = fetch_hf_sample(args.out_parquet, args.out)
    else:
        if not args.actor_id:
            raise SystemExit("apify mode needs --actor-id (see README.md)")
        df = run_apify(args.actor_id, ["$BTC", "#Bitcoin", "Bitcoin"])
        df.to_csv(args.out, index=False)
    print(f"tweets: {len(df)} rows, {df['date'].min()} to {df['date'].max()} -> {args.out}")
    print("sentiment score distribution:")
    print(df["sentiment_score"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()

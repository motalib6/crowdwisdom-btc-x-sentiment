"""Run the whole pipeline end-to-end, in order.

    python run_pipeline.py

Steps: ingest tweets (HF sample) -> ingest price (Coinbase) ->
features / joined bars + SQLite -> walk-forward training ->
backtest -> charts.

Requires: pandas, numpy, matplotlib, requests, pyarrow.
No API token is needed for the sample run. Apify / Tavily / Exa
steps are NOT run (see README.md); their code lives in
src/ingest_tweets.py (apify mode) and src/ingest_news.py.
"""
import subprocess
import sys


def run(*args: str) -> None:
    print(f"\n$ {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    run("-m", "src.ingest_tweets", "--source", "hf-sample")
    run("-m", "src.ingest_price", "--start", "2015-01-01", "--end", "2019-12-31")
    run("-m", "src.features")
    run("-m", "src.train_walkforward")
    run("-m", "src.backtest")
    run("-m", "src.charts")
    print("\nPipeline complete. See data/metrics.json, data/backtest.json, charts/.")


if __name__ == "__main__":
    main()

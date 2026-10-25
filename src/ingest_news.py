"""Recent-news ingestion stub (Tavily / Exa).

NOT run in this build: no Tavily or Exa API key was available, and no
key is hard-coded or printed here. When keys are available, set
``TAVILY_API_KEY`` and/or ``EXA_API_KEY`` in the environment and run:

    python -m src.ingest_news --query "Bitcoin" --out data/raw/news.csv

The functions below show the exact request shape that would be used,
so a reviewer can reproduce the news leg of the pipeline. News text
is used only as context for the 1-page sentiment outlook; the price
model itself uses sentiment + price features only, as specified.
"""
import argparse
import os

import requests

TAVILY_URL = "https://api.tavily.com/search"
EXA_URL = "https://api.exa.ai/search"


def search_tavily(query: str, max_results: int = 10):
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("TAVILY_API_KEY is not set; news fetch not run.")
    resp = requests.post(
        TAVILY_URL,
        json={"api_key": key, "query": query, "max_results": max_results,
              "search_depth": "basic"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def search_exa(query: str, max_results: int = 10):
    key = os.environ.get("EXA_API_KEY")
    if not key:
        raise RuntimeError("EXA_API_KEY is not set; news fetch not run.")
    resp = requests.post(
        EXA_URL,
        headers={"x-api-key": key, "Content-Type": "application/json"},
        json={"query": query, "numResults": max_results},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="Bitcoin")
    ap.add_argument("--out", default="data/raw/news.csv")
    args = ap.parse_args()
    raise SystemExit(
        "News ingestion was not run in this build (no Tavily/Exa key). "
        "Set TAVILY_API_KEY or EXA_API_KEY and re-run; see README.md."
    )


if __name__ == "__main__":
    main()

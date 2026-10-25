# CrowdWisdomTrading — X Sentiment Price Prediction Agent (Bitcoin, BTC)

Python ML pipeline that predicts the BTC price at horizons n+0 … n+5
using **only X sentiment + price features**, with walk-forward
validation. Built for the CrowdWisdomTrading Quantitative Data
Scientist intern assessment, by Sk Motalib (B.Tech CSE, AI & ML).

> **Read the honesty box first.** This build does NOT claim a live
> 180-day Apify scrape, and it contains NO Apify / Tavily / Exa
> tokens. See "What was actually run" below.

## What was actually run (this build, 2026-10-25)

| Item | Actually used |
|---|---|
| Asset | Bitcoin (BTC), BTC-USD |
| Tweets | Public sample `tahamajs/bitcoin_tweets_10_per_day` (Hugging Face): 17,880 tweets, 2015-01-01 to 2019-11-23, 10 tweets/day, with a Positive/Negative label mapped to +1/−1. 18 tweets had no label (score left blank, not invented). |
| Price | Coinbase Exchange public API, BTC-USD daily candles, no key. First available bar in that API is 2015-07-20, so price rows run 2015-07-20 to 2019-12-31 (1,626 bars). |
| Joined daily bars | 1,553 days, 2015-08-19 to 2019-11-18 (after the 30-day moving-average warm-up and the 5-day target shift). Stored in `data/joined_daily_bars.csv` and in SQLite `data/crowdwisdom.db` (tables: `tweets`, `price_bars`, `daily_bars`). |
| Model | Ridge regression (numpy closed-form, alpha = 1.0), one model per horizon, features standardised on the training window only. |
| Validation | Expanding-window walk-forward: 500-bar initial train, 5 folds × 180 test bars = 900 out-of-sample test rows per horizon, 2016-12-31 to 2019-06-18. |
| News leg | NOT run (no Tavily/Exa key). Code stub in `src/ingest_news.py`. The sentiment outlook is therefore tweet-sample only. |

## What was NOT run / NOT claimed

- **No live Apify scrape.** No Apify, Tavily or Exa token was
  available for this build, so no token is submitted, stored, or
  printed anywhere in this repository. Any submission email must say
  this plainly (see `evaluation_report.md`, "Tokens / actor IDs").
- **No last-180-days (2026) X data.** The sentiment outlook in the
  report is as of the last sample bar (2019-11-18), NOT a live 2026
  outlook. Re-running `src/ingest_tweets.py --source apify` with a
  token is what would produce a 2026 window.
- **No engagement / follower features in the sample.** The public
  sample has no likes, reposts, views or follower counts, so those
  columns are empty (not filled with invented values). The Apify
  schema in `src/ingest_tweets.py` includes them for the live run.
- **No GitHub repo created by this build.** Push instructions are
  below; fill in the real repo URL after pushing. Do not invent one.

## Data sources

- Tweet sample: <https://huggingface.co/datasets/tahamajs/bitcoin_tweets_10_per_day>
  (parquet via the Hugging Face parquet endpoint; licence as stated
  on that dataset page).
- Price: Coinbase Exchange public candles endpoint
  `https://api.exchange.coinbase.com/products/BTC-USD/candles`
  (granularity 86400, fetched in 300-day chunks).
- Assessment's historical-dataset list also pointed at
  `StephanAkkerman/crypto-stock-tweets`. That dataset was checked:
  its datasets-server view exposes only `text` + `url` (no
  timestamps, no engagement) and its full CSV is ~20 GB, so it could
  not honestly support daily sentiment bars here and was NOT used
  for the bars. It remains a valid source for the text corpus if a
  timestamped version is obtained.

## Apify / Tavily / Exa — to configure for a live run

These are **to be configured, not claimed as used**:

- Apify: set `APIFY_TOKEN` and `APIFY_ACTOR_ID` in the environment.
  Actor to configure (verify in the Apify Store at run time):
  the Apify Store **Twitter/X scraper actor** (commonly listed as
  `apify/twitter-scraper`; confirm the exact actor ID in the Store
  before running — this build does not assert an actor ID that was
  never run). Search terms: `$BTC`, `#Bitcoin`, `Bitcoin`
  (ticker, cashtag, keyword, as specified).
  Then: `python -m src.ingest_tweets --source apify --actor-id <ACTOR_ID>`
  (the live-run step is documented in code; it raises a clear error
  without a token rather than silently proceeding).
- Tavily (news): set `TAVILY_API_KEY`, see `src/ingest_news.py`
  (`https://api.tavily.com/search` — spelled "tavily" in the task doc).
- Exa (news/search): set `EXA_API_KEY`, see `src/ingest_news.py`.

Tokens must be passed via environment variables only, never pasted
into code, the report, or an email body as a live secret. If the
assessor requires reproducible tokens, supply them through a scoped /
revocable key and rotate it after submission — that is a submission
decision for the candidate, not something this build does silently.

## How to run

```bash
pip install -r requirements.txt
python run_pipeline.py
```

That runs, in order: tweet ingest (sample) → price ingest →
features / SQLite → walk-forward training → backtest → charts.

Individual steps (from the project root):

```bash
python -m src.ingest_tweets --source hf-sample
python -m src.ingest_price --start 2015-01-01 --end 2019-12-31
python -m src.features
python -m src.train_walkforward
python -m src.backtest
python -m src.charts
```

## Features (sentiment + price only)

`sentiment_mean`, `sentiment_mean_3d`, `sentiment_mean_7d`,
`sentiment_change_1d`, `post_volume`, `pos_share`, `neg_share`,
`prev_close`, `log_return_1d`, `log_return_3d`, `log_return_7d`,
`volatility_7d`, `ma_ratio_7d`, `ma_ratio_30d`.

Horizon indexing (important): a row dated `t` aggregates sentiment
for day `t` and sets `prev_close = close_{t-1}`; `target_close_h{h}`
is `close_{t+h}`. So from the last observed close the look-ahead is
h+1 days. The report states this explicitly wherever horizons are
quoted.

## Outputs

- `evaluation_report.md` — 1-page sentiment outlook + results +
  Sharpe / Sortino / Max Drawdown + limitations.
- `charts/` — sentiment vs price, forecast vs actual (h=1, h=5),
  lagged-strategy equity curve.
- `data/metrics.json`, `data/backtest.json`,
  `data/predictions_walkforward.csv` — the actual run's numbers.
- `BUILD_SUMMARY.md` — files, data, metrics, and every not-done item.

## Push to GitHub (not done by this build)

```bash
git init && git add . && git commit -m "BTC X-sentiment price prediction pipeline"
git remote add origin <YOUR-REPO-URL>
git push -u origin main
```

Then put the real repo URL in the submission email. Do not use a
placeholder URL as if it were live.

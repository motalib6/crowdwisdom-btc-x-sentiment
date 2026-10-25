# BUILD SUMMARY — CrowdWisdomTrading BTC X-sentiment pipeline

Built and run end-to-end on 2026-10-25. No email was sent, no GitHub
repo was created, and CrowdWisdomTrading was not contacted (per task
instructions). This file is the audit trail for the parent agent.

## Files created

```
crowdwisdom-btc/
├── README.md
├── BUILD_SUMMARY.md            (this file)
├── evaluation_report.md        (1-page sentiment outlook + results)
├── requirements.txt            (pandas, numpy, matplotlib, requests, pyarrow 14.x)
├── run_pipeline.py             (runs all steps in order)
├── src/
│   ├── __init__.py
│   ├── ingest_price.py         (Coinbase public API, no key)
│   ├── ingest_tweets.py        (hf-sample run; apify mode, env-token only, not run)
│   ├── ingest_news.py          (Tavily/Exa stub, not run, no key)
│   ├── features.py             (joined bars + sentiment/price-only features, SQLite)
│   ├── train_walkforward.py    (Ridge per horizon, expanding-window walk-forward)
│   ├── backtest.py             (naive + lagged backtests, Sharpe/Sortino/MaxDD)
│   └── charts.py               (matplotlib PNGs from actual outputs)
├── data/
│   ├── raw/tweets_sample.parquet
│   ├── raw/tweets.csv
│   ├── raw/btc_price_daily.csv
│   ├── joined_daily_bars.csv
│   ├── predictions_walkforward.csv
│   ├── metrics.json
│   ├── backtest.json
│   └── crowdwisdom.db          (tweets 17,880 / price_bars 1,626 / daily_bars 1,553)
└── charts/
    ├── sentiment_vs_price.png
    ├── forecast_vs_actual_h1.png
    ├── forecast_vs_actual_h5.png
    └── walkforward_cumulative.png   (lagged strategy only)
```

## Data actually used (verified counts)

- **Tweets:** Hugging Face `tahamajs/bitcoin_tweets_10_per_day`,
  17,880 rows, 2015-01-01 to 2019-11-23. Labels: Positive 9,831,
  Negative 8,021, Neutral 10, no label 18 (score left blank).
  Likes/reposts/views/followers: 0 present (not in the sample).
- **Price:** Coinbase Exchange public API, BTC-USD daily candles,
  1,626 rows, 2015-07-20 to 2019-12-31 (first available bar in that
  API is 2015-07-20; Binance was geographically blocked, so it was
  not used).
- **Joined daily bars:** 1,553 rows, 2015-08-19 to 2019-11-18.
  Post volume is constant at 10/day by dataset construction.
- **Walk-forward test set:** 900 rows per horizon,
  2016-12-31 to 2019-06-18 (500-bar initial train, 5 × 180-bar folds).

## Metrics actually computed (from data/metrics.json + data/backtest.json)

Per-horizon out-of-sample (RMSE / MAE in $, persistence in brackets):
- n+0: 280.90 / 151.45 (354.33 / 189.77) — beats persistence
- n+1: 490.65 / 264.12 (516.71 / 279.05) — beats persistence
- n+2: 652.42 / 348.68 (636.48 / 354.92) — worse on RMSE, tied on MAE
- n+3: 796.82 / 429.49 (736.60 / 418.57) — worse than persistence
- n+4: 938.12 / 511.36 (820.33 / 476.26) — worse than persistence
- n+5: 1,086.63 / 589.98 (917.81 / 531.05) — worse than persistence

Headline backtest — **lagged, executable** (899 days, 2017-01-01 to
2019-06-18): Sharpe **0.75**, Sortino **0.58**, Max Drawdown **−80.5%**,
total log-return 1.24. Buy-and-hold same period: Sharpe 1.07,
Sortino 1.04, Max Drawdown −83.8%, total log-return 2.23.
Strategy underperforms buy-and-hold: no tradable daily edge found.

Naive same-day backtest (REPORTED ONLY AS AN ARTEFACT, do not quote
as skill): Sharpe 11.06, Sortino 47.06, Max Drawdown −2.7%.
Cause: daily sentiment sign agrees with same-day return sign on
~94% of days; 99.9% of days have all 10 tweets sharing one label;
lagged sentiment correlation with next-day return is 0.016
(sign agreement 49.1%).

Sentiment outlook (sample end): last 90 days mean sentiment −0.178
(41.1% positive days), BTC −19.4%; last 180 days mean −0.011
(49.4% positive), BTC +3.6%; last day sentiment −1.0, 7-day −0.143.

## Every limitation / not-done item

1. No live 180-day Apify X scrape (no token/account available).
2. No Apify/Tavily/Exa token or actor ID submitted — none invented;
   env vars and the actor to configure are documented in README.md.
3. No Tavily/Exa news ingestion (no key).
4. No engagement/follower features (absent from the sample).
5. No GitHub repo created and no repo URL invented — push
   instructions are in README.md; the parent must push and fill in
   the real URL before any email submission.
6. No email sent to gilad@crowdwisdomtrading.com (explicitly out of
   scope for this build; parent to show a draft first).
7. No reinforcement-learning model — Ridge baseline only; RL is
   future work, not claimed.
8. Daily granularity only; intraday ordering unresolvable in sample.
9. Backtest excludes fees/slippage; real results would be worse.
10. 153 daily bars after 2019-06-18 are not covered by the 5
    walk-forward folds.
11. The assessment's `StephanAkkerman/crypto-stock-tweets` dataset
    was checked but not used for bars (datasets-server view has
    only text+url, no timestamps; full CSV ~20 GB).

## Verification performed

- `python run_pipeline.py` completed with exit code 0.
- Row counts, date ranges, label counts, SQLite table counts and
  chart files were re-checked from the output files after the run.
- The backtest was reworked after an initial inflated result was
  traced to (a) a 2-day horizon-return definition and (b) the
  same-day label alignment; the corrected lagged backtest above is
  the headline result.

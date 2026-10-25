# Evaluation Report — X Sentiment Price Prediction Agent (Bitcoin, BTC)

**Candidate:** Sk Motalib — B.Tech CSE (AI & ML)
**Asset:** Bitcoin (BTC), BTC-USD
**Model:** Ridge regression, one model per horizon n+0 … n+5, sentiment + price features only
**Build date:** 2026-10-25
**Data actually used:** public tweet sample 2015-01-01 – 2019-11-23 and Coinbase BTC-USD daily bars 2015-07-20 – 2019-12-31; joined daily bars 2015-08-19 – 2019-11-18 (1,553 days). This is a historical proof-of-concept, NOT a live 180-day Apify scrape and NOT a live 2026 outlook. See "Limitations" and "Tokens / actor IDs".

---

## 1. One-page sentiment outlook for BTC (as of the last sample bar, 2019-11-18)

**Headline: cautious-to-negative at the end of the sample, after a sharp 90-day fall — but this is a sample-end outlook, not a 2026 call.**

- **Last 90 sample days (2019-08-21 to 2019-11-18):** mean daily sentiment **−0.178**; only **41.1%** of days were positive, **58.9%** negative. BTC fell **−19.4%** over the same window ($10,130.00 → $8,168.84).
- **Last 180 sample days (2019-05-23 to 2019-11-18):** mean sentiment **−0.011**, essentially balanced (49.4% positive / 50.6% negative); BTC rose **+3.6%** ($7,881.98 → $8,168.84). The negative tilt is therefore a recent-90-day phenomenon, not a full-180-day one.
- **Most recent readings:** last daily sentiment **−1.0** (all sampled tweets that day negative) and 7-day mean sentiment **−0.143**, both below the full-sample mean sentiment of **+0.121** (56.0% of all sample days positive).
- **What this does and does not say:** within this sample, same-day sentiment tracks same-day price direction very closely (see the artefact box below), so a negative latest reading coinciding with a falling price is consistent with the sample pattern — it is NOT independent evidence that the next days must fall. The lagged test in Section 4 finds essentially no predictive signal from yesterday's sentiment for tomorrow's return (correlation 0.016, sign agreement 49.1% — a coin flip). A trader reading only this outlook should therefore treat it as *current mood, not a forecast*.
- **What would change the outlook:** a run of positive 7-day sentiment above 0 together with price holding above its 30-day average, or fresh 2026 X data from a live Apify run. No Tavily/Exa news leg was available for this build, so news sentiment is not included in this outlook.
- **Bottom line for the sample end:** sentiment had turned negative and price had fallen hard in the last 90 days; the model outlook is defensive, and the honest predictive evidence does not support a strong directional bet from sentiment alone.

---

## 2. Method

**Ingestion.** Tweets: Hugging Face sample `tahamajs/bitcoin_tweets_10_per_day` (17,880 tweets; label → +1/−1; 18 tweets had no label and were left blank). Price: Coinbase Exchange public API, BTC-USD daily candles (open/high/low/close/volume, UTC). Joined on calendar date into SQLite (`data/crowdwisdom.db`: `tweets`, `price_bars`, `daily_bars`) and `data/joined_daily_bars.csv`.

**Features — sentiment + price only.** Daily sentiment mean, 3-day and 7-day sentiment means, 1-day sentiment change, post volume, positive/negative share; previous close, 1/3/7-day log returns, 7-day volatility, price vs 7-day and 30-day moving averages. No news, on-chain, macro or other external features enter the model.

**Horizon definition.** A row dated `t` uses sentiment for day `t` and `prev_close = close_{t-1}`; the target for horizon `h` is `close_{t+h}`. From the last observed close, the look-ahead is therefore h+1 days. All horizon labels in this report use the task's n+0 … n+5 with n = the sentiment day `t`.

**Model.** Ridge regression (numpy closed-form, alpha = 1.0), trained separately per horizon on log-return to the target, converted back to price as `prev_close × exp(predicted log-return)`. Features are standardised using training-window statistics only.

**Walk-forward validation (strictly out-of-sample in time).** Initial training window 500 bars, then 5 expanding-window folds of 180 test bars each: 900 test rows per horizon, test period 2016-12-31 to 2019-06-18. No future bar is ever in a training window. The 153 bars after 2019-06-18 are not covered by these 5 folds (a stated design limit, not hidden data).

**Backtest.** Long/flat only (long BTC when the signal is positive, else cash), no leverage, no shorting, no fees/slippage modelled. Risk-free rate assumed 0. Formulas: Sharpe = mean(daily log-return) / std(daily log-return) × √365; Sortino = mean / downside-deviation × √365 (downside deviation from negative returns only); Max Drawdown = worst peak-to-trough fall of exp(cumulative log-return).

---

## 3. Model results per horizon (out-of-sample, 900 test rows each)

| Horizon | Model RMSE ($) | Model MAE ($) | Persistence RMSE ($) | Persistence MAE ($) | Mean actual close ($) |
|---|---:|---:|---:|---:|---:|
| n+0 | 280.90 | 151.45 | 354.33 | 189.77 | 5,639.00 |
| n+1 | 490.65 | 264.12 | 516.71 | 279.05 | 5,648.23 |
| n+2 | 652.42 | 348.68 | 636.48 | 354.92 | 5,657.71 |
| n+3 | 796.82 | 429.49 | 736.60 | 418.57 | 5,667.96 |
| n+4 | 938.12 | 511.36 | 820.33 | 476.26 | 5,678.68 |
| n+5 | 1,086.63 | 589.98 | 917.81 | 531.05 | 5,689.46 |

Persistence = predicting `prev_close` (no change). **Reading:** the sentiment+price Ridge beats persistence at n+0 and n+1, is roughly tied at n+2 on MAE but worse on RMSE, and loses to persistence at n+3, n+4 and n+5. In other words, any signal in this sample decays within about two days, and longer-horizon price forecasts should not be trusted over the naive baseline. Errors naturally grow with horizon as price levels rise and the look-ahead lengthens; they are reported in dollars against a mean close of ~$5,640, so n+5 RMSE is ~19% of the mean price.

![Sentiment vs price](charts/sentiment_vs_price.png)

![Forecast vs actual, n+1](charts/forecast_vs_actual_h1.png)

![Forecast vs actual, n+5](charts/forecast_vs_actual_h5.png)

---

## 4. Backtest — headline metrics (lagged, executable signal)

**Signal:** at the end of day t−1, take the model's n+1 prediction made on day t−1; if positive, hold BTC during day t, else hold cash. Realised return is the clean 1-day return log(close_t / close_{t−1}). This uses no same-day sentiment and is the only backtest in this report that should be quoted as a predictive result.

| | Sharpe Ratio | Sortino Ratio | Max Drawdown | Total log-return | Period |
|---|---:|---:|---:|---:|---|
| Lagged sentiment-signal strategy | **0.75** | **0.58** | **−80.5%** | 1.24 | 2017-01-01 – 2019-06-18 (899 days, long on 60.5% of days) |
| Buy-and-hold BTC, same period | 1.07 | 1.04 | −83.8% | 2.23 | same |

**Reading:** the lagged strategy underperforms buy-and-hold on Sharpe, Sortino and total return, with a similarly severe maximum drawdown. There is no evidence here of a tradable daily edge from this sentiment model. That is a real, reportable finding — it is not hidden behind the naive numbers below.

![Lagged equity curve](charts/walkforward_cumulative.png)

### Artefact box — why the naive same-day numbers must NOT be quoted

A same-day backtest (signal from the same row's n+0 prediction, realised same-day return) gives Sharpe **11.06**, Sortino **47.06**, Max Drawdown **−2.7%**, total log-return 14.59 over the same 900 test rows. Those numbers are **not credible as trading performance** and are reported only to expose the problem:

- In this sample, **99.9% of days have all 10 sampled tweets sharing a single sentiment label**, and the daily sentiment sign agrees with the same day's price-return sign on **~94% of days** (correlation 0.65).
- Lagged sentiment, by contrast, correlates **0.016** with next-day return, with **49.1%** sign agreement — a coin flip.
- The pattern is consistent with labels/sampling that are aligned to same-day price direction. Treating the naive Sharpe as skill would be misleading, and any reviewer should discount it accordingly.

---

## 5. Limitations (complete list)

1. **No live Apify scrape** — last-180-days 2026 X data was not collected; the sample ends in 2019. The pipeline code is Apify-ready, but the live leg needs a token (see below).
2. **No Tavily/Exa news leg** — no news sentiment in features or outlook.
3. **No engagement features in the sample** — likes, reposts, views, follower counts are absent from the public sample and were left empty, not estimated.
4. **Post volume is constant** — the sample is exactly 10 tweets/day, so `post_volume` carries no signal in this run (mean 10.0, std 0.0). A live Apify run would restore real volume variation.
5. **Daily granularity only** — the sample has date-only timestamps, so intraday tweet-vs-close ordering cannot be resolved; the n+0 nowcast uses same-day aggregated sentiment (see artefact box).
6. **Sentiment labels are dataset-provided**, not recomputed by a production classifier; a lexicon scorer is included in code only for raw Apify text.
7. **Price source starts 2015-07-20** in the Coinbase API, so January–July 2015 tweets have no matching price bar and are excluded from joined bars.
8. **No fees, slippage, liquidity or shorting costs** in the backtest; real trading results would be worse.
9. **Model is a Ridge baseline only** — no reinforcement-learning agent was trained; RL is listed as future work, not claimed.
10. **Walk-forward covers 5 folds only** — 153 bars after 2019-06-18 are unused as test data in this design.

## 6. Tokens / actor IDs

**None available, none submitted, none invented.** No Apify, Tavily or Exa token was available for this build (the candidate has no Apify/Tavily account for this task), so this report deliberately does not list a token value or an actor ID as "used". To reproduce the live leg, configure in the environment: `APIFY_TOKEN`, `APIFY_ACTOR_ID` (Apify Store Twitter/X scraper actor — verify the exact actor ID in the Apify Store before running; commonly listed as `apify/twitter-scraper`), `TAVILY_API_KEY`, `EXA_API_KEY`. Code paths: `src/ingest_tweets.py` (`--source apify`) and `src/ingest_news.py`. Any token supplied for a future submission should be scoped/revocable and rotated afterwards.

## 7. Reproduction

```bash
pip install -r requirements.txt
python run_pipeline.py
# Outputs: data/metrics.json, data/backtest.json,
#          data/predictions_walkforward.csv, charts/*.png
```

All metrics in this report come from those output files of the actual run, not from placeholders. The GitHub repository link is to be added after the code is pushed (no repo was created by this build, and no URL is invented here).

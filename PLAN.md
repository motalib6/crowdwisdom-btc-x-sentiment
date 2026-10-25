# CrowdWisdomTrading BTC X Sentiment Price Prediction — Plan (5–7 day full version)

Asset: Bitcoin (BTC)
User confirmed 2026-10-25: no Apify / Tavily account. No tokens to be invented.
Email target: gilad@crowdwisdomtrading.com — draft to be shown to user before sending.

## Deadline confirmed by user 2026-10-25
- Hard deadline: **30 October 2026** — all work completed by 30 Oct.
- Status 25 Oct: Days 1–5 already built and run (pipeline, features, walk-forward, charts, backtest, evaluation report). Remaining: GitHub repo push (blocked until user creates the empty repo — Muse GitHub App cannot create a repo, 403 on 25 Oct, twice) + email draft approval + final email submission. All remaining steps to be completed on or before 30 Oct 2026.

## Daily execution plan
- Day 1 (25 Oct): Data + pipeline skeleton. BTC public price data, public tweet sentiment sample, joined sentiment+price bars in SQLite/CSV, schema documented.
- Day 2: Feature engineering (sentiment score, post volume, lagged returns, rolling sentiment) + walk-forward training for horizons n+0 to n+5.
- Day 3: Charts (sentiment vs price over time, forecast vs actual) + 1-page BTC sentiment outlook.
- Day 4: Backtest + evaluation report (Sharpe, Sortino, Max Drawdown, RMSE/MAE per horizon) + limitations, including the live Apify/Tavily token gap stated honestly.
- Day 5: Review, README, reproduction steps, GitHub-ready repo package.
- Day 6–7: Buffer, final checks, email draft shown to user, then submit only after user approves the draft.

## Rules
- Features: sentiment + price only.
- No invented tokens, actor IDs, tweet text, engagement counts, or metrics. Every metric must come from an actual run.
- Apify code must be env-var based (APIFY_TOKEN etc.) with the public actor to configure documented, not claimed as run.
- Do not send email without showing the draft first.

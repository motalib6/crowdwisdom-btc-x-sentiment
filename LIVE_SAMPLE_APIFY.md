# Live Apify X sample — 2026-10-25

This is a live demonstration of the Apify leg only. It is NOT a
180-day series and it is NOT merged into the historical walk-forward
backtest (2015-2019 sample), so it does not change the reported
Sharpe, Sortino, or Max Drawdown figures.

- Actor: xquik/x-tweet-scraper, id wAusCMrm284Voaw86
  (README suggestion apify/twitter-scraper returned 404).
- Run id: hV7bSKANELToovkBz, dataset id: rUIZtbffzuVztTDJM
- Status: SUCCEEDED, run time 3.6 seconds, 2026-10-25 14:43 UTC.
- Input: searchTerms ["Bitcoin lang:en -filter:retweets"],
  maxItems 50, queryType Latest, outputVariant rich,
  fieldStyle camelCase, outputPreset flat.
- Raw output: data/raw/tweets_apify_sample.json
- Normalised output: data/raw/tweets_apify_sample.csv
  (createdAt, authorUsername, text, lexicon sentiment, likeCount,
  retweetCount, replyCount, viewCount, authorFollowers, url).

## Actual cost — correction to the pre-run estimate

- Pre-run estimate was about $0.75, based on a FREE-tier pricing
  record showing $0.015 per tweet.
- Actual run charges from the Apify run object: 50 dataset items at
  $0.00015 each = $0.0075, plus platform usage $0.0079, total about
  $0.0154. The estimate was therefore too high; the verified total
  is about $0.015, not $0.75.

## What the sample actually is

- 50 latest tweets, all within about 3 minutes:
  2026-10-25 14:39:37 to 14:42:42 UTC (20:09-20:12 IST).
- This is a snapshot, not a daily sentiment series. Do not quote it
  as a full-day or 180-day sentiment outlook.
- Lexicon sentiment (same simple word list as src/ingest_tweets.py):
  mean 0.05, positive 9, negative 6, neutral 35 out of 50.
  The lexicon is sparse, so most tweets score neutral.
- Engagement in this snapshot is low: mean likes 0.48, mean
  retweets 0.06, mean views 60.38, mean author followers 9,007.
- Unlike the 2015-2019 public sample, this live sample DOES carry
  real likes, retweets, views, and follower counts.

Still pending: evaluation report and repo update with this sample
plus the Tavily sample, then a re-shown email draft before sending.
Deadline: 30 Oct 2026.

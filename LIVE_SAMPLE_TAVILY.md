# Live Tavily news sample — 2026-10-25

This is a live demonstration of the news leg only. It is NOT merged into
the historical walk-forward backtest (2015-2019 sample), so it does not
change the reported Sharpe, Sortino, or Max Drawdown figures.

- Source: Tavily search, topic news, time range week, basic depth,
  max_results 5, query "Bitcoin price news".
- Cost reported by the API: 1 credit.
- Raw output: data/raw/news_tavily_sample.json
- Results, 21-25 Oct 2026:
  - 24 Oct 2026: BTC falls below $80,000 on renewed Middle East worries.
  - 25 Oct 2026: BTC recovers to $80,800 ahead of Fed meeting.
  - 21 Oct 2026: OCC finalizes GENIUS Act stablecoin rules.
  - 24 Oct 2026: Bitcoin price on its 18th birthday, history outlook.
  - 23 Oct 2026: BTC recovers to $81,700 as memecoins lead a rebound.
- Current live picture in this small sample: BTC was volatile around
  $80,000-$81,700 in the past week, with a dip below $80,000 followed
  by a recovery. This is a 5-item sample, not a full sentiment series.

Still pending at this point: a small live Apify X sample (actor ID and
pricing must be confirmed first, to protect the $5 free credits), then
a report and repo update, then a re-shown email draft before sending.
Deadline: 30 Oct 2026.

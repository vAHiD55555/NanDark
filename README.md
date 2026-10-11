# BlackBird Core v0.4 — Study Mode

## Overview
- **4 assets**: BTC, Gold/USD, Gold/EUR, Silver/USD
- **2 observers**: Conservative + Aggressive (different assumptions)
- **Real data only**: CoinGecko (crypto), MetalPriceAPI (commodities)
- **No synthetic data**: If API fails → quality=FAIL → NO trade/prediction
- **Purpose**: 6-month study to discover which patterns are predictive

## Architecture
```
main.py              # Entry point, loop control
core/
  config.py          # Asset definitions, thresholds
  data.py            # Live price fetchers (real APIs only)
  analysis.py        # Technical indicators (RSI, SMA, volatility)
  risk.py            # Independent veto power
  paper_trader.py    # Virtual positions & PnL tracking
  logger.py          # JSONL log writer
  study.py           # Runs both observers, compares results
  observers/
    conservative.py  # High risk aversion, multiple confirmations
    aggressive.py    # Momentum-driven, breakout focused
```

## Run Commands

### Single cycle (test):
```bash
python3 main.py --once --mode both
```

### 24-hour continuous study:
```bash
python3 main.py --hours 24 --interval 900 --mode study
```
Interval: 900s = 15min (respects CoinGecko rate limits)

### 24-hour paper trading:
```bash
python3 main.py --hours 24 --interval 900 --mode paper
```

### Both study + paper:
```bash
python3 main.py --hours 24 --interval 900 --mode both
```

## Data Sources (Free, No Key)
- **Crypto**: CoinGecko API (bitcoin)
- **Commodities**: MetalPriceAPI (gold, silver)
- Caching: 60s for prices, 300s for history
- Rate limit handling: 429 responses cached to avoid hammering

## Safety Rules
1. `quality=FAIL` → `NO_TRADE` (no data = no action)
2. `quality=WARN` → `WAIT` (synthetic/fixture data is forbidden)
3. `quality=PASS` → only then can a trade be considered
4. Confidence < 0.55 → `NO_TRADE`
5. Max 2 open positions
6. Max 20% drawdown

## Real Trade Path
Paper trading → 6-month study → verify patterns → explicit user approval → real trade.
Real trades NEVER happen automatically.

## Outputs
- `logs/YYYY-MM-DD.jsonl` — every cycle, decision, outcome
- `data/{ASSET}.jsonl` — price snapshots
- Console: compact cycle summary

## Requirements
- Python 3.7+
- No external dependencies (stdlib only)
- Internet connection for live APIs
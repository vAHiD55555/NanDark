# 2026-10-11 — BlackBird Study System

## Context
- Need to study 4 assets: BTC, Gold/USD, Gold/EUR, Silver/USD
- 24/7 monitoring on lightweight server
- 6-month observation period before any real trading
- Two observers with different assumptions: Conservative vs Aggressive

## Proposal
- Real data only (CoinGecko + MetalPriceAPI)
- No synthetic fallback — quality=FAIL → NO_TRADE
- Paper trading engine with virtual balance
- Daily logging to JSONL files
- Comparative study: which observer patterns are predictive?

## Open Questions
- How to handle commodity history (not available on free tier)?
- What confidence threshold for each observer?
- How to measure "predictive" over 6 months?

## Status
Implemented in `/workspace/app/main.py` and `core/`
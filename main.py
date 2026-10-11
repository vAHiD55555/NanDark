#!/usr/bin/env python3
"""BlackBird Core v0.4 — REAL DATA ONLY, Study + Paper Trading"""

import json
import time
import argparse
from datetime import datetime, timezone

from core.config import ASSETS, LOOP_INTERVAL_SECONDS, VERSION
from core.data import get_price, get_history, save_snapshot
from core.risk import evaluate
from core.paper_trader import PaperTrader
from core.logger import write_log
from core.study import run_study_cycle
from core.analysis import analyze


def build_signal(asset: str) -> dict:
    """Build a signal dict for a single asset. Used by server.py."""
    pd = get_price(asset)
    history = get_history(asset)
    analysis = analyze(asset, history, pd["price"]) if (history and pd["quality"] == "PASS" and pd["price"]) else None
    return {
        "asset": asset,
        "timeframe": "1h",
        "timestamp": pd["timestamp"],
        "direction": analysis["direction"] if analysis else "HOLD",
        "confidence": analysis["confidence"] if analysis else 0.0,
        "agreement": 0,
        "conflict": "no council configured in v0.4",
        "data_quality": pd["quality"],
        "source": pd["source"],
        "reason_codes": analysis["reason_codes"] if analysis else [],
        "version": VERSION,
        "price": pd["price"],
    }


def risk_guardian(signal: dict) -> tuple:
    """Return (decision, reason). Hard veto: cannot be overridden."""
    if signal["data_quality"] == "FAIL":
        return "NO_TRADE", "data_quality=FAIL — insufficient data"
    if signal["data_quality"] == "WARN":
        return "WAIT", "data_quality=WARN — synthetic data is not allowed"
    if signal["confidence"] < 0.55:
        return "NO_TRADE", f"confidence={signal['confidence']} below 0.55 threshold"
    return "PAPER_LONG", "risk check passed"


def run_paper_cycle(trader):
    prices = {}
    decisions = []
    for key in ASSETS:
        pd = get_price(key)
        prices[key] = pd
        save_snapshot(pd)
        history = get_history(key)
        analysis = analyze(key, history, pd["price"]) if (history and pd["quality"] == "PASS" and pd["price"]) else None
        open_count = len(trader.positions)
        signal = {
            "quality": pd["quality"],
            "confidence": analysis["confidence"] if analysis else 0.0,
            "direction": analysis["direction"] if analysis else "HOLD",
        }
        verdict, reason = evaluate(signal, open_count, trader.balance, trader.peak_balance, paper_mode=True)
        if verdict in ("PAPER_LONG", "PAPER_SHORT") and key not in trader.positions and pd["price"]:
            qty = trader.balance * 0.5 / pd["price"]
            trader.open_position(key, "LONG" if verdict == "PAPER_LONG" else "SHORT", pd["price"], qty, pd["timestamp"])
            decisions.append({"asset": key, "decision": verdict, "reason": reason, "price": pd["price"]})
        elif key in trader.positions and pd["price"]:
            outcome = trader.close_position(key, pd["price"], pd["timestamp"])
            decisions.append({"asset": key, "decision": "CLOSE", "reason": reason, "price": pd["price"], "outcome": outcome})
        else:
            decisions.append({"asset": key, "decision": verdict, "reason": reason, "price": pd["price"]})
    return {
        "system": "BlackBird Core", "version": VERSION, "mode": "PAPER_TRADING",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prices": {k: {"price": v["price"], "source": v["source"], "quality": v["quality"]} for k, v in prices.items()},
        "balance": trader.balance, "open_pnl": trader.get_open_pnl(prices),
        "open_positions": list(trader.positions.keys()), "decisions": decisions,
    }


def main():
    parser = argparse.ArgumentParser(description="BlackBird Core v0.4")
    parser.add_argument("--hours", type=float, default=24.0)
    parser.add_argument("--interval", type=int, default=LOOP_INTERVAL_SECONDS)
    parser.add_argument("--mode", choices=["study", "paper", "both"], default="study")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    trader = PaperTrader()
    start = time.time()
    end = start + args.hours * 3600

    print(f"[BlackBird v{VERSION}] Mode: {args.mode}")
    print(f"[BlackBird] Assets: {list(ASSETS.keys())}")
    print(f"[BlackBird] REAL DATA ONLY — no synthetic fallback")
    print("-" * 60)

    if args.once:
        if args.mode in ("study", "both"):
            prices = {k: get_price(k) for k in ASSETS}
            histories = {k: get_history(k) for k in ASSETS}
            entry = run_study_cycle(prices, histories)
            print(json.dumps(entry, indent=2, ensure_ascii=False))
        if args.mode in ("paper", "both"):
            output = run_paper_cycle(trader)
            print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    cycle = 0
    while time.time() < end:
        cycle += 1
        if args.mode in ("study", "both"):
            prices = {k: get_price(k) for k in ASSETS}
            histories = {k: get_history(k) for k in ASSETS}
            entry = run_study_cycle(prices, histories)
            s = entry["summary"]
            print(f"[study {cycle} {entry['generated_at'][11:19]}] "
                  f"analyzed={s['analyzed']} agreements={s['agreements']} "
                  f"conflicts={s['conflicts']}")
        if args.mode in ("paper", "both"):
            output = run_paper_cycle(trader)
            prices_str = " | ".join(
                f"{k}={v['price'] if v['price'] else 'N/A'}({v['quality']})" for k, v in output["prices"].items()
            )
            print(f"[paper {cycle} {output['generated_at'][11:19]}] {prices_str}")
            for d in output["decisions"]:
                icon = {"PAPER_LONG": "+", "PAPER_SHORT": "~", "CLOSE": "X", "WAIT": ".", "NO_TRADE": "!"}.get(d["decision"], "?")
                extra = f" PnL={d['outcome']['pnl']:+.2f}" if d.get("outcome") else ""
                print(f"  {icon} {d['asset']}: {d['decision']}{extra}")
            print(f"  Balance: ${trader.balance:,.2f} | Open: {len(trader.positions)} | Trades: {len(trader.trades)}")
        print("-" * 60)
        remaining = end - time.time()
        if remaining <= 0:
            break
        time.sleep(min(args.interval, remaining))

    if args.mode in ("paper", "both"):
        summary = trader.summary()
        final = {"system": "BlackBird Core", "version": VERSION, "mode": "COMPLETE",
                 "generated_at": datetime.now(timezone.utc).isoformat(),
                 "duration_hours": args.hours, "summary": summary, "trades": trader.trades}
        print(json.dumps(final, indent=2, ensure_ascii=False))
        write_log(final)


if __name__ == "__main__":
    main()
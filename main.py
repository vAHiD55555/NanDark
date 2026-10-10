#!/usr/bin/env python3
"""
BlackBird Core v0.2 — Observer Only
===================================
Observes and reports. Produces no trades. Safe default: WAIT.
Run: python3 main.py
"""

import json
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Configuration (no secrets, no external dependencies)
# ---------------------------------------------------------------------------
ASSETS = ["BTC", "ETH"]
TIMEFRAME = "1h"
VERSION = "0.2.0"


# ---------------------------------------------------------------------------
# Data layer — returns (data, quality, source, fetched_at)
# ---------------------------------------------------------------------------
def fetch_sample_data(asset: str) -> tuple:
    """Return a synthetic observation with explicit quality flag.

    This is a fixture, NOT real market data. It exists so the core can run
    offline. Real data replaces this function.
    """
    return (
        {"asset": asset, "price": None, "currency": "USD"},
        "WARN",          # data_quality: PASS / WARN / FAIL
        "fixture",       # source name
        datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Risk Guardian — independent veto power
# ---------------------------------------------------------------------------
def risk_guardian(signal: dict) -> tuple:
    """Return (decision, reason). Hard veto: cannot be overridden."""
    if signal["data_quality"] == "FAIL":
        return "NO_TRADE", "data_quality=FAIL — insufficient data"
    if signal["data_quality"] == "WARN":
        return "WAIT", "data_quality=WARN — data is synthetic, not real"
    if signal["confidence"] < 0.55:
        return "NO_TRADE", f"confidence={signal['confidence']} below 0.55 threshold"
    return "PAPER_LONG", "risk check passed"


# ---------------------------------------------------------------------------
# Signal Matrix — minimal council output
# ---------------------------------------------------------------------------
def build_signal(asset: str) -> dict:
    data, quality, source, fetched_at = fetch_sample_data(asset)
    return {
        "asset": asset,
        "timeframe": TIMEFRAME,
        "timestamp": fetched_at,
        "direction": "HOLD",
        "confidence": 0.0,
        "agreement": 0,
        "conflict": "no council configured in v0.2",
        "data_quality": quality,
        "source": source,
        "reason_codes": ["OBSERVE_ONLY"],
        "version": VERSION,
    }


# ---------------------------------------------------------------------------
# Commander — final decision
# ---------------------------------------------------------------------------
def main() -> None:
    signals = [build_signal(a) for a in ASSETS]
    decisions = []
    for sig in signals:
        verdict, reason = risk_guardian(sig)
        decisions.append({
            "asset": sig["asset"],
            "decision": verdict,
            "reason": reason,
            "market": {
                "asset": sig["asset"],
                "price": sig.get("price"),
                "source": sig["source"],
                "fetched_at": sig["timestamp"],
            },
            "risk": {
                "status": "PASS" if verdict != "NO_TRADE" else "VETO",
                "note": reason,
            },
            "version": VERSION,
        })

    output = {
        "system": "BlackBird Core",
        "version": VERSION,
        "mode": "OBSERVE_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
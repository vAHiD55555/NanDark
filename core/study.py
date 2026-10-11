"""Study engine — runs both observers and logs comparative results.

Purpose: after ~6 months of study, compare Conservative vs Aggressive
approaches to discover which patterns are actually predictive.
"""

from typing import List, Dict
from datetime import datetime, timezone

try:
    from core.observers.conservative import analyze as conservative_analyze
    from core.observers.aggressive import analyze as aggressive_analyze
    from core.config import ASSETS
    from core.logger import write_log
except ImportError:
    from observers.conservative import analyze as conservative_analyze
    from observers.aggressive import analyze as aggressive_analyze
    from config import ASSETS
    from logger import write_log


def run_study_cycle(prices: Dict[str, dict],
                    histories: Dict[str, List[dict]]) -> dict:
    """Run both observers on current data. Returns comparative study entry."""
    results = {}

    for key in ASSETS:
        pd = prices[key]
        history = histories.get(key)
        price = pd["price"]

        # If no live data, skip analysis — no fabrication
        if price is None or pd["quality"] != "PASS":
            results[key] = {
                "price": None,
                "quality": pd["quality"],
                "source": pd["source"],
                "error": "no_live_data",
                "conservative": None,
                "aggressive": None,
            }
            continue

        # If no history, skip — cannot analyze without history
        if not history or len(history) < 10:
            results[key] = {
                "price": price,
                "quality": pd["quality"],
                "source": pd["source"],
                "error": "insufficient_history",
                "conservative": None,
                "aggressive": None,
            }
            continue

        cons = conservative_analyze(key, history, price)
        aggr = aggressive_analyze(key, history, price)

        results[key] = {
            "price": price,
            "quality": pd["quality"],
            "source": pd["source"],
            "conservative": {
                "confidence": cons["confidence"],
                "direction": cons["direction"],
                "reason_codes": cons["reason_codes"],
                "trend": cons["trend"],
                "rsi": cons["rsi"],
                "volatility": cons["volatility"],
            },
            "aggressive": {
                "confidence": aggr["confidence"],
                "direction": aggr["direction"],
                "reason_codes": aggr["reason_codes"],
                "trend": aggr["trend"],
                "rsi": aggr["rsi"],
                "volatility": aggr["volatility"],
                "momentum": aggr.get("momentum"),
            },
            "agreement": cons["direction"] == aggr["direction"],
            "conflict": (
                cons["direction"] != aggr["direction"]
                and cons["direction"] != "HOLD"
                and aggr["direction"] != "HOLD"
            ),
        }

    entry = {
        "system": "BlackBird Study",
        "version": "0.4.0",
        "mode": "STUDY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "summary": {
            "assets": len(results),
            "analyzed": sum(1 for r in results.values() if r.get("conservative")),
            "agreements": sum(1 for r in results.values() if r.get("agreement")),
            "conflicts": sum(1 for r in results.values() if r.get("conflict")),
            "conservative_signals": sum(1 for r in results.values() if r.get("conservative") and r["conservative"]["direction"] != "HOLD"),
            "aggressive_signals": sum(1 for r in results.values() if r.get("aggressive") and r["aggressive"]["direction"] != "HOLD"),
        },
    }
    write_log(entry)
    return entry
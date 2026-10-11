"""Observer B — Aggressive Study.

Preset assumption: markets trend strongly; momentum is the dominant
signal. Reacts quickly to breakouts. Higher risk tolerance.
Purpose: study whether aggressive rules capture more gains (or more losses).
"""

from typing import List, Optional
from datetime import datetime, timezone
import math


def _sma(prices: List[float], period: int) -> Optional[float]:
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def _rsi(prices: List[float], period: int = 14) -> Optional[float]:
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(len(prices) - period, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))


def _volatility(prices: List[float], period: int = 24) -> Optional[float]:
    if len(prices) < period + 1:
        return None
    returns = []
    for i in range(len(prices) - period, len(prices)):
        if prices[i - 1] != 0:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])
    if not returns:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / len(returns)
    return math.sqrt(variance) * math.sqrt(24)


def _momentum(prices: List[float], period: int = 6) -> float:
    if len(prices) < period + 1:
        return 0.0
    return (prices[-1] - prices[-period - 1]) / prices[-period - 1] if prices[-period - 1] else 0.0


def analyze(asset_key: str, history: List[dict], current_price: float) -> dict:
    """Aggressive analysis. Returns signal dict."""
    prices = [h["price"] for h in history] + [current_price]
    prices = prices[-168:]

    sma5 = _sma(prices, 5)
    sma20 = _sma(prices, 20)
    rsi = _rsi(prices, 14)
    vol = _volatility(prices, 24)
    mom = _momentum(prices, 6)

    confidence = 0.0
    reasons = []

    # Aggressive rules: momentum is king
    if mom > 0.02:
        confidence += 0.40
        reasons.append("strong_momentum_up")
    elif mom < -0.02:
        confidence += 0.35
        reasons.append("strong_momentum_down")

    if sma5 and sma20:
        if sma5 > sma20 * 1.005:
            confidence += 0.25
            reasons.append("breakout")
        elif sma5 < sma20 * 0.995:
            confidence += 0.20
            reasons.append("breakdown")

    if rsi is not None:
        if 45 < rsi < 65:
            confidence += 0.15
            reasons.append("healthy_momentum")
        elif rsi > 70:
            confidence += 0.10
            reasons.append("overbought_but_trending")
        elif rsi < 30:
            confidence -= 0.10
            reasons.append("possible_reversal")

    # Volatility is an opportunity, not a risk
    if vol is not None:
        if vol > 0.03:
            confidence += 0.10
            reasons.append("volatility_opportunity")

    confidence = max(0.0, min(1.0, confidence))
    direction = "HOLD"
    if confidence >= 0.55:
        if mom > 0 or (sma5 and sma20 and sma5 > sma20):
            direction = "LONG"
        elif mom < 0 or (sma5 and sma20 and sma5 < sma20):
            direction = "SHORT"

    return {
        "observer": "AGGRESSIVE",
        "asset": asset_key,
        "trend": "UP" if (sma5 and sma20 and sma5 > sma20) else ("DOWN" if (sma5 and sma20 and sma5 < sma20) else "FLAT"),
        "rsi": round(rsi, 2) if rsi else None,
        "volatility": round(vol, 6) if vol else None,
        "sma5": round(sma5, 4) if sma5 else None,
        "sma20": round(sma20, 4) if sma20 else None,
        "momentum": round(mom, 6),
        "confidence": round(confidence, 4),
        "direction": direction,
        "reason_codes": reasons,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
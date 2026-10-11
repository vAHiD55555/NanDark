"""Observer A — Conservative Study.

Preset assumption: historical patterns repeat; markets are mean-reverting
over medium term. High risk aversion. Only strong signals accepted.
Purpose: study whether conservative rules reduce drawdown.
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


def analyze(asset_key: str, history: List[dict], current_price: float) -> dict:
    """Conservative analysis. Returns signal dict."""
    prices = [h["price"] for h in history] + [current_price]
    prices = prices[-168:]

    sma5 = _sma(prices, 5)
    sma20 = _sma(prices, 20)
    sma50 = _sma(prices, 50)
    rsi = _rsi(prices, 14)
    vol = _volatility(prices, 24)

    confidence = 0.0
    reasons = []

    # Conservative rules: require multiple confirmations
    if sma5 and sma20 and sma50:
        if sma5 > sma20 > sma50:
            confidence += 0.40
            reasons.append("strong_uptrend")
        elif sma5 < sma20 < sma50:
            confidence += 0.35
            reasons.append("strong_downtrend")

    if rsi is not None:
        if rsi < 25:
            confidence += 0.25
            reasons.append("deep_oversold")
        elif rsi > 75:
            confidence -= 0.15
            reasons.append("deep_overbought")

    if vol is not None:
        if vol > 0.06:
            confidence -= 0.25
            reasons.append("extreme_volatility")
        elif vol < 0.008:
            confidence += 0.10
            reasons.append("very_stable")

    # Conservative: only trade when confidence is very high
    confidence = max(0.0, min(1.0, confidence))
    direction = "HOLD"
    if confidence >= 0.75:
        if sma5 and sma20 and sma5 > sma20:
            direction = "LONG"
        elif sma5 and sma20 and sma5 < sma20:
            direction = "SHORT"

    return {
        "observer": "CONSERVATIVE",
        "asset": asset_key,
        "trend": "UP" if (sma5 and sma20 and sma5 > sma20) else ("DOWN" if (sma5 and sma20 and sma5 < sma20) else "FLAT"),
        "rsi": round(rsi, 2) if rsi else None,
        "volatility": round(vol, 6) if vol else None,
        "sma5": round(sma5, 4) if sma5 else None,
        "sma20": round(sma20, 4) if sma20 else None,
        "sma50": round(sma50, 4) if sma50 else None,
        "confidence": round(confidence, 4),
        "direction": direction,
        "reason_codes": reasons,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
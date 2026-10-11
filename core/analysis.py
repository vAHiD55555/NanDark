"""Analysis layer — technical indicators, volatility, pattern detection.

All calculations are deterministic and based on the price history.
No external news API keys required; news/volatility are treated as
external context signals only (never commands).
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
import math


def _sma(prices: List[float], period: int) -> Optional[float]:
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def _stddev(prices: List[float], period: int) -> Optional[float]:
    if len(prices) < period:
        return None
    mean = sum(prices[-period:]) / period
    variance = sum((p - mean) ** 2 for p in prices[-period:]) / period
    return math.sqrt(variance)


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
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _volatility(prices: List[float], period: int = 24) -> Optional[float]:
    """Annualized volatility estimate from hourly returns."""
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
    return math.sqrt(variance) * math.sqrt(24)  # hourly -> daily


def _trend(prices: List[float]) -> str:
    """Simple trend classification based on SMA crossover."""
    if len(prices) < 2:
        return "FLAT"
    short = _sma(prices, 5)
    long_ = _sma(prices, 20)
    if short is None or long_ is None:
        return "FLAT"
    if short > long_ * 1.002:
        return "UP"
    if short < long_ * 0.998:
        return "DOWN"
    return "FLAT"


def _momentum(prices: List[float]) -> float:
    """Price change % over last 6 hours."""
    if len(prices) < 7:
        return 0.0
    return (prices[-1] - prices[-7]) / prices[-7] if prices[-7] else 0.0


def analyze(asset_key: str, history: List[dict], current_price: float) -> dict:
    """Run full analysis on price history. Returns signal dict."""
    prices = [h["price"] for h in history] + [current_price]
    prices = prices[-168:]  # cap at 1 week

    trend = _trend(prices)
    rsi = _rsi(prices, 14)
    vol = _volatility(prices, 24)
    mom = _momentum(prices)
    sma5 = _sma(prices, 5)
    sma20 = _sma(prices, 20)

    # Confidence scoring (0.0 - 1.0)
    confidence = 0.0
    reasons = []

    if trend == "UP" and mom > 0:
        confidence += 0.35
        reasons.append("uptrend_momentum")
    elif trend == "DOWN" and mom < 0:
        confidence += 0.30
        reasons.append("downtrend_momentum")

    if rsi is not None:
        if rsi < 30:
            confidence += 0.20
            reasons.append("rsi_oversold")
        elif rsi > 70:
            confidence -= 0.10
            reasons.append("rsi_overbought")

    if vol is not None:
        if vol > 0.05:
            confidence -= 0.15
            reasons.append("high_volatility")
        elif vol < 0.01:
            confidence += 0.05
            reasons.append("low_volatility")

    if sma5 and sma20:
        if sma5 > sma20:
            confidence += 0.10
            reasons.append("golden_cross")
        elif sma5 < sma20:
            confidence -= 0.10
            reasons.append("death_cross")

    confidence = max(0.0, min(1.0, confidence))

    direction = "HOLD"
    if confidence >= 0.55 and trend == "UP":
        direction = "LONG"
    elif confidence >= 0.55 and trend == "DOWN":
        direction = "SHORT"

    return {
        "asset": asset_key,
        "trend": trend,
        "rsi": round(rsi, 2) if rsi else None,
        "volatility": round(vol, 6) if vol else None,
        "momentum": round(mom, 6),
        "sma5": round(sma5, 4) if sma5 else None,
        "sma20": round(sma20, 4) if sma20 else None,
        "confidence": round(confidence, 4),
        "direction": direction,
        "reason_codes": reasons,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
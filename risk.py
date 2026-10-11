"""Risk Guardian — independent veto power over every trade decision.

HARD RULES (cannot be overridden):
1. quality=FAIL → NO_TRADE (no data = no trade)
2. quality=WARN → WAIT (synthetic/fixture data is forbidden)
3. quality=PASS → only then can a trade be considered
4. confidence < threshold → NO_TRADE
5. max open positions → NO_TRADE
6. drawdown limit → NO_TRADE

This module is intentionally decoupled from the analysis layer.
"""

from typing import Tuple


CONFIDENCE_THRESHOLD = 0.55
MAX_DRAWDOWN = 0.20
MAX_OPEN_POSITIONS = 2


def evaluate(signal: dict, open_count: int, current_balance: float,
             peak_balance: float, paper_mode: bool = True) -> Tuple[str, str]:
    """Return (decision, reason). Hard veto: NO_TRADE cannot be overridden."""

    quality = signal.get("quality", "FAIL")

    # HARD VETO: FAIL quality — no exceptions, ever
    if quality == "FAIL":
        return "NO_TRADE", "data_quality=FAIL — no live data available"

    # HARD VETO: WARN quality — synthetic/fixture data is forbidden
    if quality == "WARN":
        return "WAIT", "data_quality=WARN — synthetic data is not allowed"

    # Only PASS quality reaches here
    if quality != "PASS":
        return "NO_TRADE", f"unknown quality={quality}"

    # Hard veto: too many open positions
    if open_count >= MAX_OPEN_POSITIONS:
        return "NO_TRADE", f"max_open_positions={MAX_OPEN_POSITIONS} reached"

    # Hard veto: drawdown check
    if peak_balance > 0:
        drawdown = (peak_balance - current_balance) / peak_balance
        if drawdown > MAX_DRAWDOWN:
            return "NO_TRADE", f"drawdown={drawdown:.2%} exceeds {MAX_DRAWDOWN:.0%}"

    # Hard veto: confidence threshold
    if signal.get("confidence", 0) < CONFIDENCE_THRESHOLD:
        return "NO_TRADE", f"confidence={signal.get('confidence')} < {CONFIDENCE_THRESHOLD}"

    direction = signal.get("direction", "HOLD")
    if direction == "LONG":
        return "PAPER_LONG", "risk check passed"
    if direction == "SHORT":
        return "PAPER_SHORT", "risk check passed"

    return "WAIT", "no clear direction"
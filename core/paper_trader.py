"""Paper trading engine — tracks virtual positions and PnL.

NO real money is ever moved. All trades are simulated.
This is the ONLY path to a real trade: paper -> verify -> explicit user approval.
"""

from typing import Optional, Dict, List
from datetime import datetime, timezone


class PaperTrader:
    def __init__(self, balance: float = 10000.0):
        self.starting_balance = balance
        self.balance = balance
        self.peak_balance = balance
        self.positions: Dict[str, dict] = {}
        self.trades: List[dict] = []

    def open_position(self, asset: str, side: str, price: float, qty: float,
                      timestamp: str) -> dict:
        cost = price * qty
        if cost > self.balance:
            qty = self.balance / price
            cost = price * qty
        self.balance -= cost
        self.positions[asset] = {
            "side": side,
            "entry_price": price,
            "quantity": qty,
            "entry_time": timestamp,
            "status": "OPEN",
        }
        return {"action": "OPEN", "asset": asset, "side": side, "qty": qty, "price": price}

    def close_position(self, asset: str, price: float, timestamp: str) -> Optional[dict]:
        pos = self.positions.pop(asset, None)
        if not pos:
            return None
        exit_value = price * pos["quantity"]
        if pos["side"] == "LONG":
            pnl = exit_value - (pos["entry_price"] * pos["quantity"])
        else:  # SHORT
            pnl = (pos["entry_price"] * pos["quantity"]) - exit_value
        self.balance += exit_value
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance

        result = {
            "asset": asset,
            "side": pos["side"],
            "entry_price": pos["entry_price"],
            "exit_price": price,
            "quantity": pos["quantity"],
            "pnl": round(pnl, 4),
            "outcome": "PROFIT" if pnl > 0 else "LOSS",
            "entry_time": pos["entry_time"],
            "exit_time": timestamp,
        }
        self.trades.append(result)
        return result

    def get_open_pnl(self, current_prices: dict) -> float:
        total = 0.0
        for asset, pos in self.positions.items():
            price = current_prices.get(asset, pos["entry_price"])
            if pos["side"] == "LONG":
                total += (price - pos["entry_price"]) * pos["quantity"]
            else:
                total += (pos["entry_price"] - price) * pos["quantity"]
        return round(total, 4)

    def summary(self) -> dict:
        wins = [t for t in self.trades if t["outcome"] == "PROFIT"]
        losses = [t for t in self.trades if t["outcome"] == "LOSS"]
        return {
            "starting_balance": self.starting_balance,
            "current_balance": round(self.balance, 4),
            "peak_balance": round(self.peak_balance, 4),
            "total_trades": len(self.trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(self.trades), 4) if self.trades else 0.0,
            "realized_pnl": round(sum(t["pnl"] for t in self.trades), 4),
            "open_positions": list(self.positions.keys()),
        }
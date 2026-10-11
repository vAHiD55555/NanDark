"""Data layer — REAL data only.

Uses free public APIs with NO key required:
- CoinGecko: crypto prices + history (free tier, no key)
- MetalPriceAPI: gold/silver prices (free tier, no key)

NO synthetic fallback. If an API fails, quality=FAIL and NO trade/prediction is made.
This is intentional: we never fabricate market data.

Includes caching to respect rate limits (CoinGecko: ~10-30 req/min).
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict

try:
    import urllib.request
    import urllib.error
    import urllib.parse
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

try:
    from core.config import ASSETS, DATA_DIR, LOOKBACK_HOURS
except ImportError:
    from config import ASSETS, DATA_DIR, LOOKBACK_HOURS


# Cache: {url: (data, timestamp)}
_cache: Dict[str, tuple] = {}
CACHE_TTL_PRICE = 60        # 60 seconds for live prices
CACHE_TTL_HISTORY = 300     # 5 minutes for history


def _http_get(url: str, timeout: int = 10) -> Optional[dict]:
    """GET request returning parsed JSON. Returns None on any failure."""
    if not HAS_URLLIB:
        return None
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "BlackBird/0.4",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            # Rate limited — do NOT retry immediately
            return None
        return None
    except Exception:
        return None


def _cached_get(url: str, ttl: int, timeout: int = 10) -> Optional[dict]:
    """GET with caching. Returns cached data if fresh, else fetches."""
    now = time.time()
    if url in _cache:
        data, ts = _cache[url]
        if now - ts < ttl:
            return data
    data = _http_get(url, timeout)
    if data is not None:
        _cache[url] = (data, now)
    return data


# ---------------------------------------------------------------------------
# Live price fetchers (real data only)
# ---------------------------------------------------------------------------
def _fetch_crypto_live(asset_key: str) -> Optional[float]:
    """Fetch live crypto price from CoinGecko (free, no key)."""
    cfg = ASSETS[asset_key]
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={urllib.parse.quote(cfg['coingecko_id'])}&vs_currencies=usd"
    )
    data = _cached_get(url, CACHE_TTL_PRICE)
    if data:
        price = data.get(cfg["coingecko_id"], {}).get("usd")
        if price:
            return float(price)
    return None


def _fetch_commodity_live(asset_key: str) -> Optional[float]:
    """Fetch live commodity price from MetalPriceAPI (free, no key)."""
    cfg = ASSETS[asset_key]
    url = "https://api.metalpriceapi.com/v1/latest"
    data = _cached_get(url, CACHE_TTL_PRICE)
    if data:
        rates = data.get("rates", {})
        symbol = cfg["symbol"].lower()
        currency = cfg["quote"].lower()
        pair = f"{symbol}_{currency}"
        rate = rates.get(pair)
        if rate:
            return float(1.0 / float(rate))
    return None


def _fetch_history_crypto(asset_key: str, days: int) -> Optional[list]:
    """Fetch historical candles from CoinGecko (free, no key)."""
    cfg = ASSETS[asset_key]
    url = (
        f"https://api.coingecko.com/api/v3/coins/{cfg['coingecko_id']}"
        f"/market_chart?vs_currency=usd&days={max(1, days)}"
    )
    data = _cached_get(url, CACHE_TTL_HISTORY, timeout=15)
    if data and "prices" in data:
        return [{"epoch": int(pt[0]), "price": float(pt[1])} for pt in data["prices"]]
    return None


def _fetch_history_commodity(asset_key: str, days: int) -> Optional[list]:
    """Commodity history not available on free tier. Returns None."""
    return None


# ---------------------------------------------------------------------------
# Public API — REAL DATA ONLY
# ---------------------------------------------------------------------------
def get_price(asset_key: str) -> dict:
    """Return live price. quality=FAIL if unavailable — caller must NOT trade."""
    cfg = ASSETS[asset_key]
    ts = int(time.time())

    if cfg["type"] == "crypto":
        price = _fetch_crypto_live(asset_key)
        source = "coingecko"
    else:
        price = _fetch_commodity_live(asset_key)
        source = "metalpriceapi"

    if price is None:
        return {
            "asset": asset_key,
            "name": cfg["name"],
            "type": cfg["type"],
            "quote": cfg["quote"],
            "price": None,
            "source": source,
            "quality": "FAIL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch": ts,
        }

    return {
        "asset": asset_key,
        "name": cfg["name"],
        "type": cfg["type"],
        "quote": cfg["quote"],
        "price": round(price, 4),
        "source": source,
        "quality": "PASS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epoch": ts,
    }


def get_history(asset_key: str, hours: int = LOOKBACK_HOURS) -> Optional[list]:
    """Return historical candles. Returns None if unavailable."""
    cfg = ASSETS[asset_key]
    days = max(1, hours // 24)

    if cfg["type"] == "crypto":
        return _fetch_history_crypto(asset_key, days)
    else:
        return _fetch_history_commodity(asset_key, days)


def save_snapshot(price_data: dict):
    """Append a price snapshot to the local JSONL history file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    fname = os.path.join(DATA_DIR, f"{price_data['asset']}.jsonl")
    with open(fname, "a", encoding="utf-8") as f:
        f.write(json.dumps(price_data, ensure_ascii=False) + "\n")
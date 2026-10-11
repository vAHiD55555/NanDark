"""BlackBird Core — configuration and asset definitions."""

ASSETS = {
    "BTC": {
        "name": "Bitcoin",
        "symbol": "BTC",
        "type": "crypto",
        "quote": "USD",
        "coingecko_id": "bitcoin",
    },
    "XAU_USD": {
        "name": "Gold",
        "symbol": "XAU",
        "type": "commodity",
        "quote": "USD",
    },
    "XAU_EUR": {
        "name": "Gold",
        "symbol": "XAU",
        "type": "commodity",
        "quote": "EUR",
    },
    "XAG_USD": {
        "name": "Silver",
        "symbol": "XAG",
        "type": "commodity",
        "quote": "USD",
    },
}

TIMEFRAME = "1h"
VERSION = "0.4.0"
PAPER_BALANCE = 10000.0
CONFIDENCE_THRESHOLD = 0.55
LOOKBACK_HOURS = 24 * 7
LOG_DIR = "logs"
DATA_DIR = "data"
LOOP_INTERVAL_SECONDS = 900
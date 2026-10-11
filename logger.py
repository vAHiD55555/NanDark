"""Logger — appends JSONL entries to the logs/ directory.

Each entry is a complete snapshot: prices, analysis, decisions, outcomes.
"""

import json
import os
from datetime import datetime, timezone

try:
    from core.config import LOG_DIR
except ImportError:
    LOG_DIR = "logs"


def ensure_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def write_log(entry: dict):
    ensure_dir()
    fname = os.path.join(LOG_DIR, f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl")
    with open(fname, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_today_logs() -> list:
    ensure_dir()
    fname = os.path.join(LOG_DIR, f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl")
    if not os.path.exists(fname):
        return []
    entries = []
    with open(fname, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries
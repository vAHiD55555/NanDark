#!/usr/bin/env python3
"""Configuration module for NanDark deployment."""

import os
from datetime import datetime, timezone

# Server
PORT = int(os.environ.get("PORT", "8080"))
HOST = "0.0.0.0"
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Application
APP_NAME = "NanDark"
APP_VERSION = "0.2.0"
APP_MODE = "OBSERVE_ONLY"

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Healthcheck
HEALTHCHECK_INTERVAL = 300  # 5 minutes
MAX_ERROR_COUNT = 5


def get_startup_info():
    """Return startup info."""
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "mode": APP_MODE,
        "port": PORT,
        "debug": DEBUG,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

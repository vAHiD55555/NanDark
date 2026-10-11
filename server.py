#!/usr/bin/env python3
import os
from datetime import datetime, timezone

from flask import Flask, jsonify

from main import ASSETS, build_signal, risk_guardian, VERSION

app = Flask(__name__)


def build_observer_payload():
    signals = [build_signal(asset) for asset in ASSETS]
    decisions = []
    for sig in signals:
        verdict, reason = risk_guardian(sig)
        decisions.append({
            "asset": sig["asset"],
            "decision": verdict,
            "reason": reason,
            "market": {
                "asset": sig["asset"],
                "price": sig.get("price"),
                "source": sig["source"],
                "fetched_at": sig["timestamp"],
            },
            "risk": {
                "status": "PASS" if verdict != "NO_TRADE" else "VETO",
                "note": reason,
            },
            "version": VERSION,
        })

    return {
        "system": "BlackBird Core",
        "version": VERSION,
        "mode": "OBSERVE_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions,
    }


@app.get("/")
def index():
    return jsonify({
        "status": "ok",
        "service": "NanDark",
        "mode": "OBSERVE_ONLY",
        "message": "NanDark observer is running.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "NanDark",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/status")
def status():
    return jsonify(build_observer_payload())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)

"""Alert routing for convergence signals.

Formats HIGH/CRITICAL convergence signals into alert messages,
saves to JSONL log, and provides a send_alert() hook for future
Telegram delivery.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .convergence import ConvergenceSignal, run_convergence_scan

# Paths
LOG_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/logs")
ALERTS_JSONL = LOG_DIR / "convergence_alerts.jsonl"
CONVERGENCE_LOG = LOG_DIR / "convergence.log"

# Set up file logger
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger("atlas_intel.alerts")

_file_handler = logging.FileHandler(CONVERGENCE_LOG)
_file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(_file_handler)
logger.setLevel(logging.INFO)

# Severity emoji
SEVERITY_EMOJI = {
    "LOW": "🟢",
    "MEDIUM": "🟡",
    "HIGH": "🟠",
    "CRITICAL": "🔴",
}


def format_alert(signal: ConvergenceSignal) -> str:
    """Format a convergence signal into a human-readable alert message."""
    emoji = SEVERITY_EMOJI.get(signal.severity, "⚪")
    source_types = sorted(set(s.source_type for s in signal.sources))
    feeds = ", ".join(source_types)

    lines = [
        f"{emoji} **{signal.severity} CONVERGENCE ALERT** {emoji}",
        "",
        f"📍 Region: {signal.region}",
        f"📊 Confidence: {signal.confidence:.0%}",
        f"🔗 Similarity: {signal.similarity_score:.3f}",
        f"📡 Feeds ({len(source_types)}): {feeds}",
        "",
        f"📝 {signal.narrative}",
        "",
    ]

    if signal.affected_assets:
        lines.append(f"💰 Predicted impact: {', '.join(signal.affected_assets)}")

    # Source details
    lines.append("")
    lines.append("Sources:")
    for src in signal.sources:
        snippet = src.content_text[:100] if src.content_text else "—"
        lines.append(f"  • [{src.source_type}] {snippet}")

    return "\n".join(lines)


def send_alert(message: str) -> None:
    """Write alert to file. Telegram delivery to be wired later."""
    alert_file = LOG_DIR / "latest_alert.txt"
    alert_file.write_text(message)
    logger.info("Alert written to %s", alert_file)


def _save_alert_jsonl(signal: ConvergenceSignal, message: str) -> None:
    """Append alert to JSONL log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "id": signal.id,
        "severity": signal.severity,
        "region": signal.region,
        "similarity_score": signal.similarity_score,
        "confidence": signal.confidence,
        "source_types": sorted(set(s.source_type for s in signal.sources)),
        "affected_assets": signal.affected_assets,
        "narrative": signal.narrative,
        "message": message,
    }
    with open(ALERTS_JSONL, "a") as f:
        f.write(json.dumps(record) + "\n")


def process_signals(signals: list[ConvergenceSignal]) -> list[str]:
    """Process convergence signals: format, save, and alert on HIGH/CRITICAL."""
    alerts_sent = []
    for signal in signals:
        message = format_alert(signal)
        _save_alert_jsonl(signal, message)
        logger.info(
            "Signal %s: severity=%s region=%s confidence=%.2f",
            signal.id, signal.severity, signal.region, signal.confidence,
        )
        if signal.severity in ("HIGH", "CRITICAL"):
            send_alert(message)
            alerts_sent.append(message)
            logger.info("HIGH/CRITICAL alert dispatched for %s", signal.id)
    return alerts_sent


def run_alert_loop(interval_seconds: int = 300) -> None:
    """Run the alert check loop (every 5 minutes by default)."""
    logger.info("Starting convergence alert loop (interval=%ds)", interval_seconds)
    while True:
        try:
            signals = run_convergence_scan(store_results=True)
            if signals:
                alerts = process_signals(signals)
                logger.info("Scan complete: %d signals, %d alerts", len(signals), len(alerts))
            else:
                logger.info("Scan complete: no convergence signals")
        except Exception as exc:
            logger.error("Alert loop error: %s", exc, exc_info=True)
        time.sleep(interval_seconds)


def check_once() -> list[str]:
    """Run a single convergence check and return any alert messages."""
    signals = run_convergence_scan(store_results=True)
    return process_signals(signals) if signals else []


if __name__ == "__main__":
    import sys
    if "--loop" in sys.argv:
        run_alert_loop()
    else:
        alerts = check_once()
        for a in alerts:
            print(a)
            print("---")
        if not alerts:
            print("No HIGH/CRITICAL convergence signals detected.")

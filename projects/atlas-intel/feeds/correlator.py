#!/usr/bin/env python3
"""Cross-modal correlator for Atlas Intel.

Reads all feed data files and detects convergence patterns:
- CLOSURE: zero vessels at chokepoint + geopolitical news about it
- CONTANGO: floating storage spike + oil price news
- REROUTING: chokepoint congestion spike + alternative route congestion
- CONFLICT: military activity near chokepoint + vessel absence

Outputs convergence.json and sends high-confidence alerts via Telegram.
"""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("atlas_intel.correlator")

DATA_DIR = PROJECT_ROOT / "dashboard" / "data"

# Chokepoint name mappings (vessel_live uses snake_case, geopolitical uses display names)
CHOKEPOINT_ALIASES = {
    "strait_of_hormuz": ["Strait of Hormuz", "hormuz", "persian gulf"],
    "hormuz": ["Strait of Hormuz", "hormuz", "persian gulf"],
    "suez_canal": ["Suez Canal", "suez"],
    "suez": ["Suez Canal", "suez"],
    "malacca_strait": ["Strait of Malacca", "malacca", "singapore"],
    "malacca": ["Strait of Malacca", "malacca", "singapore"],
    "bab_el_mandeb": ["Bab-el-Mandeb", "bab el-mandeb", "red sea", "houthi"],
    "panama_canal": ["Panama Canal", "panama"],
    "turkish_straits": ["Turkish Straits", "bosphorus", "dardanelles"],
    "danish_straits": ["Danish Straits"],
}

# Which chokepoints are alternatives for each other
ALTERNATIVE_ROUTES = {
    "suez_canal": ["bab_el_mandeb"],
    "bab_el_mandeb": ["suez_canal"],
    "strait_of_hormuz": ["hormuz"],
    "malacca_strait": ["malacca"],
}

SIGNAL_ICONS = {
    "CLOSURE": "🚫",
    "CONTANGO": "🛢️",
    "REROUTING": "🔄",
    "CONFLICT": "⚔️",
    "ANOMALY": "⚠️",
}

SIGNAL_SEVERITY = {
    "CLOSURE": "critical",
    "CONFLICT": "critical",
    "CONTANGO": "high",
    "REROUTING": "high",
    "ANOMALY": "medium",
}


def load_json(filename: str) -> dict:
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load %s: %s", filename, e)
        return {}


def load_all_feeds() -> dict[str, dict]:
    return {
        "vessels": load_json("vessel_live.json"),
        "geopolitical": load_json("geopolitical.json"),
        "gdelt": load_json("gdelt_status.json"),
        "thermal": load_json("thermal_status.json"),
        "flights": load_json("flight_status.json"),
    }


def get_vessel_stats(vessel_data: dict) -> dict[str, dict]:
    """Compute per-chokepoint vessel stats."""
    vessels = vessel_data.get("vessels", [])
    stats: dict[str, dict] = {}

    by_chokepoint: dict[str, list] = {}
    for v in vessels:
        cp = v.get("chokepoint", "unknown")
        by_chokepoint.setdefault(cp, []).append(v)

    for cp, vlist in by_chokepoint.items():
        total = len(vlist)
        stationary = sum(1 for v in vlist if v.get("speed") == 0 or v.get("speed") is None)
        moving = total - stationary
        stationary_ratio = stationary / total if total > 0 else 0

        stats[cp] = {
            "total": total,
            "stationary": stationary,
            "moving": moving,
            "stationary_ratio": round(stationary_ratio, 3),
        }

    return stats


def geopolitical_mentions_chokepoint(events: list[dict], chokepoint: str) -> list[dict]:
    """Find geopolitical events mentioning a chokepoint."""
    aliases = set()
    for key, alias_list in CHOKEPOINT_ALIASES.items():
        if key == chokepoint or chokepoint in key or key in chokepoint:
            aliases.update(a.lower() for a in alias_list)

    if not aliases:
        aliases = {chokepoint.lower().replace("_", " ")}

    matching = []
    for ev in events:
        text = f"{ev.get('title', '')} {ev.get('summary', '')}".lower()
        regions = [r.lower() for r in ev.get("regions", [])]
        if any(a in text or a in " ".join(regions) for a in aliases):
            matching.append(ev)
    return matching


def detect_closure_signals(vessel_stats: dict, geo_events: list[dict]) -> list[dict]:
    """CLOSURE: zero/very few vessels at chokepoint + geopolitical news about it."""
    signals = []
    for cp, stats in vessel_stats.items():
        if stats["total"] <= 2:  # Near-zero vessels
            mentions = geopolitical_mentions_chokepoint(geo_events, cp)
            if mentions:
                top_event = mentions[0]
                confidence = min(0.95, 0.6 + 0.1 * len(mentions))
                signals.append(make_signal(
                    signal_type="CLOSURE",
                    confidence=confidence,
                    narrative=(
                        f"Potential chokepoint closure at {cp.replace('_', ' ').title()}: "
                        f"only {stats['total']} vessel(s) detected, "
                        f"with {len(mentions)} geopolitical event(s) referencing this area. "
                        f"Lead event: \"{top_event.get('title', 'N/A')}\""
                    ),
                    contributing_sources=[
                        {"feed": "vessel_tracker", "detail": f"{stats['total']} vessels at {cp}"},
                        {"feed": "geopolitical", "detail": f"{len(mentions)} matching events"},
                    ],
                    affected_assets=["crude_oil", "shipping_etfs", "insurance_rates"],
                    region=cp.replace("_", " ").title(),
                ))
    return signals


def detect_contango_signals(vessel_stats: dict, geo_events: list[dict]) -> list[dict]:
    """CONTANGO: high stationary ratio (floating storage) + oil price news."""
    signals = []
    for cp, stats in vessel_stats.items():
        if stats["stationary_ratio"] > 0.5 and stats["total"] > 10:
            oil_events = [e for e in geo_events
                          if "crude_oil" in e.get("commodities", [])
                          or "oil" in f"{e.get('title', '')} {e.get('summary', '')}".lower()]
            if oil_events:
                confidence = min(0.90, 0.4 + stats["stationary_ratio"] * 0.3 + 0.05 * len(oil_events))
                signals.append(make_signal(
                    signal_type="CONTANGO",
                    confidence=confidence,
                    narrative=(
                        f"Floating storage pattern detected at {cp.replace('_', ' ').title()}: "
                        f"{stats['stationary']}/{stats['total']} vessels stationary "
                        f"(ratio {stats['stationary_ratio']:.0%}), "
                        f"coinciding with {len(oil_events)} oil-related news event(s). "
                        f"This pattern suggests contango-driven storage or supply buildup."
                    ),
                    contributing_sources=[
                        {"feed": "vessel_tracker", "detail": f"{stats['stationary_ratio']:.0%} stationary at {cp}"},
                        {"feed": "geopolitical", "detail": f"{len(oil_events)} oil-related events"},
                    ],
                    affected_assets=["crude_oil", "tanker_stocks", "oil_futures", "contango_spread"],
                    region=cp.replace("_", " ").title(),
                ))
    return signals


def detect_rerouting_signals(vessel_stats: dict, geo_events: list[dict]) -> list[dict]:
    """REROUTING: congestion spike at one chokepoint + activity at alternative."""
    signals = []
    for cp, stats in vessel_stats.items():
        if stats["total"] > 50:  # High traffic
            for alt_cp_key, alt_list in ALTERNATIVE_ROUTES.items():
                if cp in alt_cp_key or alt_cp_key in cp:
                    for alt_cp in alt_list:
                        alt_stats = vessel_stats.get(alt_cp, {})
                        if alt_stats.get("total", 0) > 50:
                            mentions = geopolitical_mentions_chokepoint(geo_events, cp)
                            if mentions:
                                confidence = min(0.80, 0.3 + 0.1 * len(mentions))
                                signals.append(make_signal(
                                    signal_type="REROUTING",
                                    confidence=confidence,
                                    narrative=(
                                        f"Potential rerouting detected: {cp.replace('_', ' ').title()} has "
                                        f"{stats['total']} vessels while alternative route "
                                        f"{alt_cp.replace('_', ' ').title()} shows {alt_stats['total']} vessels. "
                                        f"Geopolitical context: {mentions[0].get('title', 'N/A')}"
                                    ),
                                    contributing_sources=[
                                        {"feed": "vessel_tracker", "detail": f"{stats['total']} vessels at {cp}"},
                                        {"feed": "vessel_tracker", "detail": f"{alt_stats['total']} vessels at {alt_cp}"},
                                        {"feed": "geopolitical", "detail": f"{len(mentions)} related events"},
                                    ],
                                    affected_assets=["shipping_etfs", "freight_rates", "insurance_rates"],
                                    region=cp.replace("_", " ").title(),
                                ))
    return signals


def detect_conflict_signals(
    vessel_stats: dict,
    geo_events: list[dict],
    flight_data: dict,
    thermal_data: dict,
) -> list[dict]:
    """CONFLICT: military activity near chokepoint + vessel absence."""
    signals = []
    flights = flight_data.get("flights", [])
    hotspots = thermal_data.get("hotspots", []) if isinstance(thermal_data.get("hotspots"), list) else []
    has_military_flights = len(flights) > 0 and flight_data.get("anomalies", 0) > 0
    has_thermal = len(hotspots) > 0

    for cp, stats in vessel_stats.items():
        if stats["total"] <= 5:  # Low vessel presence
            military_events = [
                e for e in geo_events
                if any(kw in f"{e.get('title', '')} {e.get('summary', '')}".lower()
                       for kw in ("military", "conflict", "naval", "attack", "strike", "war"))
            ]
            cp_military = geopolitical_mentions_chokepoint(military_events, cp)

            if cp_military or has_military_flights or has_thermal:
                sources = [
                    {"feed": "vessel_tracker", "detail": f"Only {stats['total']} vessels at {cp}"},
                ]
                if cp_military:
                    sources.append({"feed": "geopolitical", "detail": f"{len(cp_military)} military events near {cp}"})
                if has_military_flights:
                    sources.append({"feed": "flight_tracker", "detail": f"{flight_data.get('anomalies', 0)} flight anomalies"})
                if has_thermal:
                    sources.append({"feed": "thermal", "detail": f"{len(hotspots)} thermal hotspots"})

                confidence = min(0.95, 0.3 + 0.15 * len(sources))
                signals.append(make_signal(
                    signal_type="CONFLICT",
                    confidence=confidence,
                    narrative=(
                        f"Potential conflict zone at {cp.replace('_', ' ').title()}: "
                        f"vessel traffic at {stats['total']} (near zero) with "
                        f"{len(cp_military)} military-related geopolitical events"
                        + (f", {flight_data.get('anomalies', 0)} flight anomalies" if has_military_flights else "")
                        + (f", {len(hotspots)} thermal hotspots" if has_thermal else "")
                        + ". Vessels appear to be avoiding this area."
                    ),
                    contributing_sources=sources,
                    affected_assets=["crude_oil", "defense_stocks", "gold", "vix", "shipping_etfs"],
                    region=cp.replace("_", " ").title(),
                ))
    return signals


def detect_anomaly_signals(vessel_stats: dict, gdelt_data: dict) -> list[dict]:
    """ANOMALY: GDELT significant events correlating with vessel patterns."""
    signals = []
    gdelt_events = gdelt_data.get("events", [])
    significant = [e for e in gdelt_events if e.get("significance", 0) > 30]

    if significant and any(s["stationary_ratio"] > 0.4 for s in vessel_stats.values()):
        signals.append(make_signal(
            signal_type="ANOMALY",
            confidence=0.45,
            narrative=(
                f"GDELT detected {len(significant)} significant event(s) "
                f"concurrent with elevated stationary vessel ratios across monitored chokepoints. "
                f"Lead GDELT event: {significant[0].get('title', 'N/A')[:120]}"
            ),
            contributing_sources=[
                {"feed": "gdelt", "detail": f"{len(significant)} significant events"},
                {"feed": "vessel_tracker", "detail": "Elevated stationary ratios"},
            ],
            affected_assets=["vix", "gold", "treasuries"],
            region="Global",
        ))
    return signals


def make_signal(
    signal_type: str,
    confidence: float,
    narrative: str,
    contributing_sources: list[dict],
    affected_assets: list[str],
    region: str = "Unknown",
) -> dict:
    return {
        "id": str(uuid4()),
        "signal_type": signal_type,
        "icon": SIGNAL_ICONS.get(signal_type, "⚠️"),
        "severity": SIGNAL_SEVERITY.get(signal_type, "medium"),
        "confidence": round(confidence, 3),
        "narrative": narrative,
        "contributing_sources": contributing_sources,
        "affected_assets": affected_assets,
        "region": region,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_correlation() -> list[dict]:
    """Main correlation pass across all feeds."""
    feeds = load_all_feeds()
    vessel_stats = get_vessel_stats(feeds["vessels"])
    geo_events = feeds["geopolitical"].get("events", [])

    logger.info("Vessel stats: %s", {k: v["total"] for k, v in vessel_stats.items()})
    logger.info("Geopolitical events: %d", len(geo_events))

    signals: list[dict] = []
    signals.extend(detect_closure_signals(vessel_stats, geo_events))
    signals.extend(detect_contango_signals(vessel_stats, geo_events))
    signals.extend(detect_rerouting_signals(vessel_stats, geo_events))
    signals.extend(detect_conflict_signals(
        vessel_stats, geo_events,
        feeds["flights"], feeds["thermal"],
    ))
    signals.extend(detect_anomaly_signals(vessel_stats, feeds["gdelt"]))

    # Sort: critical first, then by confidence desc
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    signals.sort(key=lambda s: (sev_order.get(s["severity"], 4), -s["confidence"]))

    return signals


def save_convergence(signals: list[dict]) -> None:
    """Write convergence.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "status": "online",
        "updated": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal_count": len(signals),
        "signals": signals,
    }
    (DATA_DIR / "convergence.json").write_text(json.dumps(output, indent=2))
    logger.info("Wrote %d convergence signals", len(signals))


def send_alerts(signals: list[dict]) -> None:
    """Send high-confidence alerts via the Atlas Intel alert system."""
    try:
        from atlas_intel.alerts import send_alert, SEVERITY_EMOJI, LOG_DIR, ALERTS_JSONL
        import json as _json

        for sig in signals:
            if sig["confidence"] < 0.6 or sig["severity"] not in ("critical", "high"):
                continue

            emoji = "🔴" if sig["severity"] == "critical" else "🟠"
            lines = [
                f"{emoji} **{sig['signal_type']} CONVERGENCE** {emoji}",
                "",
                f"📍 Region: {sig['region']}",
                f"📊 Confidence: {sig['confidence']:.0%}",
                f"🔗 Sources: {len(sig['contributing_sources'])} feeds",
                "",
                f"📝 {sig['narrative']}",
            ]
            if sig["affected_assets"]:
                lines.append(f"\n💰 Impact: {', '.join(sig['affected_assets'])}")

            message = "\n".join(lines)
            send_alert(message)
            logger.info("Alert sent for %s signal (confidence %.0f%%)",
                        sig["signal_type"], sig["confidence"] * 100)
    except Exception as e:
        logger.warning("Failed to send alerts: %s", e)


def run() -> None:
    """Main entry: correlate, save, alert."""
    logger.info("Starting cross-modal correlation")
    signals = run_correlation()
    save_convergence(signals)

    if signals:
        send_alerts(signals)
        logger.info("Correlation complete: %d signals", len(signals))
    else:
        logger.info("No convergence signals detected")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    run()

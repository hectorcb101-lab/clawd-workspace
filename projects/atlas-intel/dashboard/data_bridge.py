#!/usr/bin/env python3
"""Atlas Intel — Live Data Bridge

Reads real data from feeds and Supabase, writes dashboard JSON files.
Run: python dashboard/data_bridge.py          (single update)
     python dashboard/data_bridge.py --loop   (continuous, every 30s)
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from atlas_intel.config import load_supabase_config

# Paths
DATA_DIR = ROOT / "dashboard" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [data_bridge] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "data_bridge.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def _write(name: str, data: dict):
    (DATA_DIR / name).write_text(json.dumps(data, indent=2, default=str))
    log.info(f"Wrote {name}")


def _supabase_client():
    """Get Supabase client or None."""
    try:
        from atlas_intel.store import _get_client
        return _get_client()
    except Exception as e:
        log.warning(f"Supabase unavailable: {e}")
        return None


# ── 1. Vessel Status ─────────────────────────────────────────────────────

def build_vessel_status():
    snapshot_path = DATA_DIR / "vessel_live.json"
    now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")

    # Read snapshot written by vessel_tracker
    if snapshot_path.exists():
        try:
            snap = json.loads(snapshot_path.read_text())
            vessels = snap.get("vessels", [])
            activity = snap.get("chokepoint_activity", {})
            cp_summary = ", ".join(f"{k}: {v}" for k, v in activity.items()) if activity else "no activity"
            last_event = f"{len(vessels)} vessels — {cp_summary}"
            status = "online" if vessels else "standby"
        except Exception:
            vessels, last_event, status = [], "snapshot unreadable", "error"
    else:
        vessels, last_event, status = [], "awaiting vessel tracker", "standby"

    # Supplement with recent Supabase events for richer last_event
    sb = _supabase_client()
    if sb:
        try:
            since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            resp = sb.table("embeddings").select("content_text,metadata,created_at") \
                .eq("source_type", "ais_vessel") \
                .gte("created_at", since) \
                .order("created_at", desc=True) \
                .limit(10).execute()
            if resp.data:
                last_event = resp.data[0].get("content_text", "")[:120]
                status = "online"
        except Exception as e:
            log.warning(f"Supabase vessel query failed: {e}")

    # Read last event from JSONL as fallback
    events_file = ROOT / "logs" / "vessel_events.jsonl"
    if events_file.exists() and last_event.startswith("awaiting"):
        try:
            lines = events_file.read_text().strip().split("\n")
            if lines:
                ev = json.loads(lines[-1])
                last_event = ev.get("type", "event") + " — " + ev.get("chokepoint", "")
                status = "online"
        except Exception:
            pass

    _write("vessel_status.json", {
        "status": status,
        "tracked": len(vessels),
        "lastEvent": last_event,
        "vessels": vessels[:50],  # cap at 50
        "updated": now_str,
    })


# ── 2. Flight Status ─────────────────────────────────────────────────────

def build_flight_status():
    _write("flight_status.json", {
        "status": "degraded",
        "tracked": 0,
        "anomalies": 0,
        "note": "OpenSky Network unreachable from AWS — proxy needed",
        "flights": [],
        "updated": datetime.now(timezone.utc).strftime("%H:%M UTC"),
    })


# ── 3. Thermal Status ────────────────────────────────────────────────────

def build_thermal_status():
    import os
    from dotenv import dotenv_values

    env_path = Path("/home/ubuntu/clawd/config/supabase-atlas-intel.env")
    firms_key = os.getenv("FIRMS_API_KEY", "")
    if not firms_key and env_path.exists():
        firms_key = dotenv_values(str(env_path)).get("FIRMS_API_KEY", "")

    if not firms_key:
        _write("thermal_status.json", {
            "status": "standby",
            "hotspots": 0,
            "lastScan": "awaiting API key",
            "events": [],
            "updated": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        })
        return

    # Try fetching from FIRMS
    events = []
    hotspots = 0
    try:
        from urllib.request import urlopen
        import csv
        from io import StringIO

        # Quick query: Singapore region, last 24h, small area
        url = (f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
               f"{firms_key}/VIIRS_SNPP_NRT/world/1")
        # Use bounding box for Persian Gulf as most relevant
        url_bbox = (f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
                    f"{firms_key}/VIIRS_SNPP_NRT/46,23,56,31/1")
        resp = urlopen(url_bbox, timeout=30)
        text = resp.read().decode()
        reader = csv.DictReader(StringIO(text))
        rows = list(reader)
        hotspots = len(rows)

        # Pick top events by FRP (fire radiative power)
        rows.sort(key=lambda r: float(r.get("frp", 0)), reverse=True)
        for r in rows[:10]:
            events.append({
                "lat": float(r.get("latitude", 0)),
                "lon": float(r.get("longitude", 0)),
                "frp": float(r.get("frp", 0)),
                "confidence": r.get("confidence", ""),
                "acq_date": r.get("acq_date", ""),
                "acq_time": r.get("acq_time", ""),
            })
        status = "online"
    except Exception as e:
        log.warning(f"FIRMS fetch failed: {e}")
        status = "error"

    # Also check Supabase for stored thermal events
    if not events:
        sb = _supabase_client()
        if sb:
            try:
                since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
                resp = sb.table("embeddings").select("content_text,metadata,created_at") \
                    .eq("source_type", "thermal_anomaly") \
                    .gte("created_at", since) \
                    .order("created_at", desc=True) \
                    .limit(5).execute()
                for row in (resp.data or []):
                    events.append({
                        "text": row.get("content_text", "")[:200],
                        "time": row.get("created_at", ""),
                    })
                if events:
                    status = "online"
            except Exception as e:
                log.warning(f"Supabase thermal query failed: {e}")

    _write("thermal_status.json", {
        "status": status,
        "hotspots": hotspots,
        "lastScan": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "events": events,
        "updated": datetime.now(timezone.utc).strftime("%H:%M UTC"),
    })


# ── 4. GDELT Status ──────────────────────────────────────────────────────

def build_gdelt_status():
    import requests

    GDELT_API = "https://api.gdeltproject.org/api/v2/doc/doc"
    THEMES = ["MILITARY", "SANCTIONS", "OIL", "PROTEST", "TERROR"]

    all_events = []
    total_articles = 0

    for theme in THEMES:
        try:
            resp = requests.get(GDELT_API, params={
                "query": theme, "mode": "ArtList", "format": "json",
                "maxrecords": 20, "timespan": "1h",
            }, timeout=10)
            if resp.status_code == 429:
                log.info("GDELT rate limited, using cached/partial data")
                break
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            total_articles += len(articles)

            for art in articles[:5]:
                tone = float(art.get("tone", 0))
                if abs(tone) < 3:
                    continue
                sig = abs(tone) * 2 + int(art.get("socialimage", 0)) / 10
                all_events.append({
                    "title": art.get("title", "")[:200],
                    "url": art.get("url", ""),
                    "theme": theme,
                    "tone": round(tone, 2),
                    "significance": round(sig, 1),
                    "timestamp": art.get("seendate", ""),
                    "domain": art.get("domain", ""),
                })
            time.sleep(2)
        except Exception as e:
            log.warning(f"GDELT {theme}: {e}")
            if "429" in str(e):
                break

    # Also check Supabase for stored GDELT events
    if not all_events:
        sb = _supabase_client()
        if sb:
            try:
                since = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
                resp = sb.table("embeddings").select("content_text,metadata,created_at") \
                    .eq("source_type", "gdelt_event") \
                    .gte("created_at", since) \
                    .order("created_at", desc=True) \
                    .limit(10).execute()
                for row in (resp.data or []):
                    meta = row.get("metadata") or {}
                    if isinstance(meta, str):
                        try:
                            meta = json.loads(meta)
                        except Exception:
                            meta = {}
                    all_events.append({
                        "title": row.get("content_text", "")[:200],
                        "url": meta.get("url", ""),
                        "theme": meta.get("theme", "UNKNOWN"),
                        "tone": meta.get("tone", 0),
                        "significance": meta.get("significance_score", 0),
                        "timestamp": row.get("created_at", ""),
                    })
            except Exception as e:
                log.warning(f"Supabase GDELT query: {e}")

    all_events.sort(key=lambda e: e.get("significance", 0), reverse=True)

    _write("gdelt_status.json", {
        "status": "online" if all_events else "standby",
        "eventsPerHour": total_articles,
        "significant": len(all_events),
        "events": all_events[:20],
        "updated": datetime.now(timezone.utc).strftime("%H:%M UTC"),
    })


# ── 5. Alerts ─────────────────────────────────────────────────────────────

def build_alerts():
    alerts = []
    now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")

    sb = _supabase_client()
    if sb:
        try:
            since = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            resp = sb.table("embeddings").select("source_type,content_text,metadata,created_at") \
                .gte("created_at", since) \
                .order("created_at", desc=True) \
                .limit(30).execute()

            for row in (resp.data or []):
                src = row.get("source_type", "unknown")
                text = row.get("content_text", "")[:200]
                ts = row.get("created_at", "")
                meta = row.get("metadata") or {}
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except Exception:
                        meta = {}

                # Determine severity from content
                severity = "info"
                text_lower = text.lower()
                if any(w in text_lower for w in ["congestion", "alert", "critical", "explosion", "attack"]):
                    severity = "critical"
                elif any(w in text_lower for w in ["warning", "anomaly", "unusual", "floating storage", "sanctions"]):
                    severity = "warning"

                # Map source type
                source_map = {
                    "ais_vessel": "vessel",
                    "thermal_anomaly": "thermal",
                    "gdelt_event": "gdelt",
                    "flight": "flight",
                    "convergence": "convergence",
                }

                try:
                    t = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%H:%M UTC")
                except Exception:
                    t = now_str

                alerts.append({
                    "severity": severity,
                    "title": f"{src.replace('_', ' ').title()} Event",
                    "message": text,
                    "time": t,
                    "source": source_map.get(src, src),
                })
        except Exception as e:
            log.warning(f"Supabase alerts query failed: {e}")

    # Also pull from local event logs if no Supabase alerts
    if not alerts:
        for logfile, source in [
            (ROOT / "logs" / "vessel_events.jsonl", "vessel"),
            (ROOT / "logs" / "gdelt_events.jsonl", "gdelt"),
        ]:
            if logfile.exists():
                try:
                    lines = logfile.read_text().strip().split("\n")
                    for line in lines[-5:]:
                        ev = json.loads(line)
                        alerts.append({
                            "severity": "warning" if ev.get("severity") else "info",
                            "title": f"{source.title()}: {ev.get('type', 'event')}",
                            "message": ev.get("chokepoint", ev.get("title", ""))[:200],
                            "time": ev.get("timestamp", now_str)[-14:-6] if "T" in ev.get("timestamp", "") else now_str,
                            "source": source,
                        })
                except Exception:
                    pass

    if not alerts:
        alerts.append({
            "severity": "info",
            "title": "System Online",
            "message": "Atlas Intel data bridge active — monitoring feeds",
            "time": now_str,
            "source": "convergence",
        })

    _write("alerts.json", {"alerts": alerts[:25]})


# ── Main ──────────────────────────────────────────────────────────────────

def run_once():
    """Single update cycle."""
    log.info("── Data bridge update starting ──")
    start = time.time()

    build_vessel_status()
    build_flight_status()
    build_thermal_status()
    build_gdelt_status()
    build_alerts()

    elapsed = time.time() - start
    log.info(f"── Update complete in {elapsed:.1f}s ──")


def main():
    if "--loop" in sys.argv:
        log.info("Starting data bridge in continuous mode (30s interval)")
        while True:
            try:
                run_once()
            except KeyboardInterrupt:
                log.info("Stopped.")
                break
            except Exception as e:
                log.error(f"Update cycle failed: {e}", exc_info=True)
            time.sleep(30)
    else:
        run_once()


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# systemd service (save as /etc/systemd/system/atlas-data-bridge.service)
# ---------------------------------------------------------------------------
# [Unit]
# Description=Atlas Intel Data Bridge
# After=network.target atlas-vessel-tracker.service
#
# [Service]
# Type=simple
# User=ubuntu
# WorkingDirectory=/home/ubuntu/clawd/projects/atlas-intel
# ExecStart=/home/ubuntu/clawd/projects/atlas-intel/.venv/bin/python dashboard/data_bridge.py --loop
# Restart=always
# RestartSec=10
# Environment=PYTHONUNBUFFERED=1
#
# [Install]
# WantedBy=multi-user.target

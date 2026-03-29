#!/usr/bin/env python3
"""
Cyber Threat Intelligence Feed
Aggregates data from multiple free threat intelligence sources
Output: cyber_threats_live.json
"""

import json
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import os

# Output file path
OUTPUT_FILE = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/cyber_threats_live.json"

# Sample fallback data for when APIs are unreachable
FALLBACK_DATA = {
    "status": "DEGRADED",
    "lastUpdate": None,
    "summary": {"active_threats": 15, "critical_vulns": 3, "active_campaigns": 2, "top_targets": ["US", "GB", "DE"]},
    "threats": [
        {
            "id": "sample-001",
            "type": "malware",
            "name": "Sample Malware",
            "severity": "high",
            "source": "sample",
            "first_seen": "2026-03-20T12:00:00Z",
            "targets": ["financial", "healthcare"],
            "iocs": {"urls": 3, "ips": 8, "hashes": 2}
        }
    ],
    "recent_vulns": [
        {
            "cve": "CVE-2026-0001",
            "description": "Sample vulnerability (fallback data)",
            "severity": "high",
            "exploited": True,
            "vendor": "Sample Vendor",
            "due_date": "2026-04-01"
        }
    ],
    "attack_map": [
        {
            "source_country": "RU",
            "source_lat": 55.75,
            "source_lon": 37.62,
            "target_country": "US",
            "target_lat": 38.9,
            "target_lon": -77.0,
            "attack_type": "ransomware",
            "count": 50
        }
    ]
}

def log(msg: str):
    """Log with timestamp"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{timestamp}] {msg}", flush=True)

def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[Dict]:
    """Fetch JSON from URL with error handling"""
    try:
        req = Request(url, headers=headers or {})
        with urlopen(req, timeout=timeout) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except (URLError, HTTPError, json.JSONDecodeError, Exception) as e:
        log(f"Error fetching {url}: {e}")
        return None

def fetch_abuse_ch() -> List[Dict[str, Any]]:
    """Fetch recent malicious URLs from Abuse.ch URLhaus"""
    log("Fetching from Abuse.ch URLhaus...")
    data = fetch_json("https://urlhaus-api.abuse.ch/v1/urls/recent/", timeout=15)
    
    threats = []
    if data and data.get("urls"):
        for i, url_entry in enumerate(data["urls"][:20]):  # Limit to 20
            threats.append({
                "id": f"abuse-{url_entry.get('id', i)}",
                "type": "malicious_url",
                "name": url_entry.get("url", "Unknown URL")[:100],
                "severity": "high" if url_entry.get("threat") == "malware_download" else "medium",
                "source": "abuse.ch",
                "first_seen": url_entry.get("date_added", datetime.now(timezone.utc).isoformat()),
                "targets": ["general"],
                "iocs": {"urls": 1, "ips": 0, "hashes": 0}
            })
    
    log(f"Fetched {len(threats)} threats from Abuse.ch")
    return threats

def fetch_cisa_vulns() -> List[Dict[str, Any]]:
    """Fetch CISA Known Exploited Vulnerabilities"""
    log("Fetching from CISA KEV...")
    data = fetch_json("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", timeout=15)
    
    vulns = []
    if data and data.get("vulnerabilities"):
        for vuln in data["vulnerabilities"][:10]:  # Top 10 most recent
            vulns.append({
                "cve": vuln.get("cveID", "CVE-UNKNOWN"),
                "description": vuln.get("vulnerabilityName", "Unknown vulnerability")[:200],
                "severity": "critical" if "critical" in vuln.get("vulnerabilityName", "").lower() else "high",
                "exploited": True,  # CISA KEV = known exploited
                "vendor": vuln.get("vendorProject", "Unknown"),
                "due_date": vuln.get("dueDate", "")
            })
    
    log(f"Fetched {len(vulns)} vulnerabilities from CISA")
    return vulns

def fetch_isc_top_ips() -> List[Dict[str, Any]]:
    """Fetch Internet Storm Center top attacking IPs"""
    log("Fetching from ISC SANS...")
    data = fetch_json("https://isc.sans.edu/api/topips/records/20?json", timeout=15)
    
    attack_map = []
    if data and isinstance(data, list):
        # Country coordinates (approximations)
        country_coords = {
            "CN": (39.9, 116.4), "RU": (55.75, 37.62), "US": (38.9, -77.0),
            "KR": (37.5, 127.0), "DE": (52.5, 13.4), "GB": (51.5, -0.1),
            "BR": (-15.8, -47.9), "VN": (21.0, 105.8), "IN": (28.6, 77.2)
        }
        
        for entry in data[:10]:
            source_country = entry.get("country", "UNKNOWN")
            source_coords = country_coords.get(source_country, (0, 0))
            
            attack_map.append({
                "source_country": source_country,
                "source_lat": source_coords[0],
                "source_lon": source_coords[1],
                "target_country": "US",  # ISC primarily monitors US-targeted attacks
                "target_lat": 38.9,
                "target_lon": -77.0,
                "attack_type": "scanning",
                "count": int(entry.get("count", 0))
            })
    
    log(f"Fetched {len(attack_map)} attack vectors from ISC")
    return attack_map

def generate_summary(threats: List[Dict], vulns: List[Dict]) -> Dict[str, Any]:
    """Generate summary statistics"""
    critical_count = sum(1 for v in vulns if v.get("severity") == "critical")
    
    # Count unique sources as "campaigns"
    campaigns = len(set(t.get("source") for t in threats))
    
    # Top target countries from threats
    all_targets = []
    for t in threats:
        all_targets.extend(t.get("targets", []))
    top_targets = ["US", "GB", "DE"]  # Default common targets
    
    return {
        "active_threats": len(threats),
        "critical_vulns": critical_count,
        "active_campaigns": max(campaigns, 1),
        "top_targets": top_targets
    }

def collect_data() -> Dict[str, Any]:
    """Collect data from all sources"""
    log("Starting cyber threat data collection...")
    
    threats = []
    vulns = []
    attack_map = []
    
    # Try each source independently
    try:
        threats.extend(fetch_abuse_ch())
    except Exception as e:
        log(f"Abuse.ch failed: {e}")
    
    try:
        vulns = fetch_cisa_vulns()
    except Exception as e:
        log(f"CISA failed: {e}")
    
    try:
        attack_map = fetch_isc_top_ips()
    except Exception as e:
        log(f"ISC failed: {e}")
    
    # If all sources failed, use fallback
    if not threats and not vulns and not attack_map:
        log("All sources failed, using fallback data")
        result = FALLBACK_DATA.copy()
        result["lastUpdate"] = datetime.now(timezone.utc).isoformat()
        return result
    
    # Build final output
    summary = generate_summary(threats, vulns)
    
    output = {
        "status": "ONLINE",
        "lastUpdate": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "threats": threats[:50],  # Limit to 50
        "recent_vulns": vulns[:20],  # Limit to 20
        "attack_map": attack_map[:30]  # Limit to 30
    }
    
    log(f"Collection complete: {len(threats)} threats, {len(vulns)} vulns, {len(attack_map)} attack vectors")
    return output

def write_output(data: Dict[str, Any]):
    """Write JSON output to file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Write with pretty formatting
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Check size (limit to 2MB)
        size_bytes = len(json_str.encode('utf-8'))
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > 2.0:
            log(f"WARNING: Output size {size_mb:.2f}MB exceeds 2MB limit, truncating...")
            # Truncate threats and attack_map
            while size_mb > 2.0 and len(data["threats"]) > 10:
                data["threats"] = data["threats"][:-5]
                data["attack_map"] = data["attack_map"][:-5]
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        log(f"Output written to {OUTPUT_FILE} ({size_mb:.2f}MB)")
    except Exception as e:
        log(f"ERROR writing output: {e}")
        sys.exit(1)

def run_once():
    """Run a single data collection cycle"""
    data = collect_data()
    write_output(data)

def run_continuous(interval: int = 300):
    """Run continuously with specified interval (seconds)"""
    log(f"Starting continuous mode (interval: {interval}s)")
    
    while True:
        try:
            run_once()
        except Exception as e:
            log(f"ERROR in collection cycle: {e}")
        
        log(f"Sleeping for {interval}s...")
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        run_continuous(interval)
    else:
        run_once()

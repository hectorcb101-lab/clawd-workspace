#!/usr/bin/env python3
"""
Cyber Threat Intelligence Feed Backend for Atlas Intel Dashboard

Fetches real-time cyber threat intelligence from multiple free sources:
1. Feodo Tracker - Botnet C2 servers (abuse.ch)
2. URLhaus - Recent malware distribution URLs (abuse.ch)
3. ThreatFox - Recent IOCs including botnets and malware (abuse.ch)
4. ip-api.com - IP geolocation (free tier: 45 req/min)

Output: cyber_threats_live.json with geolocated threats, severity classification,
and aggregated statistics for the Atlas Intel dashboard.

No API keys required. Rate limiting is handled automatically.

Usage:
    python3 cyber_tracker.py

Output location: ../dashboard/data/cyber_threats_live.json
"""

import json
import time
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# Rate limiting for ip-api.com (45 requests per minute)
class RateLimiter:
    def __init__(self, max_requests: int = 45, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        now = time.time()
        # Remove requests older than time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            # Wait until oldest request falls out of window
            sleep_time = self.time_window - (now - self.requests[0]) + 1
            if sleep_time > 0:
                print(f"Rate limit: waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                self.requests = []
        
        self.requests.append(now)

rate_limiter = RateLimiter()

def fetch_feodo_tracker() -> List[Dict[str, Any]]:
    """Fetch botnet C2 servers from Feodo Tracker"""
    print("Fetching Feodo Tracker data...")
    try:
        resp = requests.get(
            "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        threats = []
        for entry in data:
            if not entry.get('ip_address'):
                continue
            
            # Calculate recency for severity
            first_seen = entry.get('first_seen', '')
            last_seen = entry.get('last_online', first_seen)
            
            threats.append({
                'ip': entry['ip_address'],
                'type': 'botnet',
                'source': 'Feodo Tracker',
                'description': f"{entry.get('malware', 'Unknown')} C2 server on port {entry.get('port', 'unknown')} ({entry.get('status', 'unknown')})",
                'first_seen': first_seen,
                'last_seen': last_seen,
                'tags': [entry.get('malware', 'unknown').lower(), 'c2', 'botnet'],
                'raw_data': entry
            })
        
        print(f"✓ Feodo Tracker: {len(threats)} threats")
        return threats
    
    except Exception as e:
        print(f"✗ Feodo Tracker failed: {e}")
        return []

def fetch_urlhaus() -> List[Dict[str, Any]]:
    """Fetch malware URLs from URLhaus"""
    print("Fetching URLhaus data...")
    try:
        resp = requests.get(
            "https://urlhaus.abuse.ch/downloads/json_recent/",
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        threats = []
        # URLhaus JSON format: {id: [entry], id: [entry], ...}
        for entry_id, entry_list in data.items():
            if not isinstance(entry_list, list) or not entry_list:
                continue
            
            entry = entry_list[0]  # Each ID has one entry in a list
            url = entry.get('url', '')
            
            # Extract IP from URL if present
            import re
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', url)
            host = ip_match.group(1) if ip_match else None
            
            tags = entry.get('tags', [])
            if not isinstance(tags, list):
                tags = []
            tags.append('malware-url')
            
            threats.append({
                'ip': host,
                'type': 'malware',
                'source': 'URLhaus',
                'description': f"{entry.get('url_status', 'Active')} malware: {entry.get('threat', 'unknown')}",
                'first_seen': entry.get('dateadded', ''),
                'last_seen': entry.get('last_online', entry.get('dateadded', '')),
                'tags': tags,
                'raw_data': entry
            })
            
            # Limit to 100 most recent
            if len(threats) >= 100:
                break
        
        print(f"✓ URLhaus: {len(threats)} threats")
        return threats
    
    except Exception as e:
        print(f"✗ URLhaus failed: {e}")
        return []

def fetch_threatfox() -> List[Dict[str, Any]]:
    """Fetch recent IOCs from ThreatFox"""
    print("Fetching ThreatFox data...")
    try:
        resp = requests.get(
            "https://threatfox.abuse.ch/export/json/recent/",
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        threats = []
        for entry_id, entry_list in data.items():
            if not isinstance(entry_list, list) or not entry_list:
                continue
            
            entry = entry_list[0]
            ioc_type = entry.get('ioc_type', '')
            ioc_value = entry.get('ioc_value', '')
            
            # Extract IP if it's an IP:port or just IP
            ip = None
            if ioc_type in ['ip:port', 'ip']:
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ioc_value)
                if ip_match:
                    ip = ip_match.group(1)
            
            # Determine threat type
            threat_type_map = {
                'botnet_cc': 'botnet',
                'payload_delivery': 'malware',
                'c2': 'botnet'
            }
            threat_type = threat_type_map.get(entry.get('threat_type', '').lower(), 'malware')
            
            # Parse tags
            tags_str = entry.get('tags', '')
            tags = [t.strip().lower() for t in tags_str.split(',')] if tags_str else []
            tags.append(threat_type)
            
            threats.append({
                'ip': ip,
                'type': threat_type,
                'source': 'ThreatFox',
                'description': f"{entry.get('malware_printable', 'Unknown malware')} {entry.get('threat_type', 'threat')}",
                'first_seen': entry.get('first_seen_utc', ''),
                'last_seen': entry.get('last_seen_utc', entry.get('first_seen_utc', '')),
                'tags': tags[:5],  # Limit tags
                'raw_data': entry
            })
            
            # Limit to 100 most recent
            if len(threats) >= 100:
                break
        
        print(f"✓ ThreatFox: {len(threats)} threats")
        return threats
    
    except Exception as e:
        print(f"✗ ThreatFox failed: {e}")
        return []

def geolocate_ips(ips: List[str]) -> Dict[str, Dict[str, Any]]:
    """Geolocate IPs using ip-api.com batch endpoint"""
    if not ips:
        return {}
    
    # Filter valid IPs and remove duplicates
    valid_ips = list(set([ip for ip in ips if ip and is_valid_ip(ip)]))
    
    if not valid_ips:
        return {}
    
    print(f"Geolocating {len(valid_ips)} unique IPs...")
    
    geo_data = {}
    
    # Process in batches of 100 (API limit)
    for i in range(0, len(valid_ips), 100):
        batch = valid_ips[i:i+100]
        
        rate_limiter.wait_if_needed()
        
        try:
            resp = requests.post(
                "http://ip-api.com/batch",
                json=batch,
                params={'fields': 'status,country,countryCode,lat,lon,query'},
                timeout=30
            )
            resp.raise_for_status()
            results = resp.json()
            
            for result in results:
                if result.get('status') == 'success':
                    ip = result['query']
                    geo_data[ip] = {
                        'country': result.get('country', 'Unknown'),
                        'country_code': result.get('countryCode', 'XX'),
                        'lat': result.get('lat', 0.0),
                        'lon': result.get('lon', 0.0),
                        'lng': result.get('lon', 0.0)  # Duplicate field as requested
                    }
            
            print(f"  Batch {i//100 + 1}: {len([r for r in results if r.get('status') == 'success'])}/{len(batch)} successful")
        
        except Exception as e:
            print(f"  Batch {i//100 + 1} failed: {e}")
    
    print(f"✓ Geolocated {len(geo_data)} IPs")
    return geo_data

def is_valid_ip(ip: str) -> bool:
    """Basic IP validation"""
    if not ip or '/' in ip or ':' in ip:  # Skip CIDR and IPv6 for now
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def classify_severity(threat: Dict[str, Any]) -> str:
    """Classify threat severity based on type and recency"""
    threat_type = threat['type']
    last_seen = threat.get('last_seen', '')
    
    # Parse last seen date
    try:
        if last_seen:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    last_seen_dt = datetime.strptime(last_seen.split('.')[0], fmt)
                    break
                except ValueError:
                    continue
            else:
                last_seen_dt = datetime.now() - timedelta(days=30)  # Default to 30 days ago
        else:
            last_seen_dt = datetime.now() - timedelta(days=30)
    except:
        last_seen_dt = datetime.now() - timedelta(days=30)
    
    days_old = (datetime.now() - last_seen_dt).days
    
    # Severity rules
    if threat_type == 'ransomware':
        return 'critical' if days_old < 7 else 'high'
    elif threat_type == 'botnet':
        if days_old < 1:
            return 'critical'
        elif days_old < 3:
            return 'high'
        elif days_old < 14:
            return 'medium'
        else:
            return 'low'
    elif threat_type == 'malware':
        if days_old < 1:
            return 'high'
        elif days_old < 7:
            return 'medium'
        else:
            return 'low'
    
    return 'medium'

def process_threats() -> Dict[str, Any]:
    """Main processing function"""
    print("\n=== Cyber Threat Intelligence Feed ===\n")
    
    # Fetch all threat data
    all_threats = []
    all_threats.extend(fetch_feodo_tracker())
    all_threats.extend(fetch_urlhaus())
    all_threats.extend(fetch_threatfox())
    
    print(f"\nTotal raw threats collected: {len(all_threats)}")
    
    # Extract IPs for geolocation
    ips_to_geolocate = [t['ip'] for t in all_threats if t.get('ip')]
    geo_data = geolocate_ips(ips_to_geolocate)
    
    # Process and enrich threats
    processed_threats = []
    for threat in all_threats:
        ip = threat.get('ip')
        
        # Add geolocation if available
        if ip and ip in geo_data:
            threat.update(geo_data[ip])
        else:
            # Use country from raw data if available (e.g., ransomware)
            threat.setdefault('country', 'Unknown')
            threat.setdefault('lat', 0.0)
            threat.setdefault('lon', 0.0)
            threat.setdefault('lng', 0.0)
        
        # Classify severity
        threat['severity'] = classify_severity(threat)
        
        # Build final threat object
        processed_threat = {
            'lat': threat['lat'],
            'lon': threat['lon'],
            'lng': threat['lng'],
            'type': threat['type'],
            'severity': threat['severity'],
            'source': threat['source'],
            'ip': threat.get('ip', 'N/A'),
            'country': threat['country'],
            'description': threat['description'],
            'first_seen': threat['first_seen'],
            'last_seen': threat['last_seen'],
            'tags': threat['tags']
        }
        
        processed_threats.append(processed_threat)
    
    # Sort by severity (critical > high > medium > low), then by last_seen
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    processed_threats.sort(
        key=lambda x: (severity_order.get(x['severity'], 9), x['last_seen'] or ''),
        reverse=True
    )
    
    # Calculate stats
    active = len(processed_threats)
    critical = len([t for t in processed_threats if t['severity'] == 'critical'])
    
    by_type = {}
    for threat in processed_threats:
        by_type[threat['type']] = by_type.get(threat['type'], 0) + 1
    
    by_country = {}
    for threat in processed_threats:
        country = threat['country']
        by_country[country] = by_country.get(country, 0) + 1
    
    # Build output
    output = {
        'threats': processed_threats,
        'active': active,
        'critical': critical,
        'by_type': by_type,
        'by_country': by_country,
        'generated_at': datetime.now().isoformat() + 'Z'
    }
    
    print(f"\n=== Statistics ===")
    print(f"Active threats: {active}")
    print(f"Critical: {critical}")
    print(f"By type: {by_type}")
    print(f"By country (top 5): {dict(sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:5])}")
    
    return output

def main():
    # Process threats
    output = process_threats()
    
    # Write output
    output_path = Path('/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/cyber_threats_live.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Output written to {output_path}")
    print(f"  Total threats: {len(output['threats'])}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    main()

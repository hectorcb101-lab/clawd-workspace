# Atlas Intel - Threat Intelligence Feeds

Backend data collectors for the Atlas Intel cyber threat dashboard.

## cyber_tracker.py

Real-time cyber threat intelligence aggregator.

### Data Sources (All Free, No API Keys)

1. **Feodo Tracker** - Active botnet C2 servers
   - URL: https://feodotracker.abuse.ch/downloads/ipblocklist.json
   - Update frequency: Real-time
   - Data: Botnet IPs, malware families, ports

2. **URLhaus** - Malware distribution URLs
   - URL: https://urlhaus.abuse.ch/downloads/json_recent/
   - Update frequency: Real-time
   - Data: Recent malware URLs, threat types, tags

3. **ThreatFox** - Recent Indicators of Compromise (IOCs)
   - URL: https://threatfox.abuse.ch/export/json/recent/
   - Update frequency: Real-time
   - Data: IPs, domains, malware families, C2 servers

4. **ip-api.com** - IP geolocation
   - URL: http://ip-api.com/batch
   - Rate limit: 45 requests/minute
   - Batch size: 100 IPs per request

### Output

**File:** `../dashboard/data/cyber_threats_live.json`

**Schema:**
```json
{
  "threats": [
    {
      "lat": float,
      "lon": float,
      "lng": float,  // duplicate of lon for compatibility
      "type": "botnet" | "malware" | "ransomware",
      "severity": "critical" | "high" | "medium" | "low",
      "source": string,
      "ip": string,
      "country": string,
      "description": string,
      "first_seen": string (ISO timestamp),
      "last_seen": string (ISO timestamp),
      "tags": [string]
    }
  ],
  "active": int,
  "critical": int,
  "by_type": {"botnet": int, "malware": int, ...},
  "by_country": {"US": int, "CN": int, ...},
  "generated_at": string (ISO timestamp)
}
```

### Severity Classification

- **Critical**: Botnets seen in last 24h, ransomware in last 7 days
- **High**: Botnets seen in last 3 days, malware in last 24h
- **Medium**: Botnets seen in last 14 days, malware in last 7 days
- **Low**: Older threats

### Usage

```bash
python3 cyber_tracker.py
```

### Rate Limiting

The script automatically handles ip-api.com rate limiting (45 req/min).
Typical run processes ~200 threats with ~70 unique IPs in under 10 seconds.

### Requirements

- Python 3.7+
- `requests` library

```bash
pip install requests
```

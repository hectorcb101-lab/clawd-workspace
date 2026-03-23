# NASA FIRMS Thermal Anomaly Monitor

Real-time monitoring of thermal anomalies near critical energy infrastructure using NASA's Fire Information for Resource Management System (FIRMS).

## Features

### Detection Algorithms

1. **Proximity Detection**: Hotspots within 10km of known refineries/ports
2. **High Fire Radiative Power**: FRP > 100 MW (significant fires)
3. **Cluster Detection**: 3+ hotspots within 5km (major events)
4. **New Area Detection**: First-time hotspots in previously cold areas

### Monitored Facilities

**Persian Gulf (20 facilities)**
- Saudi Arabia: Abqaiq, Ras Tanura, Ghawar, Jubail
- UAE: Ruwais
- Qatar: Ras Laffan
- Iran: Abadan, Rasht

**Russia**
- Volgograd, Saratov

**Kazakhstan**
- Atyrau

**Singapore**
- Jurong Island

### Severity Levels

- **Critical**: <1km from facility + FRP > 500 MW, OR cluster of 10+ hotspots
- **High**: <3km from facility + FRP > 200 MW, OR FRP > 500 MW, OR cluster of 5+ hotspots
- **Medium**: Within 10km of facility, OR FRP > 100 MW
- **Low**: Other detections

## Setup

### 1. Get NASA FIRMS API Key (Free)

1. Visit: https://firms.modaps.eosdis.nasa.gov/api/area/
2. Click "Get MAP_KEY"
3. Fill in email and organization (optional)
4. Receive key instantly (no verification needed)

### 2. Configure API Key

**Option A: Environment Variable**
```bash
export FIRMS_API_KEY="your_key_here"
```

**Option B: Config File**
Add to `/home/ubuntu/clawd/config/supabase-atlas-intel.env`:
```bash
FIRMS_API_KEY=your_key_here
```

### 3. Test Installation

```bash
cd /home/ubuntu/clawd/projects/atlas-intel
./feeds/run_thermal_monitor.sh --test
```

## Usage

### Manual Run (with real API)
```bash
./feeds/run_thermal_monitor.sh
```

### Test Mode (mock data)
```bash
./feeds/run_thermal_monitor.sh --test
```

### Cron Job (every 6 hours)
Add to crontab:
```cron
# Run at 00:00, 06:00, 12:00, 18:00 UTC
0 */6 * * * cd /home/ubuntu/clawd/projects/atlas-intel && ./feeds/run_thermal_monitor.sh >> /home/ubuntu/clawd/projects/atlas-intel/logs/thermal_monitor_cron.log 2>&1
```

## Output

### Logs
- **thermal_monitor.log**: Main execution log
- **thermal_events.jsonl**: Event records (one JSON per line)
- **thermal_history.json**: Historical location tracking

### Vector Store
All anomalies are embedded and stored in Supabase:
- **Table**: `embeddings`
- **source_type**: `thermal_anomaly`
- **Metadata**: lat, lon, FRP, brightness, facility info, severity

### Example Event
```json
{
  "timestamp": "2026-03-23T12:58:18.875278+00:00",
  "event_text": "Thermal anomaly detected: proximity | Location: 25.9400, 49.6900 | FRP: 250.0 MW | Brightness: 350.0K | Near facility: Abqaiq (0.86km away) | Severity: critical",
  "metadata": {
    "lat": 25.94,
    "lon": 49.69,
    "frp": 250.0,
    "brightness": 350.0,
    "acq_date": "2026-03-23",
    "acq_time": "1058",
    "satellite": "N",
    "confidence": "high",
    "anomaly_type": "proximity",
    "severity": "critical",
    "facility_name": "Abqaiq",
    "facility_country": "SAU",
    "distance_km": 0.86
  }
}
```

## Data Source

**NASA FIRMS** (Fire Information for Resource Management System)
- **Dataset**: VIIRS_SNPP_NRT (Near Real-Time VIIRS)
- **Update Frequency**: ~3 hours
- **Resolution**: 375m at nadir
- **Coverage**: Global
- **Documentation**: https://firms.modaps.eosdis.nasa.gov/

### CSV Fields
- `latitude`, `longitude`: Location
- `brightness`: Brightness temperature (Kelvin)
- `frp`: Fire Radiative Power (MW)
- `confidence`: Detection confidence (low/nominal/high)
- `acq_date`, `acq_time`: Acquisition timestamp
- `satellite`: Satellite identifier
- `daynight`: D=day, N=night

## Querying

### Search for anomalies near a specific facility
```python
from atlas_intel.store import query_similar
from atlas_intel.embedder import embed_text

# Search for Abqaiq-related events
query = "thermal anomaly near Abqaiq refinery Saudi Arabia"
embedding = embed_text(query)
results = query_similar(embedding, top_k=10, filters={"source_type": "thermal_anomaly"})
```

### Raw SQL (Supabase)
```sql
SELECT 
  content_text,
  metadata->>'facility_name' as facility,
  metadata->>'severity' as severity,
  metadata->>'frp' as frp,
  created_at
FROM embeddings
WHERE source_type = 'thermal_anomaly'
  AND metadata->>'severity' IN ('critical', 'high')
ORDER BY created_at DESC
LIMIT 20;
```

## Troubleshooting

### "Invalid MAP_KEY" Error
- Ensure your API key is correctly set
- Check spelling and whitespace
- Verify key hasn't expired (keys don't expire but can be revoked)

### "No hotspots detected"
- This is normal if no fires in monitored regions
- FIRMS only reports active fires, not all time
- Check logs for API errors

### "HTTP 400 Bad Request"
- Usually means invalid bounding box or parameters
- Check script is using correct API format
- Verify FIRMS service is operational

## Performance

- **Execution time**: 5-30 seconds (depending on data volume)
- **API calls**: 4 regions × 1 request each = 4 requests
- **Rate limits**: FIRMS allows reasonable usage (no hard limit published)
- **Storage**: ~1-2 KB per event

## Future Enhancements

- [ ] Telegram/email alerts for critical events
- [ ] Historical trend analysis
- [ ] Integration with commodity price feeds
- [ ] Additional facility coordinates (expanded coverage)
- [ ] Satellite imagery correlation
- [ ] Machine learning for false positive reduction

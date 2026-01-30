#!/usr/bin/env python3
"""
Weather briefing generator - personalised weather for Finn
"""
import json
import urllib.request
from datetime import datetime

def get_weather_briefing(lat=51.5, lon=-0.12, name="London"):
    """Get personalised weather briefing."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&timezone=Europe/London&forecast_days=1"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}
    
    current = data["current_weather"]
    hourly = data["hourly"]
    
    temp = current["temperature"]
    wind = current["windspeed"]
    code = current["weathercode"]
    
    # Weather codes: 0=clear, 1-3=partly cloudy, 45-48=fog, 51-67=drizzle/rain, 71-77=snow, 80-82=showers, 95-99=thunderstorm
    conditions = {
        0: "Clear skies",
        1: "Mainly clear",
        2: "Partly cloudy", 
        3: "Overcast",
        45: "Foggy",
        48: "Foggy",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        80: "Light showers",
        81: "Showers",
        82: "Heavy showers",
    }
    condition = conditions.get(code, "Mixed conditions")
    
    # Get hourly data for rest of day
    now_hour = datetime.now().hour
    rain_probs = hourly["precipitation_probability"][now_hour:24]
    temps = hourly["temperature_2m"][now_hour:24]
    codes = hourly["weathercode"][now_hour:24]
    
    # Find rain windows
    rain_hours = []
    for i, prob in enumerate(rain_probs):
        if prob > 50:
            rain_hours.append(now_hour + i)
    
    # High/low for rest of day
    high = max(temps) if temps else temp
    low = min(temps) if temps else temp
    
    # Personalised advice
    advice = []
    
    # Temperature advice
    if temp < 5:
        advice.append("❄️ Properly cold - coat weather")
    elif temp < 10:
        advice.append("🧥 Jumper or light jacket")
    elif temp < 15:
        advice.append("👕 Light layers - pleasant")
    elif temp < 20:
        advice.append("☀️ T-shirt weather")
    else:
        advice.append("🔥 Warm one - stay cool")
    
    # Rain advice
    if rain_hours:
        first_rain = rain_hours[0]
        if first_rain <= now_hour + 2:
            advice.append(f"☔ Rain likely soon - grab an umbrella")
        elif first_rain < 18:
            advice.append(f"🌂 Rain expected around {first_rain}:00 - umbrella if going out this afternoon")
        else:
            advice.append(f"🌂 Dry until evening - rain rolling in after {first_rain}:00")
    else:
        advice.append("✨ No rain expected today")
    
    # Wind advice
    if wind > 30:
        advice.append("💨 Windy - hold onto your hat")
    elif wind > 20:
        advice.append("🍃 Breezy out there")
    
    return {
        "location": name,
        "temp": round(temp),
        "feels_like": round(temp - (wind / 10)),  # rough wind chill
        "condition": condition,
        "wind": round(wind),
        "high": round(high),
        "low": round(low),
        "advice": advice,
        "rain_hours": rain_hours,
        "summary": f"{round(temp)}°C, {condition.lower()}"
    }

if __name__ == "__main__":
    weather = get_weather_briefing()
    print(json.dumps(weather, indent=2))

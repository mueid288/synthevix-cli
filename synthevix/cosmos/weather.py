"""Cosmos module — OpenWeatherMap weather integration."""

from __future__ import annotations

from typing import Optional


import json
import requests
from datetime import datetime
from pathlib import Path
from synthevix.core.database import SYNTHEVIX_DIR

CACHE_FILE = SYNTHEVIX_DIR / "weather_cache.json"
CACHE_TTL = 1800  # 30 minutes

class WeatherError(Exception):
    def __init__(self, message, error_type="network"):
        super().__init__(message)
        self.error_type = error_type

def get_weather(location: str, api_key: str) -> Optional[dict]:
    """
    Fetch current weather from OpenWeatherMap.

    Returns a dict with keys: city, temp_c, feels_like_c, description, humidity, icon.
    Returns None if disabled (no location/key).
    Raises WeatherError on failure if no cache is available.
    """
    if not location or not api_key:
        return None

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={
            "q": location,
            "appid": api_key,
            "units": "metric",
        }, timeout=5)
        
        if resp.status_code == 401:
            raise WeatherError("Invalid API Key.", "auth")
        elif resp.status_code == 404:
            raise WeatherError(f"Location '{location}' not found.", "location")
        resp.raise_for_status()
        data = resp.json()

        result = {
            "city":        data.get("name", location),
            "temp_c":      data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "description": data["weather"][0]["description"].capitalize(),
            "humidity":    data["main"]["humidity"],
            "icon":        _weather_emoji(data["weather"][0]["id"]),
            "timestamp":   datetime.now().isoformat(),
            "cached":      False
        }
        
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(result, f)
        except Exception:
            pass
            
        return result

    except WeatherError as e:
        cached = _get_cached_weather()
        if cached:
            return cached
        raise e
    except Exception as e:
        cached = _get_cached_weather()
        if cached:
            return cached
        raise WeatherError("Network error or unavailable.", "network")

def _get_cached_weather() -> Optional[dict]:
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        
        ts = datetime.fromisoformat(data["timestamp"])
        age = (datetime.now() - ts).total_seconds()
        
        data["cached"] = True
        return data  # Return it anyway on error, the UI shows 'last updated'
    except Exception:
        return None


def _weather_emoji(condition_id: int) -> str:
    """Map OpenWeatherMap condition code to an emoji."""
    if condition_id < 300:
        return "⛈️"
    elif condition_id < 400:
        return "🌦️"
    elif condition_id < 600:
        return "🌧️"
    elif condition_id < 700:
        return "❄️"
    elif condition_id < 800:
        return "🌫️"
    elif condition_id == 800:
        return "☀️"
    elif condition_id < 900:
        return "⛅"
    return "🌡️"

"""Cosmos module — OpenWeatherMap weather integration."""

from __future__ import annotations

from typing import Optional


def get_weather(location: str, api_key: str) -> Optional[dict]:
    """
    Fetch current weather from OpenWeatherMap.

    Returns a dict with keys: city, temp_c, feels_like_c, description, humidity, icon.
    Returns None if disabled (no location/key) or on any request failure.
    """
    if not location or not api_key:
        return None

    try:
        import requests
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={
            "q": location,
            "appid": api_key,
            "units": "metric",
        }, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        return {
            "city":        data.get("name", location),
            "temp_c":      data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "description": data["weather"][0]["description"].capitalize(),
            "humidity":    data["main"]["humidity"],
            "icon":        _weather_emoji(data["weather"][0]["id"]),
        }
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

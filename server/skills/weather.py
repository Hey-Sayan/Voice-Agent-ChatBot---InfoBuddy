import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE = "https://api.openweathermap.org/data/2.5/weather"

class WeatherError(Exception):
    pass


def kelvin_to_c(k: float) -> float:
    return round(k - 273.15, 1)


def mps_to_kmph(mps: float) -> float:
    return round(mps * 3.6, 1)


def fetch_by_city(city: str) -> dict:
    if not API_KEY:
        raise WeatherError("Missing OPENWEATHER_API_KEY. Add it to .env")
    r = requests.get(BASE, params={"q": city, "appid": API_KEY}, timeout=10)
    if r.status_code != 200:
        raise WeatherError(f"OpenWeather error: {r.status_code} {r.text}")
    return r.json()


def fetch_by_coords(lat: float, lon: float) -> dict:
    if not API_KEY:
        raise WeatherError("Missing OPENWEATHER_API_KEY. Add it to .env")
    r = requests.get(BASE, params={"lat": lat, "lon": lon, "appid": API_KEY}, timeout=10)
    if r.status_code != 200:
        raise WeatherError(f"OpenWeather error: {r.status_code} {r.text}")
    return r.json()


def format_weather(data: dict) -> str:
    name = data.get("name") or "your location"
    main = data.get("weather", [{}])[0].get("description", "").capitalize()
    t = data.get("main", {})
    wind = data.get("wind", {})

    temp_c = kelvin_to_c(t.get("temp", 0))
    feels_c = kelvin_to_c(t.get("feels_like", 0))
    hum = t.get("humidity")
    wind_k = mps_to_kmph(wind.get("speed", 0))

    parts = [
        f"Weather in {name}: {main}.",
        f"Temp {temp_c}°C (feels {feels_c}°C)",
        f"Humidity {hum}%",
        f"Wind {wind_k} km/h",
    ]
    return " | ".join(parts)

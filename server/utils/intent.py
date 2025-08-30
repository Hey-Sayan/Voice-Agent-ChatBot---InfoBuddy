import re
from typing import Optional, Tuple

CITY_RE = re.compile(r"weather(?:\s+in\s+([a-zA-Z .'-]+))?", re.IGNORECASE)
COORD_RE = re.compile(r"weather\s+at\s*\(?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)?", re.IGNORECASE)
WIKI_RE = re.compile(r"(?:who is|what is|tell me about|wiki)\s+(.+)", re.IGNORECASE)


def detect(text: str) -> Tuple[str, Optional[Tuple]]:
    """Return (intent, payload)
    intents: weather_city(city), weather_coords(lat, lon), wiki(topic), smalltalk
    """
    txt = text.strip()

    # coordinates first
    m = COORD_RE.search(txt)
    if m:
        lat, lon = float(m.group(1)), float(m.group(2))
        return "weather_coords", (lat, lon)

    # city name (optional)
    m = CITY_RE.search(txt)
    if m:
        city = m.group(1).strip() if m.group(1) else None
        return "weather_city", (city,)

    m = WIKI_RE.search(txt)
    if m:
        topic = m.group(1).strip()
        return "wiki", (topic,)

    return "smalltalk", None

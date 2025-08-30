import requests

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

class WikiError(Exception):
    pass

def summary(topic: str) -> dict:
    slug = topic.strip().replace(" ", "_")
    url = WIKI_API + slug
    headers = {
        "accept": "application/json",
        "User-Agent": "VoiceAgent/1.0 (https://example.com; contact@example.com)"
    }
    r = requests.get(url, timeout=10, headers=headers)

    if r.status_code == 404:
        raise WikiError("I couldn't find that topic on Wikipedia.")
    if r.status_code != 200:
        raise WikiError(f"Wikipedia error: {r.status_code}")

    j = r.json()
    return {
        "title": j.get("title", topic.title()),
        "extract": j.get("extract", "No summary available."),
        "url": j.get("content_urls", {}).get("desktop", {}).get("page", "https://wikipedia.org"),
    }

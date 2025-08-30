import json
from typing import Any, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from skills.weather import fetch_by_city, fetch_by_coords, format_weather, WeatherError
from skills.wiki import summary as wiki_summary, WikiError
from utils.intent import detect

app = FastAPI(title="Day25 Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- helpers -----------------------------------------------------------------
def handle_message(text: str) -> Dict[str, Any]:
    intent, payload = detect(text)

    if intent == "weather_coords":
        lat, lon = payload # type: ignore
        data = fetch_by_coords(lat, lon)
        reply = format_weather(data)
        return {"role": "assistant", "intent": intent, "text": reply}

    if intent == "weather_city":
        (city,) = payload # type: ignore
        city = city or "Kolkata"  # default city fallback
        data = fetch_by_city(city)
        reply = format_weather(data)
        return {"role": "assistant", "intent": intent, "text": reply}

    if intent == "wiki":
        (topic,) = payload # type: ignore
        info = wiki_summary(topic)
        reply = f"{info['title']}: {info['extract']}\nMore: {info['url']}"
        return {"role": "assistant", "intent": intent, "text": reply}

    # tiny smalltalk fallback
    return {
        "role": "assistant",
        "intent": "smalltalk",
        "text": "I can fetch weather (city or lat,lon) and give quick Wikipedia facts. Try: 'weather in Mumbai' or 'weather at 22.57, 88.36' or 'who is Rabindranath Tagore'.",
    }

# --- REST (optional) ---------------------------------------------------------
@app.post("/chat")
async def chat(body: Dict[str, Any]):
    text = body.get("text", "")
    try:
        return JSONResponse(handle_message(text))
    except (WeatherError, WikiError) as e:
        return JSONResponse({"role": "assistant", "intent": "error", "text": str(e)}, status_code=400)

# --- WebSocket ---------------------------------------------------------------
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"role": "assistant", "intent": "error", "text": "Send JSON with a 'text' field."}))
                continue
            text = data.get("text", "")
            try:
                resp = handle_message(text)
            except (WeatherError, WikiError) as e:
                resp = {"role": "assistant", "intent": "error", "text": str(e)}
            await ws.send_text(json.dumps(resp))
    except WebSocketDisconnect:
        return

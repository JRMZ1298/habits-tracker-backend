from fastapi import APIRouter, Request
import random
import httpx
import os
import json
from openai import OpenAI
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import time
from openai import OpenAI
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/recommendation", tags=["recommendation"])
load_dotenv()

limiter = Limiter(key_func=get_remote_address)

# =========================
# 🔐 CONFIG
# =========================
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
else:
    client = None


# =========================
# 🧠 CACHE
# =========================
CACHE = {}
CACHE_TTL = 300  # 5 min

def get_cache(key):
    data = CACHE.get(key)
    if not data:
        return None

    value, expires = data
    if time.time() > expires:
        del CACHE[key]
        return None

    return value

def set_cache(key, value):
    CACHE[key] = (value, time.time() + CACHE_TTL)

# =========================
# 🎯 BASE
# =========================
BASE_QUERIES = [
    "meditation 15 minutes",
    "fitness 3 days",
    "hydration 2 copes",
    "reading 20 books",
    "sleep 8 hours",
]

# =========================
# 🤖 OPENROUTER
# =========================
def generate_title(base_query: str):
    cache_key = f"title:{base_query}"

    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        prompt = f"""
Genera un hábito saludable basado en: "{base_query}"

Reglas:
- Máximo 4 palabras
- En español
- Que también funcione como búsqueda de imagen

Responde SOLO en JSON:
{{
  "title": "..."
}}
"""

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)
        title = data["title"]

        set_cache(cache_key, title)
        return title

    except Exception as e:
        print("AI ERROR:", e)

        fallback = base_query  # 🔥 importante: usar query base
        set_cache(cache_key, fallback)
        return fallback

# =========================
# 📸 PEXELS (usa title)
# =========================
async def get_image(query: str):
    cache_key = f"img:{query}"

    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=5.0) as client_http:
            res = await client_http.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": query,
                    "per_page": 1,
                },
            )

            data = res.json()
            photos = data.get("photos", [])

            if photos:
                image = photos[0]["src"]["large"]
                set_cache(cache_key, image)
                return image

    except Exception as e:
        print("PEXELS ERROR:", e)

    fallback = "https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg"
    set_cache(cache_key, fallback)
    return fallback

# =========================
# 🎯 ENDPOINT
# =========================
@router.get("")
# @limiter.limit("10/minute")
async def recommendation(request: Request):
    cache_key = "recommendation"

    cached = get_cache(cache_key)
    if cached:
        return cached

    # 🎲 base
    base_query = random.choice(BASE_QUERIES)

    # 🤖 IA genera título (que será query)
    title = generate_title(base_query)

    # 📸 imagen usa el título
    image = await get_image(title)

    response = {
        "title": title,
        "image": image,
    }

    set_cache(cache_key, response)

    return response
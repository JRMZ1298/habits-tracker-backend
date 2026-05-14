from fastapi import APIRouter, Request
import random
import httpx
import json
from openai import OpenAI
from app.core.limiter import limiter
from app.core.config import settings
from app.core.cache import cache

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


PEXELS_API_KEY = settings.PEXELS_API_KEY
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY


if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
else:
    client = None


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
async def generate_title(base_query: str):
    cache_key = f"title:{base_query}"

    cached = await cache.get(cache_key)
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

        await cache.set(cache_key, title, 300)
        return title

    except Exception as e:
        print("AI ERROR:", e)

        fallback = base_query
        await cache.set(cache_key, fallback, 300)
        return fallback

# =========================
# 📸 PEXELS (usa title)
# =========================
async def get_image(query: str):
    cache_key = f"img:{query}"

    cached = await cache.get(cache_key)
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
                await cache.set(cache_key, image, 300)
                return image

    except Exception as e:
        print("PEXELS ERROR:", e)

    fallback = "https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg"
    await cache.set(cache_key, fallback, 300)
    return fallback

# =========================
# 🎯 ENDPOINT
# =========================
@router.get("")
@limiter.limit("10/minute")
async def recommendation(request: Request):
    cache_key = "recommendation"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    # 🎲 base
    base_query = random.choice(BASE_QUERIES)

    # 🤖 IA genera título (que será query)
    title = await generate_title(base_query)

    # 📸 imagen usa el título
    image = await get_image(title)

    response = {
        "title": title,
        "image": image,
    }

    await cache.set(cache_key, response, 60)

    return response
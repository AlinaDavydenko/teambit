from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY
import hashlib
import json
from app.core.redis_client import redis_client

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def ask_ai(system_prompt: str, user_message: str) -> str:
    """Send a message to OpenAI and return the response, with Redis caching"""
    # Create cache key from message content
    cache_key = (
        f"ai:{hashlib.md5(f'{system_prompt}{user_message}'.encode()).hexdigest()}"
    )

    # Check cache first
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Call OpenAI
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = "AI assistant is temporarily unavailable. Please try again later."

    # Save to cache for 1 hour
    await redis_client.setex(cache_key, 3600, json.dumps(result))

    return result

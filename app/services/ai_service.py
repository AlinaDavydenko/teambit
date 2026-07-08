from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def ask_ai(system_prompt: str, user_message: str) -> str:
    """Send a message to OpenAI and return the response"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content

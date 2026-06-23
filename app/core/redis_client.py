import redis.asyncio as redis
from app.config import REDIS_PASSWORD

redis_client = redis.Redis(
    host="redis", port=6379, password=REDIS_PASSWORD, decode_responses=True
)


async def check_con(client):
    return await client.ping()

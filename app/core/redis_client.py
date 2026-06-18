import redis
from app.config import REDIS_PASSWORD

redis_client = redis.Redis(
    host="redis",
    port=6379,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def check_con(client):
    return client.ping()
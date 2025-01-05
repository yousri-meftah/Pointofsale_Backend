from redis.asyncio import ConnectionPool
from .config import settings
from redis.asyncio.client import Redis



redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=100,
    decode_responses=True
)

async def get_redis() -> Redis:
    redis = Redis(connection_pool=redis_pool)
    try:
        await redis.ping()
        #print("Successfully connected to Redis")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
    return redis



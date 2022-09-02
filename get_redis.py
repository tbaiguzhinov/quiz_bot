import os
import redis

from dotenv import load_dotenv


def get_redis_db():
    load_dotenv()
    return redis.Redis(
        host=os.getenv('REDIS_END_POINT'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
    )

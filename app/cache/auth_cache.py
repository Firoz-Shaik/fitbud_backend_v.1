import json
import os
import uuid
from redis import Redis

from app.core.config import settings


def _make_redis() -> Redis | None:
    if os.getenv("DISABLE_AUTH_CACHE") == "1":
        return None
    if not settings.REDIS_URL:
        raise ValueError(
            "REDIS_URL is not set. Add it to your environment, or set DISABLE_AUTH_CACHE=1."
        )
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


redis_client = _make_redis()

USER_TTL = 120


class UUIDSafeEncoder(json.JSONEncoder):
    """JSON encoder that serializes UUID to string."""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


def get_cached_user(email: str):
    if redis_client is None:
        return None
    data = redis_client.get(f"user:{email}")
    return json.loads(data) if data else None


def set_cached_user(email: str, user_dict: dict):
    if redis_client is None:
        return None
    return redis_client.setex(
        f"user:{email}", USER_TTL, json.dumps(user_dict, cls=UUIDSafeEncoder)
    )

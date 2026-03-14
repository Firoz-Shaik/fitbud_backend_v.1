import json
import uuid
import os
from redis import Redis

redis_client = Redis(host="redis", port=6379, decode_responses=True)

USER_TTL = 120


class UUIDSafeEncoder(json.JSONEncoder):
    """JSON encoder that serializes UUID to string."""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


def get_cached_user(email: str):
    if os.getenv("DISABLE_AUTH_CACHE") == "1":
        return None
    data = redis_client.get(f"user:{email}")
    return json.loads(data) if data else None


def set_cached_user(email: str, user_dict: dict):
    if os.getenv("DISABLE_AUTH_CACHE") == "1":
        return None
    return redis_client.setex(
        f"user:{email}", USER_TTL, json.dumps(user_dict, cls=UUIDSafeEncoder)
    )
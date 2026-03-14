#app/domain/client_lifecycle.py
from app.domain.errors import InvalidClientState


CLIENT_STATUSES = {
    "invited",
    "active",
    "paused",
    "archived",
}

ALLOWED_TRANSITIONS = {
    "invited": {"active"},
    "active": {"paused", "archived"},
    "paused": {"active", "archived"},
    "archived": set(),
}

def assert_valid_client_transition(current: str, target: str):
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidClientState(
            f"Cannot transition client from '{current}' to '{target}'"
        )


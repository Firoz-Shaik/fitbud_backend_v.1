#app/domains/client_guards.py

from app.domain.errors import InvalidClientState
from app.domain.client_permissions import ACTION_PERMISSIONS

def assert_client_allows_action(client, action: str):
    allowed_states = ACTION_PERMISSIONS.get(action)
    if not allowed_states:
        raise InvalidClientState(f"Unknown action '{action}'")

    if client.client_status not in allowed_states:
        raise InvalidClientState(
            f"Action '{action}' not allowed when client is '{client.client_status}'"
        )

def assert_client_active(client):
    if client.client_status != "active":
        raise InvalidClientState("Client must be active")

def assert_client_modifiable(client):
    if client.client_status not in {"invited", "active"}:
        raise InvalidClientState(
            f"Client cannot be modified when status is '{client.client_status}'"
        )

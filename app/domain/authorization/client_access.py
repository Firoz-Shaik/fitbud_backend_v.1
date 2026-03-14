# app/domain/authorization/client_access.py

import uuid
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.user import User
from app.domain.errors import OwnershipViolation, ResourceNotFound


def assert_trainer_owns_client(client: Client, trainer_id: uuid.UUID) -> None:
    if client.trainer_user_id != trainer_id:
        raise OwnershipViolation("Trainer does not own this client")


def get_client_for_trainer(
    db: Session,
    *,
    client_id: uuid.UUID,
    trainer_id: uuid.UUID,
) -> Client:
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.deleted_at.is_(None),
    ).first()

    if not client:
        raise ResourceNotFound("Client not found")

    assert_trainer_owns_client(client, trainer_id)
    return client


def get_client_for_viewer(
    db: Session,
    *,
    client_id: uuid.UUID,
    current_user: User,
) -> Client:
    """
    Returns the client if the current user (trainer or client) is authorized to view it.
    - Trainer: must own the client.
    - Client: must be viewing their own client profile.
    Raises OwnershipViolation or ResourceNotFound if not authorized.
    """
    if current_user.user_role == "trainer":
        return get_client_for_trainer(db, client_id=client_id, trainer_id=current_user.id)
    elif current_user.user_role == "client":
        if not current_user.client_profile or current_user.client_profile.id != client_id:
            raise OwnershipViolation("Not authorized to view this client's data.")
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.deleted_at.is_(None),
        ).first()
        if not client:
            raise ResourceNotFound("Client not found")
        return client
    else:
        raise OwnershipViolation("User role not authorized.")


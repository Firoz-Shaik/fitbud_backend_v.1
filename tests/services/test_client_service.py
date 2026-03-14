# tests/services/test_client_service.py
# Service layer tests for client management business logic.

import pytest
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.client_service import client_service
from app.schemas.client import ClientInvite, ClientUpdate
from app.models.user import User
from app.models.client import Client
from app.domain.errors import InvalidClientState


class TestClientCreation:
    """Tests for client invitation and creation."""
    
    def test_client_creation_sets_invited_status(self, test_db: Session, test_trainer: User):
        """Creating a client invite should set status to 'invited'."""
        invite_data = ClientInvite(
            email="newclient@test.com",
            full_name="New Client",
            goal="Muscle Gain"
        )
        
        client = client_service.create_client_invite(
            db=test_db,
            obj_in=invite_data,
            trainer_id=test_trainer.id
        )
        
        assert client.client_status == "invited"
        assert client.trainer_user_id == test_trainer.id
        assert client.client_user_id is None
        assert client.invite_code is not None
        assert len(client.invite_code) == 10
    
    def test_client_invite_generates_unique_code(self, test_db: Session, test_trainer: User):
        """Each client invite should generate a unique invite code."""
        invite1 = ClientInvite(email="client1@test.com", full_name="Client 1", goal="Weight Loss")
        invite2 = ClientInvite(email="client2@test.com", full_name="Client 2", goal="Muscle Gain")
        
        client1 = client_service.create_client_invite(db=test_db, obj_in=invite1, trainer_id=test_trainer.id)
        client2 = client_service.create_client_invite(db=test_db, obj_in=invite2, trainer_id=test_trainer.id)
        
        assert client1.invite_code != client2.invite_code
    
    def test_cannot_invite_existing_client_email(self, test_db: Session, test_trainer: User, test_client_user: User, test_client_profile: Client):
        """Cannot invite a client with an email already registered."""
        invite_data = ClientInvite(
            email=test_client_user.email,
            full_name="Duplicate Client",
            goal="Weight Loss"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            client_service.create_client_invite(
                db=test_db,
                obj_in=invite_data,
                trainer_id=test_trainer.id
            )
        assert exc_info.value.status_code == 400


class TestClientLifecycle:
    """Tests for client lifecycle state transitions."""
    
    def test_valid_lifecycle_transition_invited_to_active(self, test_db: Session, test_trainer: User):
        """Valid transition from invited to active should succeed."""
        invite_data = ClientInvite(email="client@test.com", full_name="Client", goal="Weight Loss")
        client = client_service.create_client_invite(db=test_db, obj_in=invite_data, trainer_id=test_trainer.id)
        
        updated_client = client_service.update_client_status(test_db, client, "active")
        
        assert updated_client.client_status == "active"
    
    def test_invalid_lifecycle_transition_raises_error(self, test_db: Session, test_trainer: User):
        """Invalid transition should raise InvalidClientState."""
        invite_data = ClientInvite(email="client@test.com", full_name="Client", goal="Weight Loss")
        client = client_service.create_client_invite(db=test_db, obj_in=invite_data, trainer_id=test_trainer.id)
        
        with pytest.raises(InvalidClientState, match="Cannot transition"):
            client_service.update_client_status(test_db, client, "paused")
    
    def test_archived_client_cannot_transition(self, test_db: Session, test_trainer: User, test_client_profile: Client):
        """Archived clients cannot transition to any other state."""
        test_client_profile.client_status = "archived"
        test_db.commit()
        
        with pytest.raises(InvalidClientState):
            client_service.update_client_status(test_db, test_client_profile, "active")


class TestClientPermissions:
    """Tests for permission checks per client status."""
    
    def test_invited_client_cannot_checkin(self, test_db: Session, test_trainer: User):
        """Invited clients should not be able to check in."""
        from app.domain.client_guards import assert_client_allows_action
        
        invite_data = ClientInvite(email="client@test.com", full_name="Client", goal="Weight Loss")
        client = client_service.create_client_invite(db=test_db, obj_in=invite_data, trainer_id=test_trainer.id)
        
        with pytest.raises(InvalidClientState, match="not allowed when client is 'invited'"):
            assert_client_allows_action(client, "checkin")
    
    def test_active_client_can_checkin(self, test_db: Session, test_client_profile: Client):
        """Active clients should be able to check in."""
        from app.domain.client_guards import assert_client_allows_action
        
        assert_client_allows_action(test_client_profile, "checkin")
    
    def test_paused_client_can_view_logs(self, test_db: Session, test_client_profile: Client):
        """Paused clients should be able to view logs."""
        from app.domain.client_guards import assert_client_allows_action
        
        test_client_profile.client_status = "paused"
        test_db.commit()
        
        assert_client_allows_action(test_client_profile, "view_logs")


class TestClientRetrieval:
    """Tests for retrieving client data."""
    
    def test_get_client_by_id_returns_correct_client(self, test_db: Session, test_trainer: User, test_client_profile: Client):
        """Should retrieve the correct client by ID."""
        client = client_service.get_client_by_id(
            db=test_db,
            client_id=test_client_profile.id,
            trainer_id=test_trainer.id
        )
        
        assert client.id == test_client_profile.id
        assert client.trainer_user_id == test_trainer.id
    
    def test_get_client_by_id_raises_404_for_nonexistent(self, test_db: Session, test_trainer: User):
        """Should raise HTTPException for non-existent client."""
        fake_id = uuid.uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            client_service.get_client_by_id(
                db=test_db,
                client_id=fake_id,
                trainer_id=test_trainer.id
            )
        
        assert exc_info.value.status_code == 404
    
    def test_trainer_cannot_access_other_trainers_client(self, test_db: Session, test_client_profile: Client):
        """Trainer should not be able to access another trainer's client."""
        other_trainer = User(
            id=uuid.uuid4(),
            email="other@trainer.com",
            hashed_password="hash",
            full_name="Other Trainer",
            user_role="trainer"
        )
        test_db.add(other_trainer)
        test_db.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            client_service.get_client_by_id(
                db=test_db,
                client_id=test_client_profile.id,
                trainer_id=other_trainer.id
            )
        
        assert exc_info.value.status_code == 404


class TestClientUpdate:
    """Tests for updating client information."""
    
    def test_update_client_notes(self, test_db: Session, test_trainer: User, test_client_profile: Client):
        """Should successfully update client private notes."""
        new_notes = "Client prefers morning workouts"
        
        updated_client = client_service.update_client_notes(
            db=test_db,
            client_id=test_client_profile.id,
            trainer_id=test_trainer.id,
            notes=new_notes
        )
        
        assert updated_client.private_notes == new_notes
    
    def test_update_client_details(self, test_db: Session, test_client_profile: Client):
        """Should successfully update client details."""
        update_data = ClientUpdate(
            goal="Muscle Gain",
            goal_description="Build lean muscle mass"
        )
        
        updated_client = client_service.update_client(
            db=test_db,
            client=test_client_profile,
            obj_in=update_data
        )
        
        assert updated_client.goal == "Muscle Gain"
        assert updated_client.goal_description == "Build lean muscle mass"

# tests/api/test_clients.py
# API integration tests for client management endpoints.

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client


class TestCreateClient:
    """Tests for creating client invitations."""
    
    def test_create_client_invitation_sets_invited_status(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Creating a client invitation should set status to invited."""
        response = client.post(
            "/api/v1/clients/",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "email": "newclient@test.com",
                "full_name": "New Client",
                "goal": "Weight Loss"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["clientStatus"] == "invited"
        assert data["invitedEmail"] == "newclient@test.com"
        assert data["inviteCode"] is not None
    
    def test_create_client_requires_authentication(self, client: TestClient):
        """Creating a client without authentication should fail."""
        response = client.post(
            "/api/v1/clients/",
            json={
                "email": "newclient@test.com",
                "full_name": "New Client",
                "goal": "Weight Loss"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_client_requires_trainer_role(self, client: TestClient, test_client_user: User, client_token: str):
        """Creating a client with client role should fail."""
        response = client.post(
            "/api/v1/clients/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "email": "newclient@test.com",
                "full_name": "New Client",
                "goal": "Weight Loss"
            }
        )
        
        assert response.status_code == 403


class TestListClients:
    """Tests for listing clients."""
    
    def test_trainer_can_list_their_clients(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Trainer should be able to list their clients."""
        response = client.get(
            "/api/v1/clients/",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_clients_with_status_filter(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Should be able to filter clients by status."""
        response = client.get(
            "/api/v1/clients/?status=active",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        for client_data in data:
            assert client_data["clientStatus"] == "active"


class TestGetClient:
    """Tests for retrieving individual client details."""
    
    def test_trainer_can_get_their_client(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Trainer should be able to get details of their client."""
        response = client.get(
            f"/api/v1/clients/{test_client_profile.id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_client_profile.id)
    
    def test_trainer_cannot_access_other_trainers_client(self, client: TestClient, test_db: Session, test_client_profile: Client):
        """Trainer should not be able to access another trainer's client."""
        from app.core.security import get_password_hash, create_access_token
        
        # Create another trainer
        other_trainer = User(
            id=uuid.uuid4(),
            email="other@trainer.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other Trainer",
            user_role="trainer"
        )
        test_db.add(other_trainer)
        test_db.commit()
        
        other_token = create_access_token(subject=other_trainer.email)
        
        response = client.get(
            f"/api/v1/clients/{test_client_profile.id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_nonexistent_client_returns_404(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Getting a non-existent client should return 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/clients/{fake_id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 404


class TestUpdateClient:
    """Tests for updating client information."""
    
    def test_trainer_can_update_client_details(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Trainer should be able to update their client's details."""
        response = client.patch(
            f"/api/v1/clients/{test_client_profile.id}",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "goal": "Muscle Gain",
                "goal_description": "Build lean muscle"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["goal"] == "Muscle Gain"
        assert data["goalDescription"] == "Build lean muscle"
    
    def test_trainer_can_update_client_notes(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Trainer should be able to update client private notes."""
        response = client.patch(
            f"/api/v1/clients/{test_client_profile.id}/notes",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "private_notes": "Client prefers morning workouts"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["privateNotes"] == "Client prefers morning workouts"


class TestClientOwnership:
    """Tests for client ownership enforcement."""
    
    def test_ownership_enforcement_on_client_access(self, client: TestClient, test_db: Session, test_trainer: User, test_client_profile: Client):
        """Ownership should be enforced when accessing clients."""
        from app.core.security import get_password_hash, create_access_token
        
        # Create another trainer
        other_trainer = User(
            id=uuid.uuid4(),
            email="other@trainer.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other Trainer",
            user_role="trainer"
        )
        test_db.add(other_trainer)
        test_db.commit()
        
        other_token = create_access_token(subject=other_trainer.email)
        
        # Try to update another trainer's client
        response = client.patch(
            f"/api/v1/clients/{test_client_profile.id}",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"goal": "Unauthorized Update"}
        )
        
        assert response.status_code == 404


class TestClientOverview:
    """Tests for client overview endpoint."""
    
    def test_get_client_overview(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Should retrieve comprehensive client overview."""
        response = client.get(
            f"/api/v1/clients/{test_client_profile.id}/overview",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "fullName" in data
        assert "clientStatus" in data
        assert "goal" in data


class TestClientActivityFeed:
    """Tests for client activity feed endpoint."""
    
    def test_get_client_activity_feed(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Should retrieve client activity feed."""
        response = client.get(
            f"/api/v1/clients/{test_client_profile.id}/activity-feed",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

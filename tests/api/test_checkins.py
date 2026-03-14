# tests/api/test_checkins.py
# API integration tests for check-in endpoints.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client


class TestCreateCheckin:
    """Tests for creating check-ins."""
    
    def test_client_creates_checkin(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Client should be able to create a check-in."""
        response = client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "weight_kg": 75.5,
                "notes": "Feeling great this week!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert float(data["weightKg"]) == 75.5
        assert data["notes"] == "Feeling great this week!"
        assert data["clientId"] == str(test_client_profile.id)
    
    def test_checkin_requires_authentication(self, client: TestClient):
        """Creating a check-in without authentication should fail."""
        response = client.post(
            "/api/v1/checkins/",
            json={"weight_kg": 75.0, "notes": "Test"}
        )
        
        assert response.status_code == 401
    
    def test_trainer_cannot_create_client_checkin(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Trainer should not be able to create check-ins for clients."""
        response = client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={"weight_kg": 75.0, "notes": "Test"}
        )
        
        assert response.status_code == 403


class TestListCheckins:
    """Tests for listing check-ins."""
    
    def test_client_can_list_their_checkins(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Client should be able to list their own check-ins."""
        # Create a check-in first
        client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"weight_kg": 75.0, "notes": "Test"}
        )
        
        response = client.get(
            f"/api/v1/checkins/?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_trainer_can_view_client_checkins(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_user: User, client_token: str, test_client_profile: Client):
        """Trainer should be able to view their client's check-ins."""
        # Client creates check-in
        client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"weight_kg": 75.0, "notes": "Test"}
        )
        
        # Trainer views check-ins
        response = client.get(
            f"/api/v1/checkins/?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestCheckinOwnership:
    """Tests for check-in ownership enforcement."""
    
    def test_client_cannot_view_other_client_checkins(self, client: TestClient, test_db: Session, test_trainer: User, test_client_user: User, client_token: str):
        """Client should not be able to view another client's check-ins."""
        import uuid
        from app.core.security import get_password_hash, create_access_token
        
        # Create another client
        other_client_user = User(
            id=uuid.uuid4(),
            email="other@client.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other Client",
            user_role="client"
        )
        test_db.add(other_client_user)
        test_db.commit()
        
        other_client_profile = Client(
            id=uuid.uuid4(),
            trainer_user_id=test_trainer.id,
            client_user_id=other_client_user.id,
            client_status="active"
        )
        test_db.add(other_client_profile)
        test_db.commit()
        
        # Try to view other client's check-ins
        response = client.get(
            f"/api/v1/checkins/?client_id={other_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 403


class TestCheckinDateFiltering:
    """Tests for filtering check-ins by date."""
    
    def test_filter_checkins_by_date_range(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Should be able to filter check-ins by date range."""
        from datetime import datetime, timedelta
        
        # Create check-in
        client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"weight_kg": 75.0, "notes": "Test"}
        )
        
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = client.get(
            f"/api/v1/checkins/?client_id={test_client_profile.id}&start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
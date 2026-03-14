# tests/api/test_auth.py
# API integration tests for authentication endpoints.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestLogin:
    """Tests for login endpoint."""
    
    def test_login_success_returns_token(self, client: TestClient, test_trainer: User):
        """Successful login should return access token."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "trainer@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data  # camelCase
        assert data["tokenType"] == "bearer"  # camelCase
    
    def test_login_with_invalid_credentials_fails(self, client: TestClient, test_trainer: User):
        """Login with wrong password should fail."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "trainer@test.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_with_nonexistent_user_fails(self, client: TestClient):
        """Login with non-existent email should fail."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestProtectedRoutes:
    """Tests for authentication requirement on protected routes."""
    
    def test_protected_route_requires_auth(self, client: TestClient):
        """Accessing protected route without token should return 401."""
        response = client.get("/api/v1/auth/users/me")
        
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token_succeeds(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Accessing protected route with valid token should succeed."""
        response = client.get(
            "/api/v1/auth/users/me",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "trainer@test.com"
        assert data["userRole"] == "trainer"  # camelCase
    
    def test_protected_route_with_invalid_token_fails(self, client: TestClient):
        """Accessing protected route with invalid token should return 401."""
        response = client.get(
            "/api/v1/auth/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestRoleEnforcement:
    """Tests for role-based access control."""
    
    def test_trainer_only_endpoint_rejects_client(self, client: TestClient, test_client_user: User, client_token: str):
        """Trainer-only endpoints should reject client users."""
        response = client.get(
            "/api/v1/clients/",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 403
    
    def test_trainer_only_endpoint_accepts_trainer(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer-only endpoints should accept trainer users."""
        response = client.get(
            "/api/v1/clients/",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
    
    def test_client_only_endpoint_rejects_trainer(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile):
        """Client-only endpoints should reject trainer users."""
        response = client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={"weightKg": 75.0, "notes": "Test"}  # camelCase
        )
        
        assert response.status_code == 403
    
    def test_client_only_endpoint_accepts_client(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile):
        """Client-only endpoints should accept client users."""
        response = client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"weight_kg": 75.0, "notes": "Test"}  # camelCase
        )
        
        assert response.status_code == 201


class TestClientRegistration:
    """Tests for client registration with invite code."""
    
    def test_client_registration_with_valid_invite_code(self, client: TestClient, test_db: Session, test_trainer: User):
        """Client should be able to register with valid invite code."""
        from app.services.client_service import client_service
        from app.schemas.client import ClientInvite
        
        # Create invite
        invite_data = ClientInvite(
            email="newclient@test.com",
            full_name="New Client",
            goal="Weight Loss"
        )
        invited_client = client_service.create_client_invite(
            db=test_db,
            obj_in=invite_data,
            trainer_id=test_trainer.id
        )
        
        # Register with invite code (using camelCase)
        response = client.post(
            "/api/v1/auth/register/client",
            json={
                "email": "newclient@test.com",
                "password": "newpassword123",
                "fullName": "New Client",  # camelCase
                "inviteCode": invited_client.invite_code  # camelCase
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newclient@test.com"
        assert data["userRole"] == "client"  # camelCase
    
    def test_client_registration_with_invalid_invite_code_fails(self, client: TestClient):
        """Client registration with invalid invite code should fail."""
        response = client.post(
            "/api/v1/auth/register/client",
            json={
                "email": "newclient@test.com",
                "password": "password123",
                "fullName": "New Client",  # camelCase
                "inviteCode": "INVALID_CODE"  # camelCase
            }
        )
        
        assert response.status_code == 400  # Service raises ValueError

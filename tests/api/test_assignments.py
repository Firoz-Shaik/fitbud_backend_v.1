# tests/api/test_assignments.py
# API integration tests for plan assignment endpoints.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client
from app.models.template import ExerciseLibrary, FoodItemLibrary


class TestAssignWorkoutPlan:
    """Tests for assigning workout plans via API."""
    
    def test_trainer_assigns_workout_plan_to_client(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_profile: Client, test_exercise: ExerciseLibrary):
        """Trainer should be able to assign workout plan to their client."""
        # Create template first
        template_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Strength Program",
                "description": "Build strength",
                "items": [
                    {
                        "exercise_id": str(test_exercise.id),
                        "day_name": "Monday",
                        "target_sets": "4",
                        "target_reps": "8",
                        "display_order": 1
                    }
                ]
            }
        )
        template_id = template_response.json()["id"]
        
        # Assign to client
        response = client.post(
            "/api/v1/assigned-plans/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["clientId"] == str(test_client_profile.id)
        assert data["sourceTemplateId"] == template_id
        assert "planDetails" in data
    
    def test_assign_workout_requires_authentication(self, client: TestClient, test_client_profile: Client):
        """Assigning workout plan without authentication should fail."""
        response = client.post(
            "/api/v1/assigned-plans/workout",
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": "fake-id"
            }
        )
        
        assert response.status_code == 401
    
    def test_assign_workout_requires_trainer_role(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Assigning workout plan with client role should fail."""
        response = client.post(
            "/api/v1/assigned-plans/workout",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": "fake-id"
            }
        )
        
        assert response.status_code == 403


class TestAssignDietPlan:
    """Tests for assigning diet plans via API."""
    
    def test_trainer_assigns_diet_plan_to_client(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_profile: Client, test_food_item: FoodItemLibrary):
        """Trainer should be able to assign diet plan to their client."""
        # Create template first
        template_response = client.post(
            "/api/v1/templates/diet",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "High Protein",
                "description": "Protein diet",
                "items": [
                    {
                        "food_item_id": str(test_food_item.id),
                        "meal_name": "Breakfast",
                        "serving": {"size": 150, "unit": "g"},
                        "display_order": 1
                    }
                ]
            }
        )
        template_id = template_response.json()["id"]
        
        # Assign to client
        response = client.post(
            "/api/v1/assigned-plans/diet",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["clientId"] == str(test_client_profile.id)
        assert "planDetails" in data


class TestListAssignedPlans:
    """Tests for listing assigned plans."""
    
    def test_get_client_assigned_workout_plans(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Should retrieve assigned workout plans for a client."""
        response = client.get(
            f"/api/v1/assigned-plans/workout?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_client_can_view_their_assigned_plans(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Client should be able to view their own assigned plans."""
        response = client.get(
            f"/api/v1/assigned-plans/workout?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200


class TestAssignmentOwnership:
    """Tests for ownership enforcement in assignments."""
    
    def test_trainer_cannot_assign_to_other_trainers_client(self, client: TestClient, test_db: Session, test_trainer: User, test_exercise: ExerciseLibrary):
        """Trainer should not be able to assign plans to another trainer's client."""
        import uuid
        from app.core.security import get_password_hash, create_access_token
        
        # Create another trainer and their client
        other_trainer = User(
            id=uuid.uuid4(),
            email="other@trainer.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other Trainer",
            user_role="trainer"
        )
        test_db.add(other_trainer)
        test_db.commit()
        
        other_client = Client(
            id=uuid.uuid4(),
            trainer_user_id=other_trainer.id,
            client_status="active"
        )
        test_db.add(other_client)
        test_db.commit()
        
        other_token = create_access_token(subject=other_trainer.email)
        
        # Create template for test_trainer
        template_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {other_token}"},
            json={
                "name": "Plan",
                "description": "Test",
                "items": [
                    {
                        "exercise_id": str(test_exercise.id),
                        "day_name": "Monday",
                        "target_sets": "3",
                        "target_reps": "10",
                        "display_order": 1
                    }
                ]
            }
        )
        template_id = template_response.json()["id"]
        
        # Try to assign to other trainer's client (using test_trainer's token)
        from app.core.security import create_access_token
        test_trainer_token = create_access_token(subject=test_trainer.email)
        
        response = client.post(
            "/api/v1/assigned-plans/workout",
            headers={"Authorization": f"Bearer {test_trainer_token}"},
            json={
                "client_id": str(other_client.id),
                "source_template_id": template_id
            }
        )
        
        assert response.status_code in [403, 404]

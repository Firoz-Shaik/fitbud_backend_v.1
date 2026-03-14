# tests/api/test_templates.py
# API integration tests for template management endpoints.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.template import ExerciseLibrary, FoodItemLibrary


class TestCreateWorkoutTemplate:
    """Tests for creating workout templates via API."""
    
    def test_trainer_creates_workout_template(self, client: TestClient, test_trainer: User, trainer_token: str, test_exercise: ExerciseLibrary):
        """Trainer should be able to create a workout template."""
        response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Beginner Strength",
                "description": "Basic strength training",
                "items": [
                    {
                        "exercise_id": str(test_exercise.id),
                        "day_name": "Monday",
                        "target_sets": "3",
                        "target_reps": "10",
                        "rest_period_seconds": 90,
                        "display_order": 1
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Beginner Strength"
        assert len(data["items"]) == 1
    
    def test_create_workout_template_requires_authentication(self, client: TestClient, test_exercise: ExerciseLibrary):
        """Creating workout template without authentication should fail."""
        response = client.post(
            "/api/v1/templates/workout",
            json={
                "name": "Test",
                "description": "Test",
                "items": []
            }
        )
        
        assert response.status_code == 401
    
    def test_create_workout_template_requires_trainer_role(self, client: TestClient, test_client_user: User, client_token: str):
        """Creating workout template with client role should fail."""
        response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "name": "Test",
                "description": "Test",
                "items": []
            }
        )
        
        assert response.status_code == 403


class TestCreateDietTemplate:
    """Tests for creating diet templates via API."""
    
    def test_trainer_creates_diet_template(self, client: TestClient, test_trainer: User, trainer_token: str, test_food_item: FoodItemLibrary):
        """Trainer should be able to create a diet template."""
        response = client.post(
            "/api/v1/templates/diet",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "High Protein Diet",
                "description": "Protein-focused meal plan",
                "items": [
                    {
                        "food_item_id": str(test_food_item.id),
                        "meal_name": "Breakfast",
                        "serving": {"size": 200, "unit": "g"},
                        "display_order": 1
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "High Protein Diet"
        assert len(data["items"]) == 1


class TestListTemplates:
    """Tests for listing templates."""
    
    def test_trainer_lists_their_workout_templates(self, client: TestClient, test_trainer: User, trainer_token: str, test_exercise: ExerciseLibrary):
        """Trainer should be able to list their workout templates."""
        # Create a template first
        client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Test Template",
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
        
        response = client.get(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_trainer_lists_their_diet_templates(self, client: TestClient, test_trainer: User, trainer_token: str, test_food_item: FoodItemLibrary):
        """Trainer should be able to list their diet templates."""
        # Create a template first
        client.post(
            "/api/v1/templates/diet",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Test Diet",
                "description": "Test",
                "items": [
                    {
                        "food_item_id": str(test_food_item.id),
                        "meal_name": "Breakfast",
                        "serving": {"size": 100, "unit": "g"},
                        "display_order": 1
                    }
                ]
            }
        )
        
        response = client.get(
            "/api/v1/templates/diet",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestGetTemplate:
    """Tests for retrieving individual templates."""
    
    def test_get_workout_template_by_id(self, client: TestClient, test_trainer: User, trainer_token: str, test_exercise: ExerciseLibrary):
        """Should retrieve workout template by ID."""
        # Create template
        create_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Test Template",
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
        template_id = create_response.json()["id"]
        
        # Get template
        response = client.get(
            f"/api/v1/templates/workout/{template_id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id


class TestUpdateTemplate:
    """Tests for updating templates."""
    
    def test_update_workout_template(self, client: TestClient, test_trainer: User, trainer_token: str, test_exercise: ExerciseLibrary):
        """Trainer should be able to update their workout template."""
        # Create template
        create_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Original",
                "description": "Original description",
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
        template_id = create_response.json()["id"]
        
        # Update template
        response = client.put(
            f"/api/v1/templates/workout/{template_id}",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Updated",
                "description": "Updated description",
                "items": [
                    {
                        "exercise_id": str(test_exercise.id),
                        "day_name": "Tuesday",
                        "target_sets": "4",
                        "target_reps": "12",
                        "display_order": 1
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"


class TestDeleteTemplate:
    """Tests for deleting templates."""
    
    def test_delete_workout_template(self, client: TestClient, test_trainer: User, trainer_token: str, test_exercise: ExerciseLibrary):
        """Trainer should be able to delete their workout template."""
        # Create template
        create_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "To Delete",
                "description": "Will be deleted",
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
        template_id = create_response.json()["id"]
        
        # Delete template
        response = client.delete(
            f"/api/v1/templates/workout/{template_id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 204


class TestTemplateOwnership:
    """Tests for template ownership enforcement."""
    
    def test_trainer_cannot_access_other_trainers_template(self, client: TestClient, test_db: Session, test_trainer: User, test_exercise: ExerciseLibrary):
        """Trainer should not be able to access another trainer's template."""
        import uuid
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
        
        # Other trainer creates template
        create_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {other_token}"},
            json={
                "name": "Other's Template",
                "description": "Not accessible",
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
        template_id = create_response.json()["id"]
        
        # Test trainer tries to access it
        test_trainer_token = create_access_token(subject=test_trainer.email)
        response = client.get(
            f"/api/v1/templates/workout/{template_id}",
            headers={"Authorization": f"Bearer {test_trainer_token}"}
        )
        
        assert response.status_code == 404

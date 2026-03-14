# tests/api/test_library.py
# API integration tests for exercise and food item library endpoints.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestExerciseLibrary:
    """Tests for exercise library endpoints."""
    
    def test_trainer_creates_exercise(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to create an exercise."""
        response = client.post(
            "/api/v1/library/exercises",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Squat",
                "description": "Leg exercise",
                "muscle_group": "Legs"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Squat"
        assert data["description"] == "Leg exercise"
    
    def test_create_exercise_requires_authentication(self, client: TestClient):
        """Creating exercise without authentication should fail."""
        response = client.post(
            "/api/v1/library/exercises",
            json={
                "name": "Squat",
                "description": "Leg exercise"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_exercise_requires_trainer_role(self, client: TestClient, test_client_user: User, client_token: str):
        """Creating exercise with client role should fail."""
        response = client.post(
            "/api/v1/library/exercises",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "name": "Squat",
                "description": "Leg exercise"
            }
        )
        
        assert response.status_code == 403
    
    def test_trainer_lists_exercises(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to list exercises."""
        response = client.get(
            "/api/v1/library/exercises",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_trainer_updates_their_exercise(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to update their own exercise."""
        # Create exercise
        create_response = client.post(
            "/api/v1/library/exercises",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Original Exercise",
                "description": "Original description"
            }
        )
        exercise_id = create_response.json()["id"]
        
        # Update exercise
        response = client.put(
            f"/api/v1/library/exercises/{exercise_id}",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Updated Exercise",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Exercise"
    
    def test_trainer_deletes_their_exercise(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to delete their own exercise."""
        # Create exercise
        create_response = client.post(
            "/api/v1/library/exercises",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "To Delete",
                "description": "Will be deleted"
            }
        )
        exercise_id = create_response.json()["id"]
        
        # Delete exercise
        response = client.delete(
            f"/api/v1/library/exercises/{exercise_id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 204
    
    def test_trainer_cannot_update_other_trainers_exercise(self, client: TestClient, test_db: Session, test_trainer: User):
        """Trainer should not be able to update another trainer's exercise."""
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
        
        # Other trainer creates exercise
        create_response = client.post(
            "/api/v1/library/exercises",
            headers={"Authorization": f"Bearer {other_token}"},
            json={
                "name": "Other's Exercise",
                "description": "Not accessible"
            }
        )
        exercise_id = create_response.json()["id"]
        
        # Test trainer tries to update it
        test_trainer_token = create_access_token(subject=test_trainer.email)
        response = client.put(
            f"/api/v1/library/exercises/{exercise_id}",
            headers={"Authorization": f"Bearer {test_trainer_token}"},
            json={
                "name": "Unauthorized Update",
                "description": "Should fail"
            }
        )
        
        assert response.status_code == 403


class TestFoodItemLibrary:
    """Tests for food item library endpoints."""
    
    def test_trainer_creates_food_item(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to create a food item."""
        response = client.post(
            "/api/v1/library/food-items",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Brown Rice",
                "base_unit_type": "MASS",
                "calories_per_100g": 112,
                "protein_per_100g": 2.6,
                "carbs_per_100g": 23.5,
                "fat_per_100g": 0.9
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Brown Rice"
        # Pydantic's camelCase conversion for `calories_per_100g` becomes `caloriesPer100G`.
        assert data.get("caloriesPer100g") == 112 or data.get("caloriesPer100G") == 112
    
    def test_create_food_item_requires_authentication(self, client: TestClient):
        """Creating food item without authentication should fail."""
        response = client.post(
            "/api/v1/library/food-items",
            json={
                "name": "Brown Rice",
                "base_unit_type": "MASS",
                "calories_per_100g": 112
            }
        )
        
        assert response.status_code == 401
    
    def test_trainer_lists_food_items(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to list food items."""
        response = client.get(
            "/api/v1/library/food-items",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_trainer_updates_their_food_item(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to update their own food item."""
        # Create food item
        create_response = client.post(
            "/api/v1/library/food-items",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Original Food",
                "base_unit_type": "MASS",
                "calories_per_100g": 100,
                "protein_per_100g": 10.0,
                "carbs_per_100g": 20.0,
                "fat_per_100g": 5.0
            }
        )
        food_item_id = create_response.json()["id"]
        
        # Update food item
        response = client.put(
            f"/api/v1/library/food-items/{food_item_id}",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Updated Food",
                "calories_per_100g": 120
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Food"
    
    def test_trainer_deletes_their_food_item(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should be able to delete their own food item."""
        # Create food item
        create_response = client.post(
            "/api/v1/library/food-items",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "To Delete",
                "base_unit_type": "MASS",
                "calories_per_100g": 100,
                "protein_per_100g": 10.0,
                "carbs_per_100g": 20.0,
                "fat_per_100g": 5.0
            }
        )
        food_item_id = create_response.json()["id"]
        
        # Delete food item
        response = client.delete(
            f"/api/v1/library/food-items/{food_item_id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 204

# tests/api/test_logs.py
# API integration tests for workout and diet logging endpoints.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client
from app.models.template import ExerciseLibrary, FoodItemLibrary


class TestWorkoutLogging:
    """Tests for workout logging endpoints."""
    
    def test_client_logs_workout(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_user: User, client_token: str, test_client_profile: Client, test_exercise: ExerciseLibrary):
        """Client should be able to log a workout."""
        # Create and assign workout plan first
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
        
        assignment_response = client.post(
            "/api/v1/assigned-plans/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        assigned_plan_id = assignment_response.json()["id"]
        
        # Log workout
        response = client.post(
            "/api/v1/logs/workout",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "assigned_plan_id": assigned_plan_id,
                "performance_data": {
                    "exercise_id": str(test_exercise.id),
                    "sets_completed": 4,
                    "reps_completed": "8,8,8,8",
                    "notes": "Felt strong today",
                },
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["performanceData"]["sets_completed"] == 4
        assert data["performanceData"]["notes"] == "Felt strong today"
    
    def test_workout_logging_requires_authentication(self, client: TestClient):
        """Logging workout without authentication should fail."""
        response = client.post(
            "/api/v1/logs/workout",
            json={
                "assigned_plan_id": "fake-id",
                "performance_data": {"sets_completed": 3, "reps_completed": "10,10,10"},
            },
        )
        
        assert response.status_code == 401
    
    def test_trainer_cannot_log_workout(self, client: TestClient, test_trainer: User, trainer_token: str):
        """Trainer should not be able to log workouts."""
        response = client.post(
            "/api/v1/logs/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "assigned_plan_id": "fake-id",
                "performance_data": {"sets_completed": 3, "reps_completed": "10,10,10"},
            },
        )
        
        assert response.status_code == 403


class TestDietLogging:
    """Tests for diet logging endpoints."""
    
    def test_client_logs_meal(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_user: User, client_token: str, test_client_profile: Client, test_food_item: FoodItemLibrary):
        """Client should be able to log a meal."""
        # Create and assign diet plan first
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
        
        assignment_response = client.post(
            "/api/v1/assigned-plans/diet",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        assigned_plan_id = assignment_response.json()["id"]
        
        # Log meal
        response = client.post(
            "/api/v1/logs/diet",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "assigned_plan_id": assigned_plan_id,
                "meal_name": "Breakfast",
                "status": "Followed",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["mealName"] == "Breakfast"
        assert data["status"] == "Followed"
    
    def test_diet_logging_requires_authentication(self, client: TestClient):
        """Logging meal without authentication should fail."""
        response = client.post(
            "/api/v1/logs/diet",
            json={
                "assigned_plan_id": "fake-id",
                "meal_name": "Lunch",
                "status": "Followed",
            },
        )
        
        assert response.status_code == 401


class TestListLogs:
    """Tests for listing workout and diet logs."""
    
    def test_client_lists_their_workout_logs(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Client should be able to list their workout logs."""
        response = client.get(
            f"/api/v1/logs/workout?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_trainer_views_client_workout_logs(self, client: TestClient, test_trainer: User, trainer_token: str, test_client_profile: Client):
        """Trainer should be able to view their client's workout logs."""
        response = client.get(
            f"/api/v1/logs/workout?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_client_lists_their_diet_logs(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Client should be able to list their diet logs."""
        response = client.get(
            f"/api/v1/logs/diet?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_filter_logs_by_date_range(self, client: TestClient, test_client_user: User, client_token: str, test_client_profile: Client):
        """Should be able to filter logs by date range."""
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = client.get(
            f"/api/v1/logs/workout?client_id={test_client_profile.id}&start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == 200

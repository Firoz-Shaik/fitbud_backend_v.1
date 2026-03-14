# tests/workflows/test_trainer_client_flow.py
# End-to-end workflow tests for trainer-client interactions.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.template import ExerciseLibrary, FoodItemLibrary


class TestTrainerClientOnboardingFlow:
    """End-to-end test for trainer inviting client and client registration."""
    
    def test_complete_trainer_client_onboarding_workflow(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str):
        """
        Complete workflow:
        1. Trainer invites client
        2. Client registers with invite code
        3. Client becomes active
        4. Client can create check-in
        """
        # Step 1: Trainer invites client
        invite_response = client.post(
            "/api/v1/clients/",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "email": "newclient@test.com",
                "full_name": "New Client",
                "goal": "Weight Loss"
            }
        )
        
        assert invite_response.status_code == 201
        invite_data = invite_response.json()
        assert invite_data["clientStatus"] == "invited"
        invite_code = invite_data["inviteCode"]
        client_id = invite_data["id"]
        
        # Step 2: Client registers with invite code
        register_response = client.post(
            "/api/v1/auth/register/client",
            json={
                "email": "newclient@test.com",
                "password": "clientpassword123",
                "full_name": "New Client",
                "invite_code": invite_code
            }
        )
        
        assert register_response.status_code == 200
        
        # Step 3: Trainer activates client
        activate_response = client.patch(
            f"/api/v1/clients/{client_id}",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={"client_status": "active"}
        )
        
        assert activate_response.status_code == 200
        assert activate_response.json()["clientStatus"] == "active"
        
        # Step 4: Client logs in
        login_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "newclient@test.com",
                "password": "clientpassword123"
            }
        )
        
        assert login_response.status_code == 200
        client_token = login_response.json()["accessToken"]
        
        # Step 5: Client creates check-in
        checkin_response = client.post(
            "/api/v1/checkins/",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "weight_kg": 75.0,
                "notes": "First check-in!"
            }
        )
        
        assert checkin_response.status_code == 201
        checkin_data = checkin_response.json()
        # weightKg is serialized from Decimal, so it's a string in JSON
        assert float(checkin_data["weightKg"]) == 75.0


class TestWorkoutPlanAssignmentFlow:
    """End-to-end test for workout plan creation, assignment, and logging."""
    
    def test_complete_workout_plan_workflow(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_user: User, client_token: str, test_client_profile, test_exercise: ExerciseLibrary):
        """
        Complete workflow:
        1. Trainer creates workout template
        2. Trainer assigns template to client
        3. Client views assigned plan
        4. Client logs workout
        """
        # Step 1: Trainer creates workout template
        template_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Beginner Strength",
                "description": "Basic strength program",
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
        
        assert template_response.status_code == 201
        template_id = template_response.json()["id"]
        
        # Step 2: Trainer assigns template to client
        assignment_response = client.post(
            "/api/v1/assigned-plans/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        
        assert assignment_response.status_code == 201
        assigned_plan_id = assignment_response.json()["id"]
        
        # Step 3: Client views assigned plan
        view_response = client.get(
            f"/api/v1/assigned-plans/workout?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert view_response.status_code == 200
        plans = view_response.json()
        assert len(plans) >= 1
        assert plans[0]["id"] == assigned_plan_id
        
        # Step 4: Client logs workout
        log_response = client.post(
            "/api/v1/logs/workout",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "assigned_plan_id": assigned_plan_id,
                "performance_data": {
                    "exercise_id": str(test_exercise.id),
                    "sets_completed": 3,
                    "reps_completed": "10,10,10",
                    "notes": "Felt strong today",
                },
            }
        )
        
        assert log_response.status_code == 201


class TestDietPlanAssignmentFlow:
    """End-to-end test for diet plan creation and assignment."""
    
    def test_complete_diet_plan_workflow(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_user: User, client_token: str, test_client_profile, test_food_item: FoodItemLibrary):
        """
        Complete workflow:
        1. Trainer creates diet template
        2. Trainer assigns template to client
        3. Client views assigned diet plan
        4. Client logs meal
        """
        # Step 1: Trainer creates diet template
        template_response = client.post(
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
        
        assert template_response.status_code == 201
        template_id = template_response.json()["id"]
        
        # Step 2: Trainer assigns template to client
        assignment_response = client.post(
            "/api/v1/assigned-plans/diet",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        
        assert assignment_response.status_code == 201
        assigned_plan_id = assignment_response.json()["id"]
        
        # Step 3: Client views assigned diet plan
        view_response = client.get(
            f"/api/v1/assigned-plans/diet?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert view_response.status_code == 200
        plans = view_response.json()
        assert len(plans) >= 1
        
        # Step 4: Client logs meal
        log_response = client.post(
            "/api/v1/logs/diet",
            headers={"Authorization": f"Bearer {client_token}"},
            json={
                "assigned_plan_id": assigned_plan_id,
                "meal_name": "Breakfast",
                "status": "Followed",
            }
        )
        
        assert log_response.status_code == 201


class TestTemplateUpdateDoesNotAffectAssignedPlans:
    """Test that updating a template doesn't affect already assigned plans."""
    
    def test_template_update_snapshot_isolation(self, client: TestClient, test_db: Session, test_trainer: User, trainer_token: str, test_client_profile, test_exercise: ExerciseLibrary):
        """
        Workflow:
        1. Trainer creates template
        2. Trainer assigns to client
        3. Trainer updates template
        4. Verify assigned plan remains unchanged
        """
        # Step 1: Create template
        template_response = client.post(
            "/api/v1/templates/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Original Plan",
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
        template_id = template_response.json()["id"]
        
        # Step 2: Assign to client
        assignment_response = client.post(
            "/api/v1/assigned-plans/workout",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "client_id": str(test_client_profile.id),
                "source_template_id": template_id
            }
        )
        assigned_plan = assignment_response.json()
        original_plan_name = assigned_plan["planDetails"]["name"]
        
        # Step 3: Update template
        update_response = client.put(
            f"/api/v1/templates/workout/{template_id}",
            headers={"Authorization": f"Bearer {trainer_token}"},
            json={
                "name": "Modified Plan",
                "description": "Modified description",
                "items": [
                    {
                        "exercise_id": str(test_exercise.id),
                        "day_name": "Tuesday",
                        "target_sets": "5",
                        "target_reps": "5",
                        "display_order": 1
                    }
                ]
            }
        )
        
        assert update_response.status_code == 200
        
        # Step 4: Verify assigned plan unchanged by re-listing assigned plans
        view_response = client.get(
            f"/api/v1/assigned-plans/workout?client_id={test_client_profile.id}",
            headers={"Authorization": f"Bearer {trainer_token}"}
        )
        assert view_response.status_code == 200
        plans = view_response.json()
        # Find the plan we just assigned
        current_plan = next(p for p in plans if p["id"] == assigned_plan["id"])
        assert current_plan["planDetails"]["name"] == original_plan_name
        assert current_plan["planDetails"]["items"][0]["targets"]["sets"] == "3"

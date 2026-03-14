# tests/services/test_assignment_service.py
# Service layer tests for plan assignment business logic.

import pytest
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.assigned_plan_service import assigned_plan_service
from app.services.template_service import template_service
from app.schemas.assigned_plan import WorkoutPlanAssign, DietPlanAssign
from app.schemas.template import (
    WorkoutPlanTemplateCreate,
    WorkoutTemplateItemCreate,
    DietPlanTemplateCreate,
    DietTemplateItemCreate,
    Serving
)
from app.models.user import User
from app.models.client import Client
from app.models.template import ExerciseLibrary, FoodItemLibrary
from app.models.plan import AssignedWorkoutPlan


class TestWorkoutPlanAssignment:
    """Tests for assigning workout plans to clients."""
    
    def test_assign_workout_plan_creates_snapshot(self, test_db: Session, test_trainer: User, test_client_profile: Client, test_exercise: ExerciseLibrary):
        """Assigning a workout plan should create an immutable snapshot."""
        # Create template
        template_data = WorkoutPlanTemplateCreate(
            name="Strength Program",
            description="Build strength",
            items=[
                WorkoutTemplateItemCreate(
                    exercise_id=test_exercise.id,
                    day_name="Monday",
                    target_sets="4",
                    target_reps="8",
                    display_order=1
                )
            ]
        )
        template = template_service.create_workout_template(
            db=test_db,
            obj_in=template_data,
            trainer_id=test_trainer.id
        )
        
        # Assign to client
        assignment = WorkoutPlanAssign(
            client_id=test_client_profile.id,
            source_template_id=template.id
        )
        
        assigned_plan = assigned_plan_service.assign_workout_plan(
            db=test_db,
            assignment_in=assignment,
            trainer_id=test_trainer.id
        )
        
        assert assigned_plan.client_id == test_client_profile.id
        assert assigned_plan.source_template_id == template.id
        assert assigned_plan.plan_details is not None
        assert assigned_plan.plan_details["name"] == "Strength Program"
    
    def test_snapshot_unaffected_by_template_changes(self, test_db: Session, test_trainer: User, test_client_profile: Client, test_exercise: ExerciseLibrary):
        """Assigned plan snapshot should remain unchanged when template is modified."""
        # Create and assign template
        template_data = WorkoutPlanTemplateCreate(
            name="Original Plan",
            description="Original description",
            items=[
                WorkoutTemplateItemCreate(
                    exercise_id=test_exercise.id,
                    day_name="Monday",
                    target_sets="3",
                    target_reps="10",
                    display_order=1
                )
            ]
        )
        template = template_service.create_workout_template(
            db=test_db,
            obj_in=template_data,
            trainer_id=test_trainer.id
        )
        
        assignment = WorkoutPlanAssign(
            client_id=test_client_profile.id,
            source_template_id=template.id
        )
        assigned_plan = assigned_plan_service.assign_workout_plan(
            db=test_db,
            assignment_in=assignment,
            trainer_id=test_trainer.id
        )
        
        original_snapshot = assigned_plan.plan_details.copy()
        
        # Update template
        from app.schemas.template import WorkoutPlanTemplateUpdate
        update_data = WorkoutPlanTemplateUpdate(
            name="Modified Plan",
            description="Modified description",
            items=[
                WorkoutTemplateItemCreate(
                    exercise_id=test_exercise.id,
                    day_name="Tuesday",
                    target_sets="5",
                    target_reps="5",
                    display_order=1
                )
            ]
        )
        template_service.update_workout_template(
            db=test_db,
            template=template,
            obj_in=update_data
        )
        
        # Refresh assigned plan and verify snapshot unchanged
        test_db.refresh(assigned_plan)
        assert assigned_plan.plan_details["name"] == "Original Plan"
        assert assigned_plan.plan_details["items"][0]["targets"]["sets"] == "3"
    
    def test_assign_to_non_active_client_fails(self, test_db: Session, test_trainer: User, test_exercise: ExerciseLibrary):
        """Cannot assign workout plan to non-active client."""
        from app.services.client_service import client_service
        from app.schemas.client import ClientInvite
        from app.domain.errors import InvalidClientState
        
        # Create invited client
        invite_data = ClientInvite(email="invited@test.com", full_name="Invited", goal="Weight Loss")
        invited_client = client_service.create_client_invite(db=test_db, obj_in=invite_data, trainer_id=test_trainer.id)
        
        # Create template
        template_data = WorkoutPlanTemplateCreate(
            name="Plan",
            description="Test",
            items=[
                WorkoutTemplateItemCreate(
                    exercise_id=test_exercise.id,
                    day_name="Monday",
                    target_sets="3",
                    target_reps="10",
                    display_order=1
                )
            ]
        )
        template = template_service.create_workout_template(db=test_db, obj_in=template_data, trainer_id=test_trainer.id)
        
        assignment = WorkoutPlanAssign(
            client_id=invited_client.id,
            source_template_id=template.id
        )
        
        with pytest.raises(InvalidClientState):
            assigned_plan_service.assign_workout_plan(
                db=test_db,
                assignment_in=assignment,
                trainer_id=test_trainer.id
            )


class TestDietPlanAssignment:
    """Tests for assigning diet plans to clients."""
    
    def test_assign_diet_plan_creates_snapshot(self, test_db: Session, test_trainer: User, test_client_profile: Client, test_food_item: FoodItemLibrary):
        """Assigning a diet plan should create an immutable snapshot."""
        # Create template
        template_data = DietPlanTemplateCreate(
            name="High Protein",
            description="Protein diet",
            items=[
                DietTemplateItemCreate(
                    food_item_id=test_food_item.id,
                    meal_name="Breakfast",
                    serving=Serving(size=150, unit="g"),
                    display_order=1
                )
            ]
        )
        template = template_service.create_diet_template(
            db=test_db,
            obj_in=template_data,
            trainer_id=test_trainer.id
        )
        
        # Assign to client
        assignment = DietPlanAssign(
            client_id=test_client_profile.id,
            source_template_id=template.id
        )
        
        assigned_plan = assigned_plan_service.assign_diet_plan(
            db=test_db,
            assignment_in=assignment,
            trainer_id=test_trainer.id
        )
        
        assert assigned_plan.client_id == test_client_profile.id
        assert assigned_plan.source_template_id == template.id
        assert assigned_plan.plan_details is not None
        assert assigned_plan.plan_details["name"] == "High Protein"
    
    def test_diet_snapshot_includes_nutrition(self, test_db: Session, test_trainer: User, test_client_profile: Client, test_food_item: FoodItemLibrary):
        """Diet plan snapshot should include calculated nutrition."""
        template_data = DietPlanTemplateCreate(
            name="Meal Plan",
            description="Test",
            items=[
                DietTemplateItemCreate(
                    food_item_id=test_food_item.id,
                    meal_name="Lunch",
                    serving=Serving(size=200, unit="g"),
                    display_order=1
                )
            ]
        )
        template = template_service.create_diet_template(
            db=test_db,
            obj_in=template_data,
            trainer_id=test_trainer.id
        )
        
        assignment = DietPlanAssign(
            client_id=test_client_profile.id,
            source_template_id=template.id
        )
        assigned_plan = assigned_plan_service.assign_diet_plan(
            db=test_db,
            assignment_in=assignment,
            trainer_id=test_trainer.id
        )
        
        snapshot_item = assigned_plan.plan_details["items"][0]
        assert "calculatedNutrition" in snapshot_item
        assert snapshot_item["calculatedNutrition"]["calories"] > 0


class TestAssignmentOwnership:
    """Tests for ownership enforcement in assignments."""
    
    def test_trainer_cannot_assign_to_other_trainers_client(self, test_db: Session, test_trainer: User, test_exercise: ExerciseLibrary):
        """Trainer should not be able to assign plans to another trainer's client."""
        from app.domain.errors import OwnershipViolation
        
        # Create another trainer and their client
        other_trainer = User(
            id=uuid.uuid4(),
            email="other@trainer.com",
            hashed_password="hash",
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
        
        # Create template for test_trainer
        template_data = WorkoutPlanTemplateCreate(
            name="Plan",
            description="Test",
            items=[
                WorkoutTemplateItemCreate(
                    exercise_id=test_exercise.id,
                    day_name="Monday",
                    target_sets="3",
                    target_reps="10",
                    display_order=1
                )
            ]
        )
        template = template_service.create_workout_template(db=test_db, obj_in=template_data, trainer_id=test_trainer.id)
        
        # Try to assign to other trainer's client
        assignment = WorkoutPlanAssign(
            client_id=other_client.id,
            source_template_id=template.id
        )
        
        with pytest.raises((OwnershipViolation, HTTPException)):
            assigned_plan_service.assign_workout_plan(
                db=test_db,
                assignment_in=assignment,
                trainer_id=test_trainer.id
            )

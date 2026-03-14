# app/services/log_service.py
# Business logic for creating and retrieving logs.

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.client import Client
from app.models.log import WorkoutLog, DietLog
from app.models.activity import ActivityFeed
from app.api.deps import CurrentClient, CurrentUser
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.schemas.log import WorkoutLogCreate, DietLogCreate
from app.domain.client_guards import assert_client_allows_action
from app.domain.authorization.client_access import get_client_for_viewer

class LogService:
    def create_workout_log(self, db: Session, *, obj_in: WorkoutLogCreate, current_client: CurrentClient) -> WorkoutLog:
        """
        Creates a workout log and a corresponding activity feed entry in a single transaction.
        """
        if not current_client.client_profile:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client profile not found for this user.")
        client_id = current_client.client_profile.id
        
        # 1. Validate that the client exists
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.deleted_at.is_(None)
        ).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        
        # 2. Validate that the client is allowed to log a workout
        assert_client_allows_action(client, "log_workout")
        
        # 3. Validate that the assigned plan exists and belongs to the client
        assigned_plan = db.query(AssignedWorkoutPlan).filter(
            AssignedWorkoutPlan.id == obj_in.assigned_plan_id,
            AssignedWorkoutPlan.client_id == client_id,
            AssignedWorkoutPlan.deleted_at.is_(None)
        ).first()

        if not assigned_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned workout plan not found for this client.")
        
        try:
            # 4. Create the log entry
            log_entry = WorkoutLog(
                client_id=client_id,
                assigned_plan_id=obj_in.assigned_plan_id,
                performance_data=obj_in.performance_data
            )
            db.add(log_entry)
            
            # 5. Create the activity feed entry
            activity_entry = ActivityFeed(
                client_id=client_id,
                event_type='WORKOUT_LOGGED',
                event_timestamp=datetime.now(timezone.utc),
                event_metadata={
                    "workout_name": assigned_plan.plan_details.get("name", "Workout"),
                    "log_id": str(log_entry.id) # Will be populated after flush
                }
            )
            db.add(activity_entry)
            
            # 6. Commit the transaction
            db.commit()
            db.refresh(log_entry)
            return log_entry
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to log workout: {e}")

    def create_diet_log(self, db: Session, *, obj_in: DietLogCreate, current_client: CurrentClient) -> DietLog:
        """
        Creates a diet log and a corresponding activity feed entry in a single transaction.
        """
        if not current_client.client_profile:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client profile not found for this user.")
        client_id = current_client.client_profile.id

        # 1. Validate that the client exists
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.deleted_at.is_(None)
        ).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        #2. Validate that the client is allowed to log a diet
        assert_client_allows_action(client, "log_diet")
        
        # 3. Validate that the assigned plan exists and belongs to the client
        assigned_plan = db.query(AssignedDietPlan).filter(
            AssignedDietPlan.id == obj_in.assigned_plan_id,
            AssignedDietPlan.client_id == client_id,
            AssignedDietPlan.deleted_at.is_(None)
        ).first()
        if not assigned_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned diet plan not found for this client.")

        # 4. Create the log entry
        try:
            log_entry = DietLog(**obj_in.model_dump(), client_id=client_id)
            db.add(log_entry)
            
            # 5. Create the activity feed entry
            activity_entry = ActivityFeed(
                client_id=client_id,
                event_type='DIET_LOGGED',
                event_timestamp=datetime.now(timezone.utc),
                event_metadata={
                    "meal_name": obj_in.meal_name,
                    "status": obj_in.status,
                    "log_id": str(log_entry.id)
                }
            )
            db.add(activity_entry)
            
            db.commit()
            db.refresh(log_entry)
            return log_entry
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to log diet: {e}")

    def get_workout_logs(self, db: Session, *, client_id: uuid.UUID, current_user: CurrentUser, start_date: Optional[datetime], end_date: Optional[datetime], skip: int, limit: int) -> List[WorkoutLog]:
        client = get_client_for_viewer(db, client_id=client_id, current_user=current_user)
        assert_client_allows_action(client, "view_logs")

        query = db.query(WorkoutLog).filter(WorkoutLog.client_id == client_id)
        if start_date:
            query = query.filter(WorkoutLog.logged_at >= start_date)
        if end_date:
            query = query.filter(WorkoutLog.logged_at <= end_date)
        return query.order_by(WorkoutLog.logged_at.desc()).offset(skip).limit(limit).all()

    def get_diet_logs(self, db: Session, *, client_id: uuid.UUID, current_user: CurrentUser, start_date: Optional[datetime], end_date: Optional[datetime], skip: int, limit: int) -> List[DietLog]:
        client = get_client_for_viewer(db, client_id=client_id, current_user=current_user)
        assert_client_allows_action(client, "view_logs")

        query = db.query(DietLog).filter(DietLog.client_id == client_id)
        if start_date:
            query = query.filter(DietLog.logged_at >= start_date)
        if end_date:
            query = query.filter(DietLog.logged_at <= end_date)
        return query.order_by(DietLog.logged_at.desc()).offset(skip).limit(limit).all()


log_service = LogService()

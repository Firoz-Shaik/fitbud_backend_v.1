# app/services/trainee_service.py
import uuid
from datetime import date, timedelta, timezone
from sqlalchemy.orm import Session, joinedload
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.models.log import WorkoutLog, DietLog
from app.schemas.trainee import TraineePlans
from app.models.client import Client
from app.models.user import User

class TraineeService:
    def get_trainee_dashboard(self, db: Session, *, client_id: uuid.UUID) -> dict:
        today = date.today()
        
        # 1. Get today's workout
        assigned_workout = db.query(AssignedWorkoutPlan).filter(
            AssignedWorkoutPlan.client_id == client_id,
            AssignedWorkoutPlan.assigned_at <= today
        ).order_by(AssignedWorkoutPlan.assigned_at.desc()).first()
        
        # Basic logic: find if today's day name exists in the plan
        todays_workout_details = None
        is_rest_day = True
        if assigned_workout:
            day_of_week = today.strftime("%A") # e.g., "Monday"
            for day in assigned_workout.plan_details.get("days", []):
                if day_of_week in day.get("day_name", ""):
                    todays_workout_details = day
                    is_rest_day = False
                    break
        
        # 2. Calculate diet compliance
        assigned_diet = db.query(AssignedDietPlan).filter(
            AssignedDietPlan.client_id == client_id,
            AssignedDietPlan.assigned_at <= today
        ).order_by(AssignedDietPlan.assigned_at.desc()).first()
        
        diet_compliance_percent = 0.0
        if assigned_diet:
            total_meals_planned = sum([len(meal.get("items", [])) for meal in assigned_diet.plan_details.get("meals", [])])
            if total_meals_planned > 0:
                logged_meals_today = db.query(DietLog).filter(
                    DietLog.client_id == client_id,
                    DietLog.assigned_plan_id == assigned_diet.id,
                    DietLog.logged_at >= today,
                    DietLog.logged_at < today + timedelta(days=1),
                    DietLog.status == 'Followed'
                ).count()
                diet_compliance_percent = (logged_meals_today / total_meals_planned) * 100

        # 3. Calculate streak (simplified)
        current_streak_days = 0
        for i in range(365): # Check up to a year back
            check_date = today - timedelta(days=i)
            has_log = db.query(WorkoutLog).filter(WorkoutLog.client_id == client_id, WorkoutLog.logged_at >= check_date, WorkoutLog.logged_at < check_date + timedelta(days=1)).first()
            if not has_log:
                has_log = db.query(DietLog).filter(DietLog.client_id == client_id, DietLog.logged_at >= check_date, DietLog.logged_at < check_date + timedelta(days=1)).first()
            
            if has_log:
                current_streak_days += 1
            else:
                break

        client_record = db.query(Client).options(joinedload(Client.client_user)).filter(Client.id == client_id).first()
        is_fee_due = False
        payment_status = "unpaid" # Default value
        subscription_due_date = None

        if client_record:
            payment_status = client_record.payment_status
            subscription_due_date = client_record.subscription_due_date

            if client_record.subscription_due_date:
                if date.today() >= client_record.subscription_due_date.date() and not client_record.subscription_paid_status:
                    is_fee_due = True

        return {
            "assigned_workout": todays_workout_details,
            "is_rest_day": is_rest_day,
            "diet_compliance_percent": round(diet_compliance_percent, 2),
            "current_streak_days": current_streak_days,
            "is_fee_due": is_fee_due,
            "payment_status": payment_status,
            "subscription_due_date": subscription_due_date
        }
    
        
    def get_trainee_plans(self, db: Session, *, client_id: uuid.UUID) -> TraineePlans:
        """
        Retrieves the most recently assigned workout and diet plans for a trainee.
        """
        latest_workout_plan = db.query(AssignedWorkoutPlan).filter(
            AssignedWorkoutPlan.client_id == client_id,
            AssignedWorkoutPlan.deleted_at.is_(None)
        ).order_by(AssignedWorkoutPlan.assigned_at.desc()).first()

        latest_diet_plan = db.query(AssignedDietPlan).filter(
            AssignedDietPlan.client_id == client_id,
            AssignedDietPlan.deleted_at.is_(None)
        ).order_by(AssignedDietPlan.assigned_at.desc()).first()

        return TraineePlans(
            workout_plan=latest_workout_plan,
            diet_plan=latest_diet_plan
        )
    def mark_payment_as_pending(self, db: Session, *, current_user: User) -> Client:
        """
        Finds the client profile for the current user and sets their
        payment status to 'pending'.
        """
        if not current_user.client_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found for this user.")
        
        client = current_user.client_profile
        client.payment_status = "pending"
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

trainee_service = TraineeService()
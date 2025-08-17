# create_trainers.py

from app.core.database import SessionLocal
from app.services.user_service import user_service
from app.schemas.user import UserCreate
from app.models.user import User
from app.models.client import Client
from app.models.template import WorkoutPlanTemplate, DietPlanTemplate
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.models.log import WorkoutLog, DietLog, Checkin
from app.models.activity import ActivityFeed

def create_initial_trainers():
    db = SessionLocal()
    try:
        print("Checking for existing trainers...")

        trainer1_email = "trainer1@fitbud.com"
        trainer2_email = "trainer2@fitbud.com"

        # Check if trainer 1 exists
        user1 = user_service.get_user_by_email(db, email=trainer1_email)
        if not user1:
            print(f"Creating trainer: {trainer1_email}")
            trainer1_in = UserCreate(
                email=trainer1_email,
                password="testuser1",
                full_name="Trainer One",
                user_role="trainer"
            )
            user_service.create_user(db, obj_in=trainer1_in)
            print("Trainer 1 created successfully.")
        else:
            print("Trainer 1 already exists.")

        # Check if trainer 2 exists
        user2 = user_service.get_user_by_email(db, email=trainer2_email)
        if not user2:
            print(f"Creating trainer: {trainer2_email}")
            trainer2_in = UserCreate(
                email=trainer2_email,
                password="testuser2",
                full_name="Trainer Two",
                user_role="trainer"
            )
            user_service.create_user(db, obj_in=trainer2_in)
            print("Trainer 2 created successfully.")
        else:
            print("Trainer 2 already exists.")

    finally:
        db.close()

if __name__ == "__main__":
    print("Starting trainer creation process...")
    create_initial_trainers()
    print("Process finished.")
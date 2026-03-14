import argparse
import random
import uuid
import os
import sys
import io
import csv
import json
from datetime import datetime, timedelta
from faker import Faker

# ---------- PROJECT ROOT FIX ----------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.client import Client
from app.models.template import (
    WorkoutPlanTemplate,
    DietPlanTemplate,
    WorkoutTemplateItem,
    DietTemplateItem,
    ExerciseLibrary,
    FoodItemLibrary,
)
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.models.log import Checkin, WorkoutLog, DietLog
from app.models.activity import ActivityFeed

fake = Faker()
fake_us = Faker("en_US")
fake_ind = Faker("en_IN")

def fake_name():
    return fake_us.name() if random.random() < 0.75 else fake_ind.name()

def fake_email():
    f = fake_us if random.random() < 0.75 else fake_ind
    name = f.user_name()
    return f"{name}_{uuid.uuid4().hex[:5]}@fitbud.com"

# ---------- COPY HELPER ----------
def copy_rows(db: Session, table_name: str, columns: list[str], rows: list[tuple]):

    if not rows:
        return

    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    for row in rows:
        writer.writerow(row)

    buffer.seek(0)

    cursor.copy_expert(
        f"COPY {table_name} ({','.join(columns)}) FROM STDIN WITH CSV",
        buffer
    )


# ---------- RESET DATABASE ----------
def reset_db(db: Session):
    db.execute(text("""
        TRUNCATE TABLE
            activity_feed,
            diet_logs,
            workout_logs,
            checkins,
            assigned_diet_plans,
            assigned_workout_plans,
            diet_template_items,
            workout_template_items,
            diet_plan_templates,
            workout_plan_templates,
            food_item_library,
            exercise_library,
            clients,
            users
        CASCADE
    """))


# ---------- MAIN SEED FUNCTION ----------
def seed(scale: int):

    db: Session = SessionLocal()

    try:

        reset_db(db)
        db.commit()

        trainers = []

        # ---------- CREATE TRAINERS ----------
        for i in range(scale):
            trainer = User(
                email=fake_email(),
                hashed_password=get_password_hash("trainer_password"),
                full_name=fake_name(),
                user_role="trainer",
            )

            db.add(trainer)
            trainers.append(trainer)

        db.flush()

        for idx, t in enumerate(trainers, start=1):
            print(f"Inserted Trainer {idx} -> {t.full_name} ({t.id})")

        # ---------- PROCESS TRAINERS ----------
        for trainer in trainers:

            exercises = []
            foods = []

            for _ in range(5):
                exercises.append(
                    ExerciseLibrary(
                        id=uuid.uuid4(),
                        name=f"{fake.word().title()} {fake.word().title()}",
                        description=fake.sentence(),
                        owner_trainer_id=trainer.id,
                        is_verified=False,
                    )
                )

            for _ in range(5):
                foods.append(
                    FoodItemLibrary(
                        id=uuid.uuid4(),
                        name=f"{fake.word().title()} {fake.word().title()}",
                        owner_trainer_id=trainer.id,
                        is_verified=False,
                        base_unit_type="MASS",
                        calories_per_100g=random.randint(100, 300),
                        protein_per_100g=random.uniform(5, 30),
                        carbs_per_100g=random.uniform(10, 60),
                        fat_per_100g=random.uniform(2, 20),
                    )
                )

            db.add_all(exercises + foods)

            workout_template = WorkoutPlanTemplate(
                trainer_id=trainer.id,
                name="Seeded Workout Plan",
                description="Auto seeded",
            )

            diet_template = DietPlanTemplate(
                trainer_id=trainer.id,
                name="Seeded Diet Plan",
                description="Auto seeded",
            )

            db.add(workout_template)
            db.add(diet_template)
            db.flush()

            workout_items = []
            diet_items = []

            for idx, day in enumerate(["Monday", "Wednesday", "Friday"]):

                workout_items.append(
                    WorkoutTemplateItem(
                        template_id=workout_template.id,
                        exercise_id=random.choice(exercises).id,
                        day_name=day,
                        target_sets="3",
                        target_reps="10",
                        rest_period_seconds=60,
                        display_order=idx + 1,
                    )
                )

            for meal in ["Breakfast", "Lunch", "Dinner"]:

                diet_items.append(
                    DietTemplateItem(
                        template_id=diet_template.id,
                        food_item_id=random.choice(foods).id,
                        meal_name=meal,
                        serving_size=150,
                        serving_unit="g",
                        display_order=1,
                    )
                )

            db.add_all(workout_items + diet_items)

            # ---------- LOG BUFFERS ----------
            checkins = []
            workout_logs = []
            diet_logs = []
            activities = []

            client_count = random.randint(50, 100)

            for i in range(client_count):

                invited = random.random() > 0.7
                invited_name = fake_name()
                invited_email = fake_email()

                client_user = None

                if not invited:
                    client_user = User(
                        email=invited_email,
                        hashed_password=get_password_hash("client_password"),
                        full_name=invited_name,
                        user_role="client",
                    )

                    db.add(client_user)
                    db.flush()

                    print(f"Inserted Client User -> {client_user.full_name} ({client_user.id})")

                client = Client(
                    trainer_user_id=trainer.id,
                    client_user_id=client_user.id if client_user else None,
                    client_status="invited" if invited else "active",
                    goal=random.choice(["Weight Loss", "Muscle Gain", "General Fitness"]),
                    invited_full_name=invited_name,
                    invited_email=invited_email,
                    invite_code=fake.unique.bothify(text="########"),
                    initial_weight_kg=random.uniform(60, 100),
                    height_cm=random.uniform(150, 190),
                )

                db.add(client)
                db.flush()

                print(f"Inserted Client -> {client.invited_full_name} ({client.id})")

                workout_plan = AssignedWorkoutPlan(
                    client_id=client.id,
                    source_template_id=workout_template.id,
                    plan_details={"name": workout_template.name},
                )

                diet_plan = AssignedDietPlan(
                    client_id=client.id,
                    source_template_id=diet_template.id,
                    plan_details={"name": diet_template.name},
                )

                db.add(workout_plan)
                db.add(diet_plan)
                db.flush()

                activities.append((
                    str(client.id),
                    "WORKOUT_PLAN_ASSIGNED",
                    datetime.utcnow(),
                    json.dumps({"plan_id": str(workout_plan.id)})
                ))

                activities.append((
                    str(client.id),
                    "DIET_PLAN_ASSIGNED",
                    datetime.utcnow(),
                    json.dumps({"plan_id": str(diet_plan.id)})
                ))

                if client.client_status == "active":

                    today = datetime.utcnow().date()

                    for j in range(random.randint(5, 10)):

                        day = today - timedelta(days=j)

                        checkins.append((
                            str(client.id),
                            random.uniform(60, 100),
                            None,
                            None,
                            datetime.combine(day, datetime.min.time())
                        ))

                        workout_logs.append((
                            str(client.id),
                            str(workout_plan.id),
                            json.dumps({"sets": 3})
                        ))

                        diet_logs.append((
                            str(client.id),
                            str(diet_plan.id),
                            "Breakfast",
                            "Followed"
                        ))

                # ---------- COPY BATCH ----------
                if (i + 1) % 10 == 0:

                    copy_rows(
                        db,
                        "checkins",
                        ["client_id", "weight_kg", "progress_photo_url", "notes", "checked_in_at"],
                        checkins
                    )

                    copy_rows(
                        db,
                        "workout_logs",
                        ["client_id", "assigned_plan_id", "performance_data"],
                        workout_logs
                    )

                    copy_rows(
                        db,
                        "diet_logs",
                        ["client_id", "assigned_plan_id", "meal_name", "status"],
                        diet_logs
                    )

                    copy_rows(
                        db,
                        "activity_feed",
                        ["client_id", "event_type", "event_timestamp", "event_metadata"],
                        activities
                    )

                    db.commit()

                    checkins.clear()
                    workout_logs.clear()
                    diet_logs.clear()
                    activities.clear()

                    print(f"Committed {i+1} clients for trainer {trainer.id}")

            # ---------- FINAL COPY ----------
            copy_rows(db,"checkins",
                ["client_id","weight_kg","progress_photo_url","notes","checked_in_at"],
                checkins)

            copy_rows(db,"workout_logs",
                ["client_id","assigned_plan_id","performance_data"],
                workout_logs)

            copy_rows(db,"diet_logs",
                ["client_id","assigned_plan_id","meal_name","status"],
                diet_logs)

            copy_rows(db,"activity_feed",
                ["client_id","event_type","event_timestamp","event_metadata"],
                activities)

            db.commit()

        print(f"\nSeeded DB with {scale} trainers")

    finally:
        db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=int, default=3)
    args = parser.parse_args()

    seed(args.scale)
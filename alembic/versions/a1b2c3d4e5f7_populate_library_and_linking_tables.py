"""populate_library_and_linking_tables

Revision ID: a1b2c3d4e5f7
Revises: c1a2b3d4e5f6
Create Date: 2025-08-31 10:47:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Data Migration for Workout Plan Templates ---
    op.execute("""
    WITH template_exercises AS (
        SELECT
            id AS template_id,
            (jsonb_array_elements(plan_structure -> 'days') ->> 'day_name') AS day_name,
            jsonb_array_elements(jsonb_array_elements(plan_structure -> 'days') -> 'items') AS exercise_item
        FROM
            workout_plan_templates
        WHERE
            plan_structure IS NOT NULL
    ),
    distinct_exercises AS (
        SELECT DISTINCT
            exercise_item ->> 'exercise_name' AS exercise_name
        FROM
            template_exercises
    )
    INSERT INTO exercise_library (id, name)
    SELECT
        uuid_generate_v4(),
        exercise_name
    FROM
        distinct_exercises
    ON CONFLICT (name) DO NOTHING;
    """)

    op.execute("""
    INSERT INTO workout_template_items (template_id, exercise_id, day_name, sets_details)
    SELECT
        t.id,
        el.id,
        (jsonb_array_elements(t.plan_structure -> 'days') ->> 'day_name') AS day_name,
        (jsonb_array_elements(jsonb_array_elements(t.plan_structure -> 'days') -> 'items') -> 'sets') AS sets_details
    FROM
        workout_plan_templates t
    CROSS JOIN LATERAL
        jsonb_array_elements(t.plan_structure -> 'days') day
    CROSS JOIN LATERAL
        jsonb_array_elements(day -> 'items') item
    JOIN
        exercise_library el ON el.name = item ->> 'exercise_name'
    WHERE
        t.plan_structure IS NOT NULL;
    """)

    # --- Data Migration for Diet Plan Templates ---
    op.execute("""
    WITH template_food_items AS (
        SELECT
            id AS template_id,
            (jsonb_array_elements(plan_structure -> 'meals') ->> 'meal_name') AS meal_name,
            jsonb_array_elements(jsonb_array_elements(plan_structure -> 'meals') -> 'items') AS food_item
        FROM
            diet_plan_templates
        WHERE
            plan_structure IS NOT NULL
    ),
    distinct_food_items AS (
        SELECT DISTINCT
            food_item ->> 'name' AS food_name
        FROM
            template_food_items
    )
    INSERT INTO food_item_library (id, name)
    SELECT
        uuid_generate_v4(),
        food_name
    FROM
        distinct_food_items
    ON CONFLICT (name) DO NOTHING;
    """)

    op.execute("""
    INSERT INTO diet_template_items (template_id, food_item_id, meal_name, serving_details)
    SELECT
        t.id,
        fl.id,
        (jsonb_array_elements(t.plan_structure -> 'meals') ->> 'meal_name') AS meal_name,
        (jsonb_array_elements(jsonb_array_elements(t.plan_structure -> 'meals') -> 'items')) - 'name' AS serving_details
    FROM
        diet_plan_templates t
    CROSS JOIN LATERAL
        jsonb_array_elements(t.plan_structure -> 'meals') meal
    CROSS JOIN LATERAL
        jsonb_array_elements(meal -> 'items') item
    JOIN
        food_item_library fl ON fl.name = item ->> 'name'
    WHERE
        t.plan_structure IS NOT NULL;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM diet_template_items;")
    op.execute("DELETE FROM workout_template_items;")
    op.execute("DELETE FROM food_item_library;")
    op.execute("DELETE FROM exercise_library;")
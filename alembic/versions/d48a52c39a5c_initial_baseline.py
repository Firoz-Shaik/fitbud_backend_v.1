"""Initial baseline revision (schema bootstrap).

Revision ID: d48a52c39a5c
Revises: None
Create Date: 2026-01-07

This project historically used a SQL bootstrap (`fitbud_v1.sql`) and later
switched to Alembic-managed migrations. Some migrations reference this base
revision, but the file was missing from the repo, causing Alembic to crash
with KeyError: 'd48a52c39a5c'.

This revision bootstraps the original V1 schema (derived from `fitbud_v1.sql`)
so a fresh database can be created purely via Alembic.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d48a52c39a5c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Core user & client management tables
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            user_role TEXT NOT NULL CHECK (user_role IN ('trainer', 'client')),
            profile_photo_url TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique_when_active_idx
        ON users (email)
        WHERE deleted_at IS NULL;
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            trainer_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            -- Nullable to support invites before registration
            client_user_id UUID UNIQUE REFERENCES users(id) ON DELETE RESTRICT,
            status TEXT NOT NULL CHECK (status IN ('invited', 'active', 'inactive')),
            goal_description TEXT,
            invite_code TEXT UNIQUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS clients_trainer_user_id_idx ON clients (trainer_user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS clients_client_user_id_idx ON clients (client_user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS clients_trainer_user_id_status_idx ON clients (trainer_user_id, status);")

    # Template tables ("blueprints")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS exercise_library (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name TEXT NOT NULL,
            description TEXT,
            video_url TEXT,
            owner_trainer_id UUID REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS exercise_library_owner_trainer_id_idx ON exercise_library (owner_trainer_id);")

    # NOTE: plan_structure is added later via migration 8a7b3c2d1f0e
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_plan_templates (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            trainer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            parent_template_id UUID REFERENCES workout_plan_templates(id) ON DELETE SET NULL,
            version INT NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS workout_plan_templates_trainer_id_idx ON workout_plan_templates (trainer_id);")
    op.execute(
        "CREATE INDEX IF NOT EXISTS workout_plan_templates_parent_template_id_idx ON workout_plan_templates (parent_template_id);"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS diet_plan_templates (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            trainer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            parent_template_id UUID REFERENCES diet_plan_templates(id) ON DELETE SET NULL,
            version INT NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS diet_plan_templates_trainer_id_idx ON diet_plan_templates (trainer_id);")
    op.execute("CREATE INDEX IF NOT EXISTS diet_plan_templates_parent_template_id_idx ON diet_plan_templates (parent_template_id);")

    # Assigned plan tables (JSONB snapshot pattern)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS assigned_workout_plans (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            source_template_id UUID REFERENCES workout_plan_templates(id) ON DELETE SET NULL,
            plan_details JSONB NOT NULL,
            assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS assigned_workout_plans_client_id_idx ON assigned_workout_plans (client_id);")
    op.execute(
        "CREATE INDEX IF NOT EXISTS assigned_workout_plans_source_template_id_idx ON assigned_workout_plans (source_template_id);"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS assigned_diet_plans (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            source_template_id UUID REFERENCES diet_plan_templates(id) ON DELETE SET NULL,
            plan_details JSONB NOT NULL,
            assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            deleted_at TIMESTAMPTZ DEFAULT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS assigned_diet_plans_client_id_idx ON assigned_diet_plans (client_id);")
    op.execute(
        "CREATE INDEX IF NOT EXISTS assigned_diet_plans_source_template_id_idx ON assigned_diet_plans (source_template_id);"
    )

    # Logging & activity feed tables
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_logs (
            id BIGSERIAL PRIMARY KEY,
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            assigned_plan_id UUID NOT NULL REFERENCES assigned_workout_plans(id) ON DELETE CASCADE,
            performance_data JSONB,
            logged_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS workout_logs_client_id_logged_at_desc_idx ON workout_logs (client_id, logged_at DESC);"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS diet_logs (
            id BIGSERIAL PRIMARY KEY,
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            assigned_plan_id UUID NOT NULL REFERENCES assigned_diet_plans(id) ON DELETE CASCADE,
            meal_name TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('Followed', 'Partially Followed', 'Skipped')),
            logged_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS diet_logs_client_id_logged_at_desc_idx ON diet_logs (client_id, logged_at DESC);")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS checkins (
            id BIGSERIAL PRIMARY KEY,
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            weight_kg NUMERIC(6, 2),
            measurements JSONB,
            progress_photo_url TEXT,
            subjective_scores JSONB,
            notes TEXT,
            checked_in_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS checkins_client_id_checked_in_at_desc_idx ON checkins (client_id, checked_in_at DESC);")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_feed (
            id BIGSERIAL PRIMARY KEY,
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            event_timestamp TIMESTAMPTZ NOT NULL,
            metadata JSONB
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS activity_feed_client_id_event_timestamp_desc_idx ON activity_feed (client_id, event_timestamp DESC);"
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.execute("DROP TABLE IF EXISTS activity_feed CASCADE;")
    op.execute("DROP TABLE IF EXISTS checkins CASCADE;")
    op.execute("DROP TABLE IF EXISTS diet_logs CASCADE;")
    op.execute("DROP TABLE IF EXISTS workout_logs CASCADE;")
    op.execute("DROP TABLE IF EXISTS assigned_diet_plans CASCADE;")
    op.execute("DROP TABLE IF EXISTS assigned_workout_plans CASCADE;")
    op.execute("DROP TABLE IF EXISTS diet_plan_templates CASCADE;")
    op.execute("DROP TABLE IF EXISTS workout_plan_templates CASCADE;")
    op.execute("DROP TABLE IF EXISTS exercise_library CASCADE;")
    op.execute("DROP TABLE IF EXISTS clients CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")


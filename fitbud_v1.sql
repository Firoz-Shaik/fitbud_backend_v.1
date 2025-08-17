-- Fitbud V1 Production Schema
-- Final DDL - Ready for Deployment
-- Design decisions reflect JSONB snapshot pattern and soft deletes.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

--------------------------------------------------------------------------------
-- Core User & Client Management Tables
--------------------------------------------------------------------------------

CREATE TABLE users (
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

-- Partial unique index for soft-delete compatibility
CREATE UNIQUE INDEX users_email_unique_when_active_idx ON users (email) WHERE deleted_at IS NULL;

CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trainer_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    client_user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK (status IN ('invited', 'active', 'inactive')),
    goal_description TEXT,
    invite_code TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

-- Indexes for clients table
CREATE INDEX clients_trainer_user_id_idx ON clients (trainer_user_id);
CREATE INDEX clients_client_user_id_idx ON clients (client_user_id);
-- Composite index for the main trainer dashboard query
CREATE INDEX clients_trainer_user_id_status_idx ON clients (trainer_user_id, status);

--------------------------------------------------------------------------------
-- Template Tables (The "Blueprints")
--------------------------------------------------------------------------------

CREATE TABLE exercise_library (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    video_url TEXT,
    owner_trainer_id UUID REFERENCES users(id) ON DELETE SET NULL, -- If trainer is deleted, exercise becomes global
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX exercise_library_owner_trainer_id_idx ON exercise_library (owner_trainer_id);

CREATE TABLE workout_plan_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trainer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    parent_template_id UUID REFERENCES workout_plan_templates(id) ON DELETE SET NULL, -- For V2 versioning
    version INT NOT NULL DEFAULT 1, -- For V2 versioning
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX workout_plan_templates_trainer_id_idx ON workout_plan_templates (trainer_id);
CREATE INDEX workout_plan_templates_parent_template_id_idx ON workout_plan_templates (parent_template_id);


CREATE TABLE diet_plan_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trainer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    parent_template_id UUID REFERENCES diet_plan_templates(id) ON DELETE SET NULL, -- For V2 versioning
    version INT NOT NULL DEFAULT 1, -- For V2 versioning
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX diet_plan_templates_trainer_id_idx ON diet_plan_templates (trainer_id);
CREATE INDEX diet_plan_templates_parent_template_id_idx ON diet_plan_templates (parent_template_id);


--------------------------------------------------------------------------------
-- Assigned Plan Tables (JSONB Snapshot Pattern)
--------------------------------------------------------------------------------

CREATE TABLE assigned_workout_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE, -- If relationship is deleted, assigned plan is too
    source_template_id UUID REFERENCES workout_plan_templates(id) ON DELETE SET NULL,
    plan_details JSONB NOT NULL, -- Snapshot of the full plan
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX assigned_workout_plans_client_id_idx ON assigned_workout_plans (client_id);
CREATE INDEX assigned_workout_plans_source_template_id_idx ON assigned_workout_plans (source_template_id);


CREATE TABLE assigned_diet_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    source_template_id UUID REFERENCES diet_plan_templates(id) ON DELETE SET NULL,
    plan_details JSONB NOT NULL, -- Snapshot of the full plan
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX assigned_diet_plans_client_id_idx ON assigned_diet_plans (client_id);
CREATE INDEX assigned_diet_plans_source_template_id_idx ON assigned_diet_plans (source_template_id);


--------------------------------------------------------------------------------
-- Logging & Activity Feed Tables
--------------------------------------------------------------------------------

-- NOTE: Application logic MUST wrap inserts into a log table AND activity_feed in a single transaction.

CREATE TABLE workout_logs (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    assigned_plan_id UUID NOT NULL REFERENCES assigned_workout_plans(id) ON DELETE CASCADE,
    performance_data JSONB, -- e.g., { "exercise_name": "Squat", "sets": [{"reps": 10, "weight": 50}] }
    logged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX workout_logs_client_id_logged_at_desc_idx ON workout_logs (client_id, logged_at DESC);

CREATE TABLE diet_logs (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    assigned_plan_id UUID NOT NULL REFERENCES assigned_diet_plans(id) ON DELETE CASCADE,
    meal_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Followed', 'Partially Followed', 'Skipped')),
    logged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX diet_logs_client_id_logged_at_desc_idx ON diet_logs (client_id, logged_at DESC);

CREATE TABLE checkins (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    weight_kg NUMERIC(6, 2),
    measurements JSONB, -- e.g., {"waist_cm": 80, "hip_cm": 95}
    progress_photo_url TEXT,
    subjective_scores JSONB, -- e.g., {"energy": 8, "sleep_quality": 7}
    notes TEXT,
    checked_in_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX checkins_client_id_checked_in_at_desc_idx ON checkins (client_id, checked_in_at DESC);

CREATE TABLE activity_feed (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- e.g., 'WORKOUT_LOGGED', 'CHECKIN_SUBMITTED', 'DIET_LOGGED'
    event_timestamp TIMESTAMPTZ NOT NULL,
    metadata JSONB -- e.g., {"workout_name": "Upper Body A"} or {"weight": "75.5 kg"}
);

-- The most important index for the trainer's dashboard log feed.
CREATE INDEX activity_feed_client_id_event_timestamp_desc_idx ON activity_feed (client_id, event_timestamp DESC);


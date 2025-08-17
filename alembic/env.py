# alembic/env.py
# This file is executed when the 'alembic' command is run.

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- Start of Fitbud Configuration ---

# Add the 'app' directory to the Python path
# This allows Alembic to find our application's modules (models, core)
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Import our SQLAlchemy Base and the settings object
from app.core.database import Base
from app.core.config import settings
# Import all the models to ensure they are registered with the Base metadata
from app.models.user import User
from app.models.client import Client
from app.models.template import WorkoutPlanTemplate, DietPlanTemplate
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.models.log import WorkoutLog, DietLog, Checkin
from app.models.activity import ActivityFeed


# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the SQLAlchemy URL from our Pydantic settings
# This ensures Alembic uses the same database URL as our app.
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the target metadata for Alembic 'autogenerate' support
# It points to our application's Base object.
target_metadata = Base.metadata

# --- End of Fitbud Configuration ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

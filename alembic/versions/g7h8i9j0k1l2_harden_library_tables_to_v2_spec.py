"""Harden library tables to V2 spec

Revision ID: g7h8i9j0k1l2
Revises: f9e8d7c6b5a4
Create Date: 2025-09-01 11:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'g7h8i9j0k1l2'
down_revision: Union[str, None] = 'f9e8d7c6b5a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Add new columns to exercise_library ###
    op.add_column('exercise_library', sa.Column('owner_trainer_id', sa.UUID(), nullable=True))
    op.add_column('exercise_library', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('exercise_library', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('exercise_library', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_exercise_library_owner', 'exercise_library', 'users', ['owner_trainer_id'], ['id'])

    # ### Add new columns to food_item_library ###
    op.add_column('food_item_library', sa.Column('owner_trainer_id', sa.UUID(), nullable=True))
    op.add_column('food_item_library', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('food_item_library', sa.Column('base_unit_type', sa.String(), nullable=True))
    op.add_column('food_item_library', sa.Column('grams_per_ml', sa.Numeric(), nullable=True))
    op.add_column('food_item_library', sa.Column('calories_per_100g', sa.Integer(), nullable=True))
    op.add_column('food_item_library', sa.Column('protein_per_100g', sa.Numeric(), nullable=True))
    op.add_column('food_item_library', sa.Column('carbs_per_100g', sa.Numeric(), nullable=True))
    op.add_column('food_item_library', sa.Column('fat_per_100g', sa.Numeric(), nullable=True))
    op.add_column('food_item_library', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('food_item_library', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_food_item_library_owner', 'food_item_library', 'users', ['owner_trainer_id'], ['id'])

    # ### Restructure workout_template_items ###
    op.add_column('workout_template_items', sa.Column('target_sets', sa.String(), nullable=True))
    op.add_column('workout_template_items', sa.Column('target_reps', sa.String(), nullable=True))
    op.add_column('workout_template_items', sa.Column('rest_period_seconds', sa.Integer(), nullable=True))
    op.add_column('workout_template_items', sa.Column('notes', sa.Text(), nullable=True))
    op.drop_column('workout_template_items', 'sets_details')
    # Enforce ondelete='RESTRICT'
    op.drop_constraint('workout_template_items_exercise_id_fkey', 'workout_template_items', type_='foreignkey')
    op.create_foreign_key('fk_workout_template_items_exercise', 'workout_template_items', 'exercise_library', ['exercise_id'], ['id'], ondelete='RESTRICT')

    # ### Restructure diet_template_items ###
    op.add_column('diet_template_items', sa.Column('serving_size', sa.Numeric(), nullable=True))
    op.add_column('diet_template_items', sa.Column('serving_unit', sa.String(), nullable=True))
    op.add_column('diet_template_items', sa.Column('notes', sa.Text(), nullable=True))
    op.drop_column('diet_template_items', 'serving_details')
    # Enforce ondelete='RESTRICT'
    op.drop_constraint('diet_template_items_food_item_id_fkey', 'diet_template_items', type_='foreignkey')
    op.create_foreign_key('fk_diet_template_items_food_item', 'diet_template_items', 'food_item_library', ['food_item_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    # ### Revert diet_template_items ###
    op.drop_constraint('fk_diet_template_items_food_item', 'diet_template_items', type_='foreignkey')
    op.create_foreign_key('diet_template_items_food_item_id_fkey', 'diet_template_items', 'food_item_library', ['food_item_id'], ['id'], ondelete='CASCADE')
    op.add_column('diet_template_items', sa.Column('serving_details', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.drop_column('diet_template_items', 'notes')
    op.drop_column('diet_template_items', 'serving_unit')
    op.drop_column('diet_template_items', 'serving_size')

    # ### Revert workout_template_items ###
    op.drop_constraint('fk_workout_template_items_exercise', 'workout_template_items', type_='foreignkey')
    op.create_foreign_key('workout_template_items_exercise_id_fkey', 'workout_template_items', 'exercise_library', ['exercise_id'], ['id'], ondelete='CASCADE')
    op.add_column('workout_template_items', sa.Column('sets_details', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.drop_column('workout_template_items', 'notes')
    op.drop_column('workout_template_items', 'rest_period_seconds')
    op.drop_column('workout_template_items', 'target_reps')
    op.drop_column('workout_template_items', 'target_sets')

    # ### Revert food_item_library ###
    op.drop_constraint('fk_food_item_library_owner', 'food_item_library', type_='foreignkey')
    op.drop_column('food_item_library', 'deleted_at')
    op.drop_column('food_item_library', 'updated_at')
    op.drop_column('food_item_library', 'fat_per_100g')
    op.drop_column('food_item_library', 'carbs_per_100g')
    op.drop_column('food_item_library', 'protein_per_100g')
    op.drop_column('food_item_library', 'calories_per_100g')
    op.drop_column('food_item_library', 'grams_per_ml')
    op.drop_column('food_item_library', 'base_unit_type')
    op.drop_column('food_item_library', 'is_verified')
    op.drop_column('food_item_library', 'owner_trainer_id')

    # ### Revert exercise_library ###
    op.drop_constraint('fk_exercise_library_owner', 'exercise_library', type_='foreignkey')
    op.drop_column('exercise_library', 'deleted_at')
    op.drop_column('exercise_library', 'updated_at')
    op.drop_column('exercise_library', 'is_verified')
    op.drop_column('exercise_library', 'owner_trainer_id')
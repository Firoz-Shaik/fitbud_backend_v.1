#app/domain/authorization/template_access.py

from sqlalchemy.orm import Session
from app.domain.errors import OwnershipViolation, ResourceNotFound
from app.models.template import WorkoutPlanTemplate, DietPlanTemplate

def get_workout_template_for_trainer(db: Session, *, template_id, trainer_id):
    template = db.query(WorkoutPlanTemplate).filter(
        WorkoutPlanTemplate.id == template_id,
        WorkoutPlanTemplate.deleted_at.is_(None),
    ).first()

    if not template:
        raise ResourceNotFound("Workout plan template not found")

    if template.trainer_id != trainer_id:
        raise OwnershipViolation("Trainer does not own this workout template")

    return template

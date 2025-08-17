# app/api/v1/api.py
# This file aggregates all the routers from the 'api/v1' directory.

from fastapi import APIRouter
from .endpoints import auth, clients, templates, assigned_plans, logs, checkins, trainers, trainees, library,users

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# User-specific settings
api_router.include_router(users.router, prefix="/users", tags=["Users"])
# Trainer-facing endpoints
api_router.include_router(trainers.router, prefix="/trainers", tags=["Trainer"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(assigned_plans.router, prefix="/assigned-plans", tags=["Assigned Plans"])
api_router.include_router(library.router, prefix="/library", tags=["Library"]) # NEW

# Trainee-facing endpoints
api_router.include_router(trainees.router, prefix="/trainees", tags=["Trainee"])

# Shared endpoints
api_router.include_router(logs.router, prefix="/logs", tags=["Logging"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["Check-ins"])

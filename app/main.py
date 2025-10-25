# app/main.py
# The main entry point for the FastAPI application.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import the middleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Fitbud API",
    description="The backend for the Fitbud fitness platform.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Define the list of allowed origins (your frontend URL)
origins = [
    "http://localhost:8000",
    "http://localhost:5174",
    "http://localhost:5173"
]

# Add the CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# Include the main API router with a prefix
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok", "version": "1.0.0"}

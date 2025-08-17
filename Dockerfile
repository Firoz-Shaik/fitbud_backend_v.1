# Dockerfile
# Defines the environment for the FastAPI application container.

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application's code into the container at /app
COPY . /app

# Command to run the application
# The docker-compose.yml will override this with a command that supports hot-reloading.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

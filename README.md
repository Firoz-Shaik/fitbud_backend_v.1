**Fitbud Backend V1**
**Problem Statement**
Fitbud is a comprehensive backend platform for fitness trainers who need an efficient way to manage clients, create custom workout and diet plans, and track their progress.

Features
Secure User Authentication: JWT-based authentication for trainers and their clients, with secure password handling.

Complete Client Management: Invite new clients, manage their active status, and store private notes and health details.

Dynamic Plan Creation: Trainers can create, update, and manage reusable workout and diet plan templates with a flexible JSON-based structure.

Plan Assignment: Assign custom plans to clients, which creates an immutable snapshot of the plan at the time of assignment.

Progress Tracking: Clients can log their workouts, meals, and weekly check-ins, which are then reflected in a real-time activity feed for the trainer.

Trainee Dashboard: A dedicated set of endpoints for the trainee-facing application to fetch daily workout/diet plans, track streaks, and manage subscription payments.

Trainer Dashboard: Endpoints to provide trainers with key stats, such as the number of active clients and month-over-month growth.

**Tech Stack**
Technology	Purpose
Python	The core programming language for the backend.
FastAPI	A modern, high-performance web framework for building APIs with Python. Chosen for its speed, automatic interactive documentation (Swagger UI), and dependency injection system.
PostgreSQL	A powerful, open-source object-relational database system. Chosen for its reliability, robustness, and support for advanced data types like JSONB.
SQLAlchemy	The Python SQL toolkit and Object Relational Mapper (ORM) that gives application developers the full power and flexibility of SQL.
Alembic	A lightweight database migration tool for SQLAlchemy, allowing for easy management of schema changes.
Pydantic	A data validation and settings management library, used to define clear data schemas for API requests and responses.
Docker	Used to containerize the application and its database, ensuring a consistent development and deployment environment.

**Architectural Decisions**
This project is built using a service-oriented architecture. The application is divided into logical domains (e.g., users, clients, plans), each with its own service layer (client_service.py, template_service.py, etc.). This was a deliberate choice for several reasons:

  Separation of Concerns: It cleanly separates the API routing logic from the core business logic. The API endpoints are responsible for handling HTTP requests and responses, while the service layer           contains the actual business rules, database interactions, and logic.

  Reusability: Business logic can be easily reused across different parts of the application. For example, the user_service is used by both the authentication endpoints and the client management endpoints.

  Testability: By isolating the business logic in services, we can write more focused and effective unit tests without needing to simulate a full HTTP request.

  Scalability: As the application grows, this structure makes it easier to add new features or modify existing ones without impacting other parts of the system.

**Setup & Installation**
Follow these steps to get the Fitbud backend running locally using Docker.

**Prerequisites
Docker and Docker Compose installed on your machine.**

**1. Clone the Repository**
  Bash
  git clone <your-repository-url>
  cd fitbud-backend

**2. Create the Environment File**
Copy the example environment file to create your own local configuration.

  Bash
  cp .env.example .env

The default values in the .env file are already configured to work with the docker-compose.yml setup, so you don't need to change anything unless you want to use a different database name or password.

**3. Build and Run the Containers**
Use Docker Compose to build the images and start the backend server and the PostgreSQL database.

  Bash
  docker-compose up --build

The --build flag ensures that the Docker image is rebuilt if there are any changes to the Dockerfile or the application's dependencies.

**4. Access the API**
Once the containers are running, the API will be available at http://localhost:8000.

You can access the interactive API documentation (Swagger UI) at:
http://localhost:8000/api/docs

This interface will allow you to interact with all the available API endpoints directly from your browser.

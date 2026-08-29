# AI Learning Path Copilot - Backend

This is the backend service for the AI Learning Path Copilot. It is built using FastAPI, PostgreSQL (with pgvector), and SQLAlchemy, orchestrated via Docker Compose and `uv` for dependency management.

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.14+
- **Database:** PostgreSQL 16 (with pgvector)
- **ORM:** SQLAlchemy 2.0 (Async) + asyncpg
- **Dependency Management:** `uv`
- **Authentication:** JWT + Google OAuth2

## Prerequisites

- **Python:** 3.14 or later (or compatible version managed by `uv`)
- **Docker & Docker Compose:** For running the PostgreSQL database locally
- **uv:** A fast Python package and project manager (install via `pip install uv` or official script)

## Project Setup

Follow these steps to get the backend up and running locally.

### 1. Start the Database

The project requires a PostgreSQL database with the `pgvector` extension. A `docker-compose.yml` is provided at the root of the project workspace.

Start the database using:
```bash
docker-compose up -d
```
This will start a PostgreSQL instance on port `5432`.

### 2. Environment Variables

Navigate to the `backend` directory and create your `.env` file based on the provided example.

```bash
cd backend
cp .env.example .env
```
Ensure the `DATABASE_URL` matches your local docker setup (the default in `.env.example` will work out-of-the-box).

### 3. Install Dependencies

We use `uv` for lightning-fast dependency management.

```bash
# In the backend/ directory
uv sync
```
Or to install directly from `pyproject.toml` into a virtual environment:
```bash
uv venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

uv pip install -e .
```

### 4. Initialize and Seed the Database

Before starting the server, initialize the tables and seed the initial data (skills, courses, prerequisites).

Make sure your virtual environment is active, and run:
```bash
# In the backend/ directory
uv run python -m database.seed
```
*(Note: If you encounter module resolution issues, ensure you are running this command from the `backend/` directory so relative imports work correctly.)*

### 5. Run the Application

Start the FastAPI development server:

```bash
# In the backend/ directory
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# Or using the script defined in pyproject.toml
uv run serve
```

The API will be available at: `http://localhost:8000`

Interactive API documentation (Swagger UI) can be accessed at:
- **Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Project Structure

- `models/`: SQLAlchemy ORM models
- `schemas/`: Pydantic models for request and response validation
- `routes/`: FastAPI API endpoint routers
- `services/`: Core business logic and AI integrations
- `database/`: Database connection and seeding scripts
- `auth/`: JWT and OAuth2 authentication handlers
- `utils/`: Helpers, exceptions, and logging

## Documentation

For a deeper dive into the system's design and requirements, refer to the documentation in the `/docs` folder at the root of the repository:
- `docs/SRS.md` - System Requirements Specification
- `docs/HLD.md` - High-Level Design
- `docs/LLD.md` - Low-Level Design
- `docs/technical_architecture.md` - Architecture specifics
- `docs/database_design.md` - Database schema details

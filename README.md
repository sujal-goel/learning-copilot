# PathPilot AI — AI Learning Path Copilot

PathPilot AI is an adaptive, prerequisite-aware learning roadmap engine. It converts your career goals into a personalized curriculum by combining deterministic skill-graph algorithms with LLM-powered profiling and RAG-based tutoring.

## What It Does

- Conversational onboarding to capture your goals, current skills, and constraints
- Skill-gap analysis against a structured skill graph
- Course recommendations from a curated Coursera catalog
- Topological roadmap DAG generation (prerequisite-aware milestones)
- Persistent progress tracking and mastery levels in PostgreSQL
- AI mentor chat grounded in your roadmap and course metadata
- Adaptive roadmap based on assessments and feedback

## Tech Stack

### Backend
- Python 3.14+ — FastAPI
- PostgreSQL 16 with pgvector
- SQLAlchemy 2.0 (async)
- Google Gemini LLM (with fallbacks)
- JWT + Google OAuth2 authentication

### Frontend
- React 18 + TypeScript
- Vite

### Data
- Coursera course catalog (CSV)
- Role-to-skill mappings (skill_graph.json)
- Job descriptions for role benchmarking

## Repository Layout

```
.
├── ai/                      # LLM/RAG logic and pipelines
│   ├── mentor/              # AI mentor chat (RAG)
│   ├── pipeline/            # End-to-end learning pipeline
│   ├── profile_engine/      # LLM-based profile extraction
│   ├── recommender/         # Hybrid recommendation engine
│   ├── roadmap/             # DAG roadmap generator
│   ├── skill_gap/           # Skill-gap analyzer
│   └── shared/              # Gemini client, config, models
├── backend/                 # FastAPI REST API
│   ├── auth/                # JWT, Google OAuth2, password hashing
│   ├── database/            # Session, seed, init
│   ├── models/              # SQLAlchemy ORM models
│   ├── routes/              # API routers
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic services
│   └── utils/               # Logging, exceptions, rate limiting
├── data/                    # Static datasets
│   ├── coursera-courses.csv
│   ├── skill_graph.json
│   └── job_descriptions_2025.csv
├── data scrapper/           # Coursera scraper (CouReco)
├── docs/                    # SRS, HLD, LLD, architecture, DB design
└── frontend/                # React + Vite SPA
    └── src/
        ├── main.tsx         # App shell and pages
        └── styles.css
```

## Prerequisites

- Python 3.14+ (or let `uv` manage it)
- Docker & Docker Compose (for PostgreSQL + pgvector)
- Node.js 18+ and npm
- `uv` package manager: `pip install uv`
- Google Gemini API key
- (Optional) Google OAuth2 credentials

## Quick Start

### 1. Start PostgreSQL with pgvector

From the repo root:

```bash
docker-compose -f backend/docker-compose.yml up -d
```

This starts a PostgreSQL 16 + pgvector container on port 5432:
- Database: `learning_copilot`
- User: `postgres`
- Password: `postgres`

### 2. Configure Environment

Create a `.env` file in `backend/`:

```bash
cd backend
cp .env.example .env
```

Required keys:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/learning_copilot
SYNC_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/learning_copilot

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI
GEMINI_API_KEY=your-gemini-api-key

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### 3. Install Backend Dependencies

```bash
cd backend
uv sync
```

Or with a venv:

```bash
cd backend
uv venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

uv pip install -e .
```

### 4. Seed the Database

Initialize tables and seed skills, courses, and prerequisites:

```bash
cd backend
uv run python -m database.seed
```

### 5. Run the Backend API

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 7. Run the Frontend Dev Server

```bash
cd frontend
npm run dev
```

The app runs at http://localhost:5173 by default (Vite default). The frontend expects the backend at http://localhost:8000 (set in `frontend/src/main.tsx`).

## API Overview

All endpoints are under `/api/v1` unless noted. Authenticated endpoints require `Authorization: Bearer <JWT>`.

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user (email + password) |
| POST | `/login` | Login and receive JWT |
| POST | `/refresh` | Refresh access token |
| GET | `/google` | Initiate Google OAuth2 flow |
| GET | `/google/callback` | OAuth2 callback, returns JWT |

### Profile (`/api/v1/profile`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/onboard` | Conversational onboarding, LLM extraction |
| GET | `/me` | Get current user's profile |
| PUT | `/me` | Update profile (study hours, goal, etc.) |

### Roadmap (`/api/v1/roadmap`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate` | Generate and persist a new roadmap |
| GET | `/current` | Get current user's active roadmap |
| GET | `/{user_id}` | Get roadmap by user (admin/debug) |

### Progress (`/api/v1/progress`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Record progress on a node |
| GET | `` | Get progress summary for current user |

### Feedback (`/api/v1/feedback`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Submit feedback (TOO_EASY, JUST_RIGHT, TOO_HARD) |

### Chat / AI Mentor (`/api/v1/chat`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send a query to the AI mentor |
| GET | `/chat/history` | Get chat history for current user |

### Assessments (`/api/v1/assessment`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/submit` | Submit assessment answers, get score, trigger adaptation |

### AI Pipeline (`/ai`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate` | Full pipeline: skill gap → recommendations → roadmap |
| POST | `/chat` | Direct Gemini chat (fallback mentor) |

### Supporting Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses/{skill}` | Courses for a skill |
| GET | `/resources/{skill}` | Resources for a skill |
| POST | `/skill-gap/` | Skill gap analysis |

## How the Pipeline Works

1. **Onboarding**: User enters goal, current skills, study hours, and timeline via conversational chat.
2. **Profile Extraction**: LLM extracts structured profile from chat.
3. **Skill Gap Analysis**: Compare required skills (from `skill_graph.json`) against user's current skills.
4. **Course Recommendations**: Hybrid engine filters courses by prerequisites and ranks by relevance.
5. **Roadmap Generation**: LLM builds a DAG of milestones with topological ordering.
6. **Persistence**: Profile, roadmap, and progress stored in PostgreSQL.
7. **Adaptation**: Assessment scores and feedback trigger roadmap mutations.

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app and router registration |
| `backend/database/seed.py` | DB init and seed data |
| `backend/.env.example` | Environment variable template |
| `ai/pipeline/learning_pipeline.py` | End-to-end pipeline orchestrator |
| `ai/shared/gemini_client.py` | Gemini LLM client with fallbacks |
| `ai/skill_gap/analyzer.py` | Skill gap computation |
| `ai/roadmap/roadmap_generator.py` | DAG roadmap builder |
| `ai/mentor/mentor_chat.py` | RAG-based mentor responses |
| `frontend/src/main.tsx` | React app shell, routing, pages |
| `data/skill_graph.json` | Role-to-skill mappings |
| `data/coursera-courses.csv` | Course catalog |

## Development

### Run Backend Tests

```bash
cd backend
uv run pytest
```

(If `pytest` is installed; add to `pyproject.toml` if not.)

### Build Frontend

```bash
cd frontend
npm run build
```

### Docker Compose (Database Only)

```bash
docker-compose -f backend/docker-compose.yml up -d
docker-compose -f backend/docker-compose.yml down
```

## Documentation

In the `docs/` folder:

- `SRS.md` — Software Requirements Specification
- `HLD.md` — High-Level Design (architecture, subsystems)
- `LLD.md` — Low-Level Design (API contracts, schemas)
- `technical_architecture.md` — Architecture deep dive
- `database_design.md` — ERD and table schemas

## Data Sources

- **Coursera Courses**: `data/coursera-courses.csv` (from CouReco scraper)
- **Skill Graph**: `data/skill_graph.json` (role → skills by experience level)
- **Job Descriptions**: `data/job_descriptions_2025.csv` (for role benchmarking)

To update course data, see `data scrapper/couReco/README.md`.

## Security Notes

- Passwords hashed with bcrypt
- JWT for stateless auth; refresh tokens in HttpOnly cookies
- Google OAuth2 supported; password-less accounts for OAuth users
- `.env` is gitignored — never commit secrets

## Troubleshooting

- **Database connection fails**: Ensure Docker container is running (`docker ps`). Check `DATABASE_URL` in `.env`.
- **`uv` not found**: Install with `pip install uv` or use the official installer.
- **Frontend can't reach API**: Verify backend is running on port 8000 and CORS is enabled (it is by default).
- **Gemini errors**: Check `GEMINI_API_KEY` is set and has quota. Fallback models are tried automatically.

## License

MIT

---

Built with FastAPI, React, PostgreSQL, and Google Gemini.

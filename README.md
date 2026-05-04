# GoGym API

Backend API for GoGym — a workout planning, scheduling, and logging application. Built with Python FastAPI, PostgreSQL, and JWT authentication.

GoGym lets users build custom workout plans from a hierarchical exercise library (Categories → Sub-Categories → Exercises), schedule workouts on a calendar, log sets and weights during sessions, and track progress over time. Admins curate a global exercise library while users can create private content and share it with others.

## Related Projects

- [GoGym Mobile App](#) — _coming soon_
- [GoGym Web App](#) — _coming soon_

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose + passlib/bcrypt)
- **Validation**: Pydantic v2

## API Features

- User registration and login with JWT tokens
- Role-based access control (Admin / User)
- Workout inventory CRUD (categories, sub-categories, exercises)
- Workout plan management with multi-day structures
- Calendar-based workout scheduling
- Session logging with weight tracking
- Sharing and admin approval workflows
- Workout history and progress tracking

## Dev Setup

### Prerequisites

- Python 3.10+
- PostgreSQL running locally (or a remote instance)

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd gogym-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
DATABASE_URL=postgresql://user:password@localhost:5432/gogym
JWT_SECRET=change-me-to-a-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Create the database

```bash
createdb gogym
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API docs at `http://127.0.0.1:8000/docs`.

## Database Migrations (Alembic)

Alembic manages database schema changes. Migration files live in `alembic/versions/`.

Apply all pending migrations:

```bash
alembic upgrade head
```

Roll back the last migration:

```bash
alembic downgrade -1
```

After changing a model in `app/models/`, generate a new migration:

```bash
alembic revision --autogenerate -m "describe your change"
```

Check which migration the database is currently on:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

## Running Tests

```bash
pytest
```

## Project Structure

```
app/
├── main.py            # FastAPI app, lifespan, exception handlers
├── config.py          # Settings from .env
├── database.py        # SQLAlchemy engine and session
├── dependencies.py    # Auth and DB dependencies
├── exceptions.py      # Custom exception classes
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response schemas
├── services/          # Business logic layer
└── routes/            # API endpoint definitions
```

## Dependencies

| Package | Purpose |
|---|---|
| fastapi | Web framework for building the API |
| uvicorn | ASGI server to run the FastAPI app |
| sqlalchemy | ORM for database models and queries |
| psycopg2-binary | PostgreSQL database driver |
| alembic | Database schema migration tool |
| python-jose[cryptography] | JWT token creation and validation |
| passlib[bcrypt] | Password hashing using bcrypt |
| bcrypt | Bcrypt implementation (pinned for passlib compatibility) |
| python-dotenv | Loads environment variables from `.env` files |
| pydantic-settings | Settings management with env var support |
| httpx | HTTP client (used for testing with FastAPI's TestClient) |
| pytest | Test runner |
| pytest-asyncio | Async test support for pytest |
| hypothesis | Property-based testing library |
| factory-boy | Test data factories for generating model instances |

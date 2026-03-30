# FastAPI Implementation Documentation — GoGym MVP Backend

> A step-by-step guide to building a production-ready FastAPI backend from scratch.
> Covers project setup, database integration, authentication, CRUD APIs, and more.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Prerequisites](#2-prerequisites)
3. [Task 1: Project Scaffolding and Configuration](#3-task-1-project-scaffolding-and-configuration)
   - [1.1 Create the Project Directory Structure](#31-create-the-project-directory-structure)
   - [1.2 Install Dependencies](#32-install-dependencies)
   - [1.3 Application Configuration](#33-application-configuration)
   - [1.4 Database Connection](#34-database-connection)
   - [1.5 FastAPI App Factory](#35-fastapi-app-factory)
   - [1.6 Alembic Migrations Setup](#36-alembic-migrations-setup)

---

## 1. Project Overview

**GoGym** is a mobile-first workout planning, scheduling, and logging application. This document walks through building the backend API using:

- **FastAPI** — modern, high-performance Python web framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM (Object-Relational Mapper) for database interactions
- **Alembic** — database migration tool (tracks schema changes over time)
- **JWT** — JSON Web Tokens for authentication
- **Pydantic** — data validation and serialization

### Architecture Pattern: Layered Architecture

We organize code into layers where each layer has a single responsibility:

```
Client Request
    ↓
Routes (app/routes/)      → Handle HTTP requests/responses (thin layer)
    ↓
Services (app/services/)  → Business logic (the "brains")
    ↓
Models (app/models/)      → Database table definitions
    ↓
PostgreSQL Database
```

**Why layers?** Each layer only talks to the one below it. This makes code easier to test, debug, and modify without breaking other parts.

---

## 2. Prerequisites

- Python 3.10+
- PostgreSQL installed and running
- A terminal/command line
- A code editor (VS Code, Kiro, etc.)

### 2.1 Installing PostgreSQL (macOS)

**Why?** Our API uses PostgreSQL as its database. You need it running locally for development.

**Option A: Homebrew (recommended for macOS)**

```bash
# Install PostgreSQL 16
brew install postgresql@16

# Start it as a background service (auto-starts on boot)
brew services start postgresql@16

# Verify it's running
psql --version
```

After installation, create the database for our project:

```bash
createdb gogym
```

To verify it worked:

```bash
psql -d gogym -c "SELECT 1;"
```

You should see a result with `1`. If so, Postgres is ready.

**Your `.env` DATABASE_URL will look like:**
```
DATABASE_URL=postgresql://your_mac_username:@localhost:5432/gogym
```

> **Note:** On macOS with Homebrew, PostgreSQL often creates a default user matching your
> macOS username with no password. So the URL might just be
> `postgresql://libintom:@localhost:5432/gogym` (empty password).

**Option B: Docker**

If you prefer containers:

```bash
docker run --name gogym-postgres \
  -e POSTGRES_USER=libin \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=gogym \
  -p 5432:5432 \
  -d postgres:16
```

Your `.env` would then be:
```
DATABASE_URL=postgresql://libin:yourpassword@localhost:5432/gogym
```

**Option C: Cloud-hosted (Supabase, Neon, Railway)**

All have free tiers. You get a connection string from their dashboard and paste it into `.env`. Good for when you don't want to manage Postgres locally.

**Useful PostgreSQL commands:**

```bash
createdb gogym          # Create a database
dropdb gogym            # Delete a database (careful!)
psql -d gogym           # Connect to the database interactively
psql -l                 # List all databases
brew services stop postgresql@16   # Stop the Postgres service
brew services start postgresql@16  # Start it again
```

---

## 3. Task 1: Project Scaffolding and Configuration

### 3.1 Create the Project Directory Structure

**Why?** A well-organized directory structure keeps your codebase maintainable as it grows. Each directory has a clear purpose.

```bash
# Navigate to your project root
cd gogym/gogym-api

# Create all directories at once
# -p flag creates parent directories as needed
mkdir -p app/models app/schemas app/services app/routes tests alembic/versions
```

**What each directory is for:**

| Directory | Purpose |
|---|---|
| `app/` | Main application package — all your source code lives here |
| `app/models/` | SQLAlchemy models — Python classes that map to database tables |
| `app/schemas/` | Pydantic schemas — define the shape of request/response JSON |
| `app/services/` | Business logic — validation, authorization, data processing |
| `app/routes/` | API endpoints — thin layer that handles HTTP and calls services |
| `tests/` | All test files |
| `alembic/` | Database migration scripts — tracks schema changes over time |
| `alembic/versions/` | Individual migration files (auto-generated) |

**Make directories importable as Python packages:**

Python needs `__init__.py` files to treat directories as packages you can import from. They can be empty.

```bash
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/routes/__init__.py
touch tests/__init__.py
```

**Verify the structure:**

```bash
ls -R app/
```

Expected output:
```
app/:
__init__.py  config.py  models/  routes/  schemas/  services/

app/models:
__init__.py

app/routes:
__init__.py

app/schemas:
__init__.py

app/services:
__init__.py
```

> **Note:** FastAPI doesn't have a built-in scaffolding CLI like Django (`django-admin startproject`)
> or Alembic (`alembic init`). Community tools like `cookiecutter` with FastAPI templates exist,
> but building manually helps you understand every piece.


### 3.2 Install Dependencies

**Why?** We need external libraries for our API. Each one serves a specific purpose.

**Step 1: Create a virtual environment**

A virtual environment isolates your project's dependencies from your system Python. This prevents version conflicts between projects.

```bash
# Create a virtual environment named .venv
python3 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Your terminal prompt should now show (.venv) at the beginning
```

**Step 2: Create `requirements.txt`**

This file lists all the packages your project needs. Create it in your project root (`gogym/gogym-api/requirements.txt`):

```
fastapi                  # Web framework — handles routing, validation, docs
uvicorn                  # ASGI server — runs your FastAPI app
sqlalchemy               # ORM — maps Python classes to database tables
psycopg2-binary          # PostgreSQL driver — lets SQLAlchemy talk to Postgres
alembic                  # Database migrations — tracks schema changes
python-jose[cryptography] # JWT token creation and verification
passlib[bcrypt]          # Password hashing using bcrypt algorithm
python-dotenv            # Loads environment variables from .env files
pydantic-settings        # Pydantic extension for app configuration
httpx                    # HTTP client — used for testing FastAPI endpoints
pytest                   # Test runner
pytest-asyncio           # Async test support for pytest
hypothesis               # Property-based testing — generates random test inputs
factory-boy              # Test data factories — creates realistic test objects
```

**Step 3: Install the dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Create `.env.example`**

This file documents what environment variables your app needs, with placeholder values. Developers copy this to `.env` and fill in real values. Never commit `.env` itself (it has secrets).

Create `gogym/gogym-api/.env.example`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/gogym
JWT_SECRET=change-me-to-a-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Step 5: Create `pyproject.toml`**

This is the modern Python way to define project metadata and tool configuration. Create `gogym/gogym-api/pyproject.toml`:

```toml
[project]
name = "gogym-api"
version = "0.1.0"
description = "GoGym MVP Backend API — workout planning, scheduling, and logging"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]          # Tell pytest where to find tests
asyncio_mode = "auto"          # Auto-detect async tests
filterwarnings = ["ignore::DeprecationWarning"]

[tool.hypothesis]
max_examples = 100             # Each property test runs at least 100 random inputs
```

**Step 6: Set up your actual `.env` file**

```bash
cp .env.example .env
# Now edit .env with your real PostgreSQL credentials
```

---

### 3.3 Application Configuration

**Why?** We need a central place to load and validate configuration values (database URL, JWT secret, etc.) from environment variables. Pydantic's `BaseSettings` does this with type validation built in.

**Create `app/config.py`:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str                    # PostgreSQL connection string
    jwt_secret: str                      # Secret key for signing JWT tokens
    jwt_algorithm: str = "HS256"         # Algorithm for JWT (default: HS256)
    access_token_expire_minutes: int = 60  # Token expiry in minutes (default: 60)

    # Tell Pydantic to load values from a .env file
    model_config = SettingsConfigDict(env_file=".env")


# Create a singleton instance — import this everywhere
settings = Settings()
```

**How it works:**

1. `BaseSettings` automatically reads environment variables matching the field names (case-insensitive)
2. `SettingsConfigDict(env_file=".env")` also loads from a `.env` file as a fallback
3. Fields with defaults (`jwt_algorithm`, `access_token_expire_minutes`) are optional in `.env`
4. Fields without defaults (`database_url`, `jwt_secret`) are required — the app won't start without them
5. Pydantic validates types automatically — if `access_token_expire_minutes` isn't an integer, you get a clear error at startup

**Key concept — Singleton pattern:** We create `settings = Settings()` once at module level. Every file that does `from app.config import settings` gets the same instance. This avoids reading `.env` multiple times.

**Verify it works:**

```bash
python3 -c "from app.config import settings; print(settings.database_url)"
# Expected: postgresql://your_username:@localhost:5432/gogym
```

If it prints your database URL, the config module is wired up correctly.

---

### 3.4 Database Connection

**Why?** We need to set up SQLAlchemy to connect to PostgreSQL. This involves three things: an engine (the connection), a session factory (for per-request database sessions), and a base class (that all our models inherit from).

**Create `app/database.py`:**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# Engine — manages the actual database connection pool
engine = create_engine(settings.database_url)

# SessionLocal — a factory that creates new database sessions
# autocommit=False: we control when to commit (explicit is better than implicit)
# autoflush=False: we control when to flush changes to DB (prevents surprises)
sessionmaker = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Base — every database model will inherit from this
# SQLAlchemy uses this to track all your models and their table definitions
class Base(DeclarativeBase):
    pass
```

**Key concepts:**

- **Engine**: Think of it as the connection manager. It maintains a pool of database connections and hands them out as needed.
- **Session**: A "workspace" for database operations. You query, add, update within a session, then commit or rollback. Each API request gets its own session.
- **DeclarativeBase**: The modern SQLAlchemy 2.0 way to define a base class. All your models (User, Exercise, etc.) will inherit from `Base`, which lets SQLAlchemy know about them.

**Verify it works:**

```bash
python3 -c "from app.database import engine, SessionLocal, Base; print('Engine:', engine); print('Base tables:', Base.metadata.tables)"
# Expected:
# Engine: Engine(postgresql://your_username:***@localhost:5432/gogym)
# Base tables: FacadeDict({})
```

The engine shows your connection (password masked for security). `FacadeDict({})` means no tables registered yet — that's expected since we haven't created any models.

---

### 3.5 FastAPI App Factory

**Why?** This is the entry point of your application. It creates the FastAPI instance, verifies the database is reachable on startup, and registers all your route modules.

**First, create empty routers for each route module:**

Each route file gets a simple `APIRouter` with a prefix. These are placeholders we'll fill in later.

`app/routes/auth.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
```

`app/routes/inventory.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/inventory", tags=["inventory"])
```

`app/routes/plan.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/plans", tags=["plans"])
```

`app/routes/schedule.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/schedule", tags=["schedule"])
```

`app/routes/session.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])
```

`app/routes/sharing.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/sharing", tags=["sharing"])
```

**Why prefixes?** The prefix means all endpoints in `auth.py` will start with `/auth` (e.g., `/auth/register`, `/auth/login`). The `tags` group endpoints in the auto-generated API docs.

**Quick bash script to create all 6 at once:**

```bash
for module in auth inventory plan schedule session sharing; do
  prefix=$module
  case $module in
    plan) prefix="plans" ;;
    session) prefix="sessions" ;;
  esac
  cat > app/routes/${module}.py << EOF
from fastapi import APIRouter

router = APIRouter(prefix="/${prefix}", tags=["${prefix}"])
EOF
done
```

This loops through the module names, handles the plural prefixes (`plan` → `/plans`, `session` → `/sessions`), and writes each file.

**Verify with:**

```bash
head app/routes/*.py
```

**Now create `app/main.py`:**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routes.auth import router as auth_router
from app.routes.inventory import router as inventory_router
from app.routes.plan import router as plan_router
from app.routes.schedule import router as schedule_router
from app.routes.session import router as session_router
from app.routes.sharing import router as sharing_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown of the application."""
    # STARTUP: Verify database connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise RuntimeError(
            f"Failed to connect to the database on startup: {exc}"
        ) from exc
    yield
    # SHUTDOWN: cleanup would go here (if needed)


app = FastAPI(title="GoGym API", lifespan=lifespan)

# Register all route modules
app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(plan_router)
app.include_router(schedule_router)
app.include_router(session_router)
app.include_router(sharing_router)
```

**Key concepts:**

- **Lifespan context manager**: Code before `yield` runs on startup, code after runs on shutdown. We use startup to verify the DB is reachable — fail fast if it's not.
- **`text("SELECT 1")`**: The simplest possible query to check if the database is alive.
- **`include_router()`**: Registers a group of endpoints with the app. This keeps `main.py` clean — each domain (auth, inventory, etc.) has its own file.

**Test it:**

```bash
# Make sure your .env has a valid DATABASE_URL, then:
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs to see the auto-generated Swagger UI
```

---

### 3.6 Alembic Migrations Setup

**Why?** As your app evolves, your database schema changes (new tables, new columns, etc.). Alembic tracks these changes as versioned migration scripts, so you can apply them consistently across environments (dev, staging, production) and roll back if needed.

**Think of Alembic as git for your database schema.** With git, you track code changes over time. Alembic does the same for your database tables.

**Real-world example:** You start with a `User` table with `email` and `password`. A month later, you need to add a `phone_number` column. You can't just change your Python model and hope the database updates itself — Postgres doesn't know about your Python code. You need to actually run `ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)`.

Alembic automates this:
1. You change your SQLAlchemy model in Python
2. Run `alembic revision --autogenerate -m "add phone_number"` — Alembic compares your models to the actual DB and generates a migration script
3. Run `alembic upgrade head` — applies the change
4. If something breaks: `alembic downgrade -1` — rolls it back

**Without Alembic**, you'd be writing raw SQL by hand and hoping everyone runs the same commands in the same order. That gets messy fast.

**Step 1: Initialize Alembic**

```bash
# From your project root (gogym/gogym-api/)
alembic init alembic
```

This creates:
- `alembic.ini` — main config file
- `alembic/env.py` — migration environment (connects to your DB)
- `alembic/script.py.mako` — template for new migration files
- `alembic/versions/` — where migration scripts are stored

**Step 2: Configure `alembic/env.py`**

The key change is telling Alembic about your models and database URL. Edit `alembic/env.py`:

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import YOUR config and models
from app.config import settings
from app.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# THIS IS THE KEY LINE — tells Alembic about your models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live database connection."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live database connection."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url  # Override from .env
    connectable = engine_from_config(
        configuration,
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
```

**What's happening:**
- `target_metadata = Base.metadata` — Alembic inspects this to know what tables/columns your models define
- `settings.database_url` overrides whatever is in `alembic.ini` — single source of truth for the DB URL
- **Offline mode**: Generates SQL without connecting (useful for review)
- **Online mode**: Connects to DB and applies changes directly

**Step 3: Update `alembic.ini`**

The `sqlalchemy.url` in `alembic.ini` is just a placeholder since `env.py` overrides it:

```ini
# In alembic.ini, this line exists but gets overridden by env.py:
sqlalchemy.url = driver://user:pass@localhost/dbname
```

**Common Alembic commands you'll use later:**

```bash
# Generate a migration from model changes (after creating/modifying models)
alembic revision --autogenerate -m "description of change"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# See current migration state
alembic current
```

**Verify Alembic is configured correctly:**

```bash
alembic current
# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

`PostgresqlImpl` confirms Alembic connected to Postgres. `transactional DDL` means schema changes are wrapped in transactions — if a migration fails halfway, it rolls back cleanly. No current revision is expected since we haven't created any migrations yet.

---

## What's Next?

With the project scaffolding complete, the next tasks are:
- **Task 2**: Verify the setup (checkpoint)
- **Task 3**: Create database models (User, Category, Exercise, etc.)
- **Task 4**: Custom exceptions and error handling
- **Task 5**: Authentication (register, login, JWT)

Each task builds on the previous one — that's the beauty of the layered approach.

---

## 4. Task 3: Database Models and Migrations

This is where we define the actual tables that PostgreSQL will create. Each model is a Python class that maps to a database table.

### 4.1 User Model (`app/models/user.py`)

**Why?** Every app needs users. This model stores account info, hashed passwords, and roles.

```python
import uuid
from datetime import datetime

from sqlalchemy import Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum("user", "admin", name="user_role"),
        nullable=False,
        default="user",
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
```

**Key concepts:**

- `__tablename__ = "users"` — the actual table name in Postgres. Convention is lowercase plural.
- `Mapped[uuid.UUID]` — SQLAlchemy 2.0 style type annotations. Tells both Python and SQLAlchemy the column type.
- `uuid.uuid4` as default — random UUIDs are better than auto-incrementing integers for APIs (don't leak user count).
- `server_default=func.now()` — the database generates the timestamp, not Python. More reliable (uses DB server's clock).
- `onupdate=func.now()` — automatically updates `updated_at` whenever the row changes.
- `Enum("user", "admin")` — restricts the `role` column to only these two values at the database level.

**Verify:**

```bash
python3 -c "from app.models.user import User; print(User.__tablename__, User.__table__.columns.keys())"
# Expected: users ['id', 'email', 'hashed_password', 'name', 'role', 'created_at', 'updated_at']
```

### 4.2 Inventory Models (`app/models/inventory.py`)

**Why?** The workout inventory is a hierarchy: Category → SubCategory → Exercise. For example: "Upper Body" → "Chest" → "Bench Press". Three models in one file since they're tightly related.

> **Python version note:** If you're on Python 3.9, use `Optional[str]` from `typing` instead of `str | None`.
> The `type | None` syntax requires Python 3.10+.

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope"),
        nullable=False,
        default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    subcategories = relationship(
        "SubCategory", back_populates="category", cascade="all, delete-orphan"
    )


class SubCategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope",
             create_type=False),
        nullable=False,
        default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status",
             create_type=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    category = relationship("Category", back_populates="subcategories")
    exercises = relationship(
        "Exercise", back_populates="subcategory", cascade="all, delete-orphan"
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_muscles: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    subcategory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subcategories.id"), nullable=False
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope",
             create_type=False),
        nullable=False,
        default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status",
             create_type=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    subcategory = relationship("SubCategory", back_populates="exercises")
```

**Key concepts:**

- `ForeignKey("users.id")` — creates a relationship to the `users` table. The database enforces this — you can't set an `owner_id` that doesn't exist.
- `relationship(...)` — the Python-side relationship. `category.subcategories` gives you a list of child SubCategories.
- `cascade="all, delete-orphan"` — deleting a Category automatically deletes its SubCategories, which cascades to Exercises.
- `back_populates` — links both sides: `category.subcategories` and `subcategory.category` both work.
- `create_type=False` — since `sharing_scope` and `approval_status` Enum types were already created by Category, we tell SQLAlchemy not to create them again.
- `Optional[str]` — means the column is nullable (can be empty/null).

**Verify:**

```bash
python3 -c "from app.models.inventory import Category, SubCategory, Exercise; \
print('Category:', Category.__table__.columns.keys()); \
print('SubCategory:', SubCategory.__table__.columns.keys()); \
print('Exercise:', Exercise.__table__.columns.keys())"
```

### 4.3 Workout Plan Models (`app/models/plan.py`)

**Why?** Workout plans are structured as: Plan → Days → Exercises per day. A "Push/Pull/Legs" plan has 3 days, each with different exercises.

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    num_days: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    sharing_scope: Mapped[str] = mapped_column(
        Enum("private", "shared", "global", name="sharing_scope", create_type=False),
        nullable=False, default="private",
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "approved", "rejected", name="approval_status", create_type=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    days = relationship("PlanDay", back_populates="plan", cascade="all, delete-orphan")


class PlanDay(Base):
    __tablename__ = "plan_days"
    __table_args__ = (
        UniqueConstraint("plan_id", "day_number", name="uq_plan_day_number"),
    )
    # ... columns: id, plan_id, day_number, name, created_at, updated_at
    # ... relationships: plan, exercises


class PlanDayExercise(Base):
    __tablename__ = "plan_day_exercises"
    __table_args__ = (
        UniqueConstraint("plan_day_id", "display_order", name="uq_plan_day_display_order"),
    )
    # ... columns: id, plan_day_id, exercise_id, display_order, prescribed_sets, prescribed_reps, created_at, updated_at
```

**Key concept — UniqueConstraint:**
- `UniqueConstraint("plan_id", "day_number")` — can't have two Day 1s in the same plan
- `UniqueConstraint("plan_day_id", "display_order")` — can't have two exercises at position #1 on the same day
- `__table_args__` is how you add table-level constraints (vs column-level `unique=True`)

### 4.4 Schedule Model (`app/models/schedule.py`)

Maps calendar dates to plan days. `UniqueConstraint("user_id", "scheduled_date")` enforces one workout per day per user — the database rejects duplicates.

### 4.5 Session and SetLog Models (`app/models/session.py`)

Tracks actual workout performance. Key features:
- `CheckConstraint("weight > 0")` — database rejects zero/negative weights (defense in depth)
- `Numeric(7, 2)` — precise decimal storage for weights (avoids floating-point rounding)
- Session status: `in_progress` → `completed` or `partial`

### 4.6 Sharing Model (`app/models/sharing.py`)

Generic sharing table — `item_type` + `item_id` can point to any shareable resource (category, exercise, plan).

### 4.7 Register Models and Generate Migration

**Critical step:** Alembic only knows about models that have been imported. You must register them.

**`app/models/__init__.py`:**

```python
from app.models.user import User
from app.models.inventory import Category, SubCategory, Exercise
from app.models.plan import WorkoutPlan, PlanDay, PlanDayExercise
from app.models.schedule import Schedule
from app.models.session import WorkoutSession, SetLog
from app.models.sharing import SharedItem
```

**Also add this import to `alembic/env.py`** (right after `from app.database import Base`):

```python
import app.models  # noqa: F401 — ensures all models are registered with Base
```

> **Gotcha:** Without this import, `alembic revision --autogenerate` generates an empty migration
> because `Base.metadata` has no tables registered. This is a common mistake that's hard to debug.

**Verify all models are registered:**

```bash
python3 -c "from app.models import *; from app.database import Base; print(list(Base.metadata.tables.keys()))"
# Expected: ['users', 'categories', 'subcategories', 'exercises', 'workout_plans',
#            'plan_days', 'plan_day_exercises', 'schedules', 'workout_sessions',
#            'set_logs', 'shared_items']
```

**Generate and apply the migration:**

```bash
# Generate migration script
alembic revision --autogenerate -m "initial schema"

# Apply it to create tables in Postgres
alembic upgrade head

# Verify tables exist
psql -d gogym -c "\dt"
# Should show all 11 tables + alembic_version (12 rows total)
```

---

## 5. Task 4: Custom Exceptions and Error Handling

**Why?** Every API needs consistent error responses. Instead of scattering HTTP status codes throughout your routes, we define custom exception classes and register global handlers. Any service can just `raise NotFoundError("User not found")` and the right HTTP response happens automatically.

### 5.1 Custom Exception Classes (`app/exceptions.py`)

Create this at `app/exceptions.py` — directly in the `app/` directory (not in a subdirectory). Exceptions are cross-cutting: used by services, routes, and the main app, so they live at the root level.

```python
class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class ForbiddenError(Exception):
    def __init__(self, detail: str = "You do not have permission to modify this resource"):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Resource already exists"):
        self.detail = detail
```

Each maps to an HTTP status code:
- `NotFoundError` → 404
- `ForbiddenError` → 403
- `ConflictError` → 409

### 5.2 Register Exception Handlers in `app/main.py`

Add these imports at the top:

```python
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import NotFoundError, ForbiddenError, ConflictError
```

Then add handlers after `app = FastAPI(...)` but before the `include_router` calls:

```python
logger = logging.getLogger(__name__)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"},
    )
```

**Key points:**
- The global `Exception` handler catches anything unexpected — logs the full traceback server-side but returns a generic message to the client (never leak internal details)
- `@app.exception_handler(...)` is FastAPI's way of registering these globally
- Any service or route can now just `raise NotFoundError("User not found")` and the right response happens

**Verify:**

```bash
uvicorn app.main:app --reload
curl http://localhost:8000/nonexistent
# Expected: {"detail":"Not Found"}
```

---

## 6. Task 5: Authentication and Authorization

### 6.1 Database Session Dependency (`app/dependencies.py`)

**Why?** Each API request needs its own database session with automatic cleanup.

```python
from app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db          # ← pause, give session to route
        db.commit()       # ← route succeeded, save changes
    except Exception:
        db.rollback()     # ← route crashed, undo everything
        raise
    finally:
        db.close()        # ← always close the connection
```

**How `yield` works (the sandwich pattern):**
1. Code before `yield` runs when request arrives (setup)
2. `yield db` pauses, hands the session to your route function
3. Your route does its work
4. Code after `yield` runs when route finishes (cleanup)
5. If the route crashes, the `except` block catches it and rolls back

### 6.2 Auth Pydantic Schemas (`app/schemas/auth.py`)

Define the shape of request/response JSON for auth endpoints:

```python
import uuid
from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    model_config = {"from_attributes": True}  # allows reading from SQLAlchemy objects

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

### 6.3 Auth Service (`app/services/auth.py`)

Business logic for password hashing, JWT creation, register, and login:

```python
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.exceptions import ConflictError
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])  # bcrypt 72-byte limit

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def register_user(db: Session, email: str, password: str, name: str) -> tuple:
    if db.query(User).filter(User.email == email).first():
        raise ConflictError("Email already registered")
    user = User(email=email, hashed_password=hash_password(password), name=name)
    db.add(user)
    db.flush()  # get the generated UUID without committing
    return create_access_token({"sub": str(user.id)}), user

def login_user(db: Session, email: str, password: str) -> tuple:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
    return create_access_token({"sub": str(user.id)}), user
```

> **Gotcha — passlib + bcrypt 5.x incompatibility:** `passlib` doesn't support `bcrypt` 5.x.
> Pin bcrypt in `requirements.txt`: `bcrypt==4.2.1`

### 6.4 Auth Routes (`app/routes/auth.py`)

Wire schemas and service into HTTP endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.services.auth import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    token, user = register_user(db, request.email, request.password, request.name)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))

@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        token, user = login_user(db, request.email, request.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))
```

### 6.5 Auth Dependencies (`app/dependencies.py`)

Add JWT validation and role checking (append to existing file):

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret,
                             algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user
```

**Verify the full auth flow:**

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret123", "name": "Test User"}'
# Expected: 201 with access_token and user info

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret123"}'
# Expected: 200 with access_token

# Duplicate email
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "other", "name": "Dup"}'
# Expected: 409 {"detail": "Email already registered"}
```

---

*Document maintained as part of the GoGym MVP Backend implementation. Updated as new tasks are completed.*

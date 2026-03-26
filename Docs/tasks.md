# Implementation Plan: GoGym MVP Backend API

## Overview

Build the GoGym MVP Backend API incrementally using Python FastAPI, PostgreSQL, SQLAlchemy ORM, Alembic migrations, and JWT authentication. Tasks are ordered so each step builds on the previous one, starting from project scaffolding through to workout history and progress tracking. The plan follows the layered architecture: config → database → models → schemas → services → routes → tests.

## Tasks

- [ ] 1. Project scaffolding and configuration
  - [ ] 1.1 Create the project directory structure and install dependencies
    - Create the full directory tree as defined in the design: `app/`, `app/models/`, `app/schemas/`, `app/services/`, `app/routes/`, `tests/`, `alembic/`
    - Create `requirements.txt` with: fastapi, uvicorn, sqlalchemy, psycopg2-binary, alembic, python-jose, passlib[bcrypt], python-dotenv, pydantic[dotenv], pydantic-settings, httpx, pytest, pytest-asyncio, hypothesis, factory-boy
    - Create `pyproject.toml` with project metadata and pytest configuration
    - Create `.env.example` with placeholder values for DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    - Add all `__init__.py` files to make packages importable
    - _Requirements: 1.1, 1.2_

  - [ ] 1.2 Implement application configuration (`app/config.py`)
    - Create `Settings` class using Pydantic `BaseSettings` with fields: `database_url`, `jwt_secret`, `jwt_algorithm` (default "HS256"), `access_token_expire_minutes` (default 60)
    - Configure `model_config = SettingsConfigDict(env_file=".env")` to load from `.env` file
    - Export a singleton `settings = Settings()` instance
    - _Requirements: 1.2_

  - [ ] 1.3 Implement database connection (`app/database.py`)
    - Create SQLAlchemy `engine` from `settings.database_url`
    - Create `SessionLocal` session factory
    - Create `Base` declarative base class for all models
    - _Requirements: 1.3_

  - [ ] 1.4 Implement FastAPI app factory with startup verification (`app/main.py`)
    - Create the FastAPI application instance
    - Implement a lifespan context manager that verifies DB connectivity on startup and raises a descriptive error if the connection fails
    - Register all route modules (initially empty routers)
    - _Requirements: 1.5_

  - [ ] 1.5 Initialize Alembic for database migrations
    - Run `alembic init alembic` to generate the Alembic directory structure
    - Configure `alembic/env.py` to import `Base.metadata` from `app/database.py` and `settings.database_url` from `app/config.py`
    - Move `alembic.ini` to project root and update `sqlalchemy.url` to read from config
    - _Requirements: 1.4_

- [ ] 2. Checkpoint - Verify project setup
  - Ensure the FastAPI app starts without errors, Alembic is configured, and the database connection is verified. Ask the user if questions arise.

- [ ] 3. Database models and migrations
  - [ ] 3.1 Create the User model (`app/models/user.py`)
    - Define `User` model with columns: id (UUID PK), email (unique, indexed), hashed_password, name, role (Enum: "user", "admin", default "user"), created_at, updated_at
    - Use `mapped_column` (SQLAlchemy 2.0 style)
    - _Requirements: 3.1, 3.3_

  - [ ] 3.2 Create inventory models (`app/models/inventory.py`)
    - Define `Category` model: id, name, owner_id (FK → User, nullable), sharing_scope (Enum: private/shared/global, default private), approval_status (Enum: pending/approved/rejected, nullable), created_at, updated_at
    - Define `SubCategory` model: id, name, category_id (FK → Category), owner_id, sharing_scope, approval_status, created_at, updated_at
    - Define `Exercise` model: id, name, description, target_muscles, subcategory_id (FK → SubCategory), owner_id, sharing_scope, approval_status, created_at, updated_at
    - Set up cascade delete: Category → SubCategory → Exercise
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6_

  - [ ] 3.3 Create workout plan models (`app/models/plan.py`)
    - Define `WorkoutPlan` model: id, name, description, num_days, owner_id, sharing_scope, approval_status, created_at, updated_at
    - Define `PlanDay` model: id, plan_id (FK → WorkoutPlan), day_number, name, created_at, updated_at. Unique constraint on (plan_id, day_number)
    - Define `PlanDayExercise` model: id, plan_day_id (FK → PlanDay), exercise_id (FK → Exercise), display_order, prescribed_sets, prescribed_reps, created_at, updated_at. Unique constraint on (plan_day_id, display_order)
    - Set up cascade delete: WorkoutPlan → PlanDay → PlanDayExercise
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [ ] 3.4 Create schedule model (`app/models/schedule.py`)
    - Define `Schedule` model: id, user_id (FK → User), plan_day_id (FK → PlanDay), plan_id (FK → WorkoutPlan), scheduled_date, created_at, updated_at
    - Unique constraint on (user_id, scheduled_date) to enforce one workout per day
    - _Requirements: 3.1, 3.2, 10.5_

  - [ ] 3.5 Create session and set log models (`app/models/session.py`)
    - Define `WorkoutSession` model: id, user_id (FK → User), plan_day_id (FK → PlanDay), session_date, status (Enum: in_progress/completed/partial, default in_progress), started_at, completed_at (nullable), created_at, updated_at
    - Define `SetLog` model: id, session_id (FK → WorkoutSession), exercise_id (FK → Exercise), set_number, reps_performed, weight (Decimal(7,2), Check > 0), created_at. Unique constraint on (session_id, exercise_id, set_number)
    - Set up cascade delete: WorkoutSession → SetLog
    - _Requirements: 3.1, 3.2, 3.3, 12.3_

  - [ ] 3.6 Create sharing model (`app/models/sharing.py`)
    - Define `SharedItem` model: id, item_type (Enum: category/subcategory/exercise/workout_plan), item_id (UUID), shared_with_user_id (FK → User), shared_by_user_id (FK → User), created_at
    - Unique constraint on (item_type, item_id, shared_with_user_id)
    - _Requirements: 3.1, 6.1_

  - [ ] 3.7 Register all models and generate initial Alembic migration
    - Import all models in `app/models/__init__.py` so Base.metadata sees them
    - Run `alembic revision --autogenerate -m "initial schema"` to generate the migration
    - Run `alembic upgrade head` to apply the migration
    - _Requirements: 3.4_

  - [ ]* 3.8 Write property tests for model field invariants
    - **Property 8: Model field invariants** — verify created_at/updated_at are non-null, sharing_scope and owner_id are consistent with creator role
    - **Validates: Requirements 3.3, 3.5**

- [ ] 4. Custom exceptions and error handling
  - [ ] 4.1 Create custom exception classes (`app/exceptions.py`)
    - Define `NotFoundError`, `ForbiddenError`, `ConflictError` exception classes
    - Register FastAPI exception handlers in `app/main.py` that convert these to proper HTTP responses (404, 403, 409) with the JSON error format from the design
    - Add a global catch-all exception handler that returns 500 with a generic message and logs the traceback
    - _Requirements: 2.3, 2.4, 2.5, 2.6, 5.5, 10.5, 16.3_

- [ ] 5. Authentication dependencies and auth service
  - [ ] 5.1 Implement database session dependency (`app/dependencies.py`)
    - Create `get_db()` generator that yields a DB session per request and handles commit/rollback in a try/finally block
    - _Requirements: 1.3, 16.3_

  - [ ] 5.2 Implement auth service (`app/services/auth.py`)
    - Implement `hash_password(password)` using bcrypt via passlib
    - Implement `verify_password(plain, hashed)` using bcrypt
    - Implement `create_access_token(data, expires_delta)` using python-jose with configurable expiration from settings
    - Implement `register_user(db, email, password, name)` — check for duplicate email (raise ConflictError), hash password, create User, return token
    - Implement `login_user(db, email, password)` — verify credentials (raise 401 on failure), return token
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.8, 17.1, 17.2_

  - [ ] 5.3 Implement auth dependencies (`app/dependencies.py`)
    - Implement `get_current_user(token)` — decode JWT, fetch User from DB, raise 401 if invalid/expired/malformed
    - Implement `require_admin(user)` — raise 403 if user.role != "admin"
    - _Requirements: 2.5, 2.6, 2.7_

  - [ ] 5.4 Implement auth Pydantic schemas (`app/schemas/auth.py`)
    - Define `UserRegisterRequest` (email, password, name), `UserLoginRequest` (email, password)
    - Define `UserResponse` (id, email, name, role), `TokenResponse` (access_token, token_type, user)
    - All schemas use snake_case field naming
    - _Requirements: 14.1, 14.2_

  - [ ] 5.5 Implement auth routes (`app/routes/auth.py`)
    - `POST /auth/register` — validate input, call auth service, return TokenResponse or 409/422
    - `POST /auth/login` — validate input, call auth service, return TokenResponse or 401/422
    - Register router with prefix `/auth`
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 5.6 Write property tests for authentication
    - **Property 1: Authentication round-trip** — register then login returns valid JWT decoding to same user
    - **Validates: Requirements 2.1, 2.2**

  - [ ]* 5.7 Write property test for duplicate email rejection
    - **Property 2: Duplicate email rejection** — re-registering same email returns 409, user count unchanged
    - **Validates: Requirements 2.3**

  - [ ]* 5.8 Write property test for invalid credentials
    - **Property 3: Invalid credentials rejection** — login with wrong password returns 401, no token issued
    - **Validates: Requirements 2.4**

  - [ ]* 5.9 Write property tests for auth guards
    - **Property 4: Unauthenticated access rejection** — requests without valid JWT return 401
    - **Property 5: Non-admin role rejection** — user role accessing admin endpoints returns 403
    - **Property 6: JWT expiration configuration** — token exp claim matches configured minutes
    - **Validates: Requirements 2.5, 2.6, 2.8, 17.2**

  - [ ]* 5.10 Write property test for password hashing
    - **Property 32: Password hashing** — stored hash differs from plaintext and verifies correctly with bcrypt
    - **Validates: Requirements 17.1**

- [ ] 6. Checkpoint - Verify auth flow
  - Ensure user registration, login, JWT issuance, and auth guards work correctly. Run all tests. Ask the user if questions arise.

- [ ] 7. Test infrastructure setup
  - [ ] 7.1 Create test configuration and fixtures (`tests/conftest.py`)
    - Set up an in-memory SQLite test database with SQLAlchemy (override `get_db` dependency)
    - Create a `TestClient` fixture using httpx `AsyncClient` with the FastAPI app
    - Create helper fixtures: `create_test_user` (returns user + token), `create_admin_user` (returns admin + token), `auth_headers` (returns Authorization header dict)
    - Create `factory_boy` factories for User, Category, SubCategory, Exercise, WorkoutPlan, PlanDay, PlanDayExercise
    - Ensure each test gets a fresh DB transaction that rolls back after the test
    - _Requirements: 1.3, 16.3_

- [ ] 8. Inventory CRUD — schemas, service, and routes
  - [ ] 8.1 Create inventory Pydantic schemas (`app/schemas/inventory.py`)
    - Define request schemas: `CategoryCreate` (name), `SubCategoryCreate` (name), `ExerciseCreate` (name, description, target_muscles)
    - Define update schemas: `CategoryUpdate`, `SubCategoryUpdate`, `ExerciseUpdate` (all fields optional)
    - Define response schemas: `CategoryResponse`, `SubCategoryResponse`, `ExerciseResponse` — include id, name, sharing_scope, owner_id, created_at, updated_at and nested fields as appropriate
    - All schemas use snake_case field naming
    - _Requirements: 14.1, 14.2_

  - [ ] 8.2 Implement inventory service (`app/services/inventory.py`)
    - Implement CRUD methods for Category, SubCategory, Exercise
    - For create: set sharing_scope to "global" if user is admin, "private" if regular user; set owner_id to current user
    - For list/get: return union of global items + user's own items + items shared with user (visibility filtering)
    - For update/delete: check ownership — allow if owner or admin, raise ForbiddenError otherwise
    - Implement cascade delete logic (Category deletes SubCategories and Exercises, SubCategory deletes Exercises)
    - _Requirements: 4.1–4.7, 5.1–5.5_

  - [ ] 8.3 Implement inventory routes (`app/routes/inventory.py`)
    - `GET /inventory/categories` — list all visible categories for current user
    - `POST /inventory/categories` — create category (admin=global, user=private)
    - `PUT /inventory/categories/{id}` — update category (ownership check)
    - `DELETE /inventory/categories/{id}` — delete category with cascade (ownership check)
    - `GET /inventory/categories/{id}/subcategories` — list sub-categories
    - `POST /inventory/categories/{id}/subcategories` — create sub-category
    - `PUT /inventory/subcategories/{id}` — update sub-category
    - `DELETE /inventory/subcategories/{id}` — delete sub-category with cascade
    - `GET /inventory/subcategories/{id}/exercises` — list exercises
    - `POST /inventory/subcategories/{id}/exercises` — create exercise
    - `PUT /inventory/exercises/{id}` — update exercise
    - `DELETE /inventory/exercises/{id}` — delete exercise
    - All endpoints require authentication via `get_current_user`
    - _Requirements: 4.1–4.7, 5.1–5.5_

  - [ ]* 8.4 Write property tests for inventory
    - **Property 9: Admin-created resources have global scope** — admin-created Category/SubCategory/Exercise has sharing_scope "global"
    - **Property 12: User-created resources have private scope** — user-created items have sharing_scope "private" and correct owner_id
    - **Validates: Requirements 4.1, 4.2, 4.3, 5.1**

  - [ ]* 8.5 Write property tests for inventory visibility and ownership
    - **Property 13: Visibility filtering** — listing returns exactly global + own + shared items, no other users' private items
    - **Property 14: Ownership enforcement** — User B cannot update/delete User A's resource, gets 403
    - **Validates: Requirements 5.2, 5.5**

  - [ ]* 8.6 Write property tests for update round-trip and cascade delete
    - **Property 10: Resource update round-trip** — update a field then retrieve returns updated value
    - **Property 11: Cascade delete removes children** — deleting parent removes all descendants
    - **Validates: Requirements 4.4, 4.5, 4.6, 4.7, 5.3, 5.4**

- [ ] 9. Checkpoint - Verify inventory CRUD
  - Ensure all inventory endpoints work for both admin and user roles, visibility filtering is correct, ownership checks pass, and cascade deletes work. Run all tests. Ask the user if questions arise.

- [ ] 10. Workout plan CRUD — schemas, service, and routes
  - [ ] 10.1 Create plan Pydantic schemas (`app/schemas/plan.py`)
    - Define request schemas: `WorkoutPlanCreate` (name, description, num_days), `PlanDayCreate` (day_number, name), `PlanDayExerciseCreate` (exercise_id, display_order, prescribed_sets, prescribed_reps)
    - Define update schemas: `WorkoutPlanUpdate`, `PlanDayUpdate`, `PlanDayExerciseUpdate` (all fields optional)
    - Define response schemas: `WorkoutPlanResponse` (with nested list of PlanDays), `PlanDayResponse` (with nested list of PlanDayExercises), `PlanDayExerciseResponse`
    - _Requirements: 14.1, 14.2_

  - [ ] 10.2 Implement plan service (`app/services/plan.py`)
    - Implement CRUD for WorkoutPlan: create (admin=global, user=private), list (visibility filtering), get by id, update, delete with cascade
    - Implement CRUD for PlanDay: add day to plan, update day, delete day
    - Implement CRUD for PlanDayExercise: add exercise to day (with display_order, sets, reps), update, remove
    - Ownership checks on all mutating operations (owner or admin allowed, else ForbiddenError)
    - _Requirements: 7.1–7.5, 8.1–8.6_

  - [ ] 10.3 Implement plan routes (`app/routes/plan.py`)
    - `GET /plans` — list all visible plans
    - `POST /plans` — create plan
    - `GET /plans/{id}` — get plan with days and exercises
    - `PUT /plans/{id}` — update plan
    - `DELETE /plans/{id}` — delete plan with cascade
    - `POST /plans/{id}/days` — add plan day
    - `PUT /plans/{plan_id}/days/{day_id}` — update plan day
    - `DELETE /plans/{plan_id}/days/{day_id}` — delete plan day
    - `POST /plans/days/{day_id}/exercises` — add exercise to day
    - `PUT /plans/day-exercises/{id}` — update exercise assignment
    - `DELETE /plans/day-exercises/{id}` — remove exercise from day
    - All endpoints require authentication
    - _Requirements: 7.1–7.5, 8.1–8.6_

  - [ ]* 10.4 Write property tests for workout plans
    - **Property 9: Admin-created resources have global scope** — admin-created WorkoutPlan has sharing_scope "global"
    - **Property 12: User-created resources have private scope** — user-created plan has sharing_scope "private" and correct owner_id
    - **Property 10: Resource update round-trip** — update plan name then retrieve returns updated value
    - **Property 11: Cascade delete removes children** — deleting plan removes PlanDays and PlanDayExercises
    - **Property 14: Ownership enforcement** — User B cannot modify/delete User A's plan, gets 403
    - **Validates: Requirements 7.1–7.5, 8.1–8.6**

- [ ] 11. Checkpoint - Verify plan CRUD
  - Ensure all plan endpoints work for both admin and user roles, plan days and exercises can be managed, visibility and ownership checks pass. Run all tests. Ask the user if questions arise.

- [ ] 12. Sharing and approval workflow
  - [ ] 12.1 Create sharing Pydantic schemas (`app/schemas/sharing.py`)
    - Define `ShareItemRequest` (emails: list of email strings)
    - Define `ApprovalActionRequest` (action: "approve" or "reject")
    - Define `SharedItemResponse`, `ApprovalQueueItemResponse` (include item details, status, submitter info)
    - _Requirements: 14.1, 14.2_

  - [ ] 12.2 Implement sharing service (`app/services/sharing.py`)
    - Implement `share_with_users(db, item_type, item_id, emails, current_user)` — look up users by email, create SharedItem records, set sharing_scope to "shared"
    - Implement `submit_for_approval(db, item_type, item_id, current_user)` — set approval_status to "pending"
    - Implement `approve_item(db, item_type, item_id)` — set sharing_scope to "global", approval_status to "approved" (admin only)
    - Implement `reject_item(db, item_type, item_id)` — set approval_status to "rejected" (admin only)
    - Implement `get_approval_queue(db, status_filter)` — return pending/approved/rejected items with filtering
    - _Requirements: 6.1–6.5, 9.1–9.4_

  - [ ] 12.3 Implement sharing routes (`app/routes/sharing.py`)
    - `POST /sharing/items/{item_type}/{id}/share` — share with specific users by email
    - `POST /sharing/items/{item_type}/{id}/submit` — submit for global approval
    - `GET /sharing/approval-queue` — admin: list items with optional status filter query param
    - `PUT /sharing/approval-queue/{item_type}/{id}` — admin: approve or reject
    - Share endpoints require authentication; approval queue endpoints require admin role
    - _Requirements: 6.1–6.5, 9.1–9.4_

  - [ ]* 12.4 Write property tests for sharing
    - **Property 15: Sharing grants read access** — after sharing, recipient's listing includes the shared resource
    - **Property 16: Submit for approval sets pending status** — submitted item has approval_status "pending"
    - **Property 17: Admin approval sets global scope** — approved item has sharing_scope "global" and approval_status "approved"
    - **Property 18: Admin rejection sets rejected status** — rejected item has approval_status "rejected", sharing_scope unchanged
    - **Property 19: Approval queue filtering** — filtering by status returns only matching items
    - **Validates: Requirements 6.1–6.5, 9.1–9.4**

- [ ] 13. Checkpoint - Verify sharing and approval
  - Ensure sharing by email works, approval queue is functional, admin approve/reject changes statuses correctly, and shared items appear in recipient listings. Run all tests. Ask the user if questions arise.

- [ ] 14. Workout scheduling
  - [ ] 14.1 Create schedule Pydantic schemas (`app/schemas/schedule.py`)
    - Define `ScheduleCreateSingle` (plan_day_id, plan_id, scheduled_date)
    - Define `ScheduleCreatePlan` (plan_id, start_date) — assigns full plan across consecutive dates
    - Define `ScheduleUpdate` (scheduled_date or plan_day_id, optional)
    - Define `ScheduleResponse` (id, scheduled_date, plan_day details, plan details)
    - Define `DailyWorkoutResponse` (plan name, plan_day name, list of exercises with display_order, name, target_muscles, prescribed_sets, prescribed_reps)
    - _Requirements: 14.1, 14.2_

  - [ ] 14.2 Implement schedule service (`app/services/schedule.py`)
    - Implement `assign_plan_to_dates(db, plan_id, start_date, user)` — fetch plan's PlanDays ordered by day_number, create Schedule entries for consecutive dates starting from start_date. Check for conflicts (409 ConflictError if date already scheduled)
    - Implement `assign_single_day(db, plan_day_id, plan_id, date, user)` — create single Schedule entry with conflict check
    - Implement `update_schedule(db, schedule_id, update_data, user)` — update date or plan_day assignment
    - Implement `delete_schedule(db, schedule_id, user)` — remove schedule entry
    - Implement `get_schedule_range(db, user, start_date, end_date)` — return entries within date range with plan/day details
    - Implement `get_today_workout(db, user)` — return today's scheduled plan day with exercises, or indicate no workout planned
    - Implement `get_plan_day_detail(db, day_id)` — return all exercises in prescribed order
    - _Requirements: 10.1–10.6, 11.1–11.3_

  - [ ] 14.3 Implement schedule routes (`app/routes/schedule.py`)
    - `GET /schedule?start_date=&end_date=` — get schedule for date range
    - `POST /schedule` — assign single plan day to date
    - `POST /schedule/plan` — assign full plan to date range
    - `PUT /schedule/{id}` — update schedule entry
    - `DELETE /schedule/{id}` — remove schedule entry
    - `GET /schedule/today` — get today's workout
    - `GET /schedule/days/{day_id}` — get plan day detail with exercises
    - All endpoints require authentication
    - _Requirements: 10.1–10.6, 11.1–11.3_

  - [ ]* 14.4 Write property tests for scheduling
    - **Property 20: Schedule date-range assignment** — assigning plan with N days creates exactly N entries with correct day-to-date mapping
    - **Property 21: Schedule conflict detection** — scheduling on an already-scheduled date returns 409, original entry unchanged
    - **Property 22: Schedule date-range retrieval** — querying [start, end] returns exactly entries within that range
    - **Property 23: Daily workout returns correct plan day** — today's endpoint returns correct plan/day with exercises in display_order
    - **Validates: Requirements 10.1–10.6, 11.1–11.3**

- [ ] 15. Checkpoint - Verify scheduling
  - Ensure plan assignment to dates works (single and range), conflict detection returns 409, date range queries are correct, and today's workout endpoint returns the right data. Run all tests. Ask the user if questions arise.

- [ ] 16. Workout session logging
  - [ ] 16.1 Create session Pydantic schemas (`app/schemas/session.py`)
    - Define `SessionStartRequest` (plan_day_id, session_date)
    - Define `SetLogCreate` (exercise_id, set_number, reps_performed, weight) — weight must be positive (gt=0)
    - Define `SetLogResponse` (id, exercise_id, set_number, reps_performed, weight, created_at)
    - Define `SessionResponse` (id, plan_day_id, session_date, status, started_at, completed_at, set_logs list)
    - Define `SessionListResponse` for paginated history (items, total, page, page_size)
    - Define `ExerciseProgressResponse` (exercise_id, history: list of date + weight entries)
    - _Requirements: 14.1, 14.2, 12.3_

  - [ ] 16.2 Implement session service (`app/services/session.py`)
    - Implement `start_session(db, plan_day_id, session_date, user)` — create WorkoutSession with status "in_progress" and started_at timestamp
    - Implement `log_set(db, session_id, set_log_data, user)` — validate weight > 0 (422 if not), create SetLog record
    - Implement `complete_session(db, session_id, user)` — set status to "completed", set completed_at timestamp
    - Implement `end_session_early(db, session_id, user)` — set status to "partial", set completed_at timestamp
    - Implement `get_session_detail(db, session_id, user)` — return session with all SetLogs
    - Implement `get_session_history(db, user, page, page_size)` — return paginated sessions in reverse chronological order
    - Implement `get_previous_performance(db, exercise_id, user)` — return SetLogs from the most recent past session for that exercise
    - Implement `get_exercise_progress(db, exercise_id, user)` — return weight history across sessions ordered by date
    - _Requirements: 12.1–12.6, 13.1–13.4_

  - [ ] 16.3 Implement session routes (`app/routes/session.py`)
    - `POST /sessions` — start workout session
    - `POST /sessions/{id}/sets` — log a set
    - `PUT /sessions/{id}/complete` — mark session complete
    - `PUT /sessions/{id}/end` — end session early (partial)
    - `GET /sessions` — workout history (paginated, query params: page, page_size)
    - `GET /sessions/{id}` — session detail
    - `GET /sessions/exercises/{id}/history` — exercise progress/weight history
    - `GET /sessions/exercises/{id}/previous` — previous performance for exercise
    - All endpoints require authentication
    - _Requirements: 12.1–12.6, 13.1–13.4_

  - [ ]* 16.4 Write property tests for session logging
    - **Property 24: Session logging round-trip** — log a set then retrieve session detail includes that SetLog with matching fields
    - **Property 25: Weight validation rejects non-positive values** — zero/negative/non-numeric weight returns 422, no SetLog created
    - **Property 26: Previous performance returns most recent logs** — returns SetLogs from most recent past session only
    - **Property 27: Session status transitions** — completing sets status to "completed" with timestamp; ending early sets status to "partial" with timestamp
    - **Validates: Requirements 12.1–12.6**

  - [ ]* 16.5 Write property tests for workout history
    - **Property 28: History is paginated and chronologically ordered** — sessions returned newest first, page size respected
    - **Validates: Requirements 13.2, 13.4**

- [ ] 17. Checkpoint - Verify session logging and history
  - Ensure session start, set logging, completion, early end, history pagination, previous performance, and exercise progress all work correctly. Run all tests. Ask the user if questions arise.

- [ ] 18. Data integrity, serialization, and cross-cutting concerns
  - [ ] 18.1 Implement transaction rollback safety in `get_db()` dependency
    - Ensure the `get_db()` dependency in `app/dependencies.py` wraps each request in a try/except/finally that rolls back on any unhandled exception, preventing partial writes
    - Verify the global exception handler in `app/main.py` returns 500 with generic message and logs the traceback
    - _Requirements: 16.3_

  - [ ] 18.2 Write property tests for data integrity
    - **Property 7: Referential integrity enforcement** — creating a child record with non-existent parent FK raises integrity error, record not persisted
    - **Property 31: Transaction rollback on failure** — DB state after a failed write is identical to state before the request
    - **Validates: Requirements 3.2, 16.2, 16.3**

  - [ ] 18.3 Write property tests for serialization
    - **Property 29: Serialization round-trip** — serialize Pydantic response to JSON then deserialize back produces equivalent object
    - **Property 33: Snake_case field naming** — all JSON response field names match snake_case pattern
    - **Validates: Requirements 14.1, 14.3**

  - [ ] 18.4 Write property test for schema validation errors
    - **Property 30: Schema validation returns 422 with field errors** — request body violating schema returns 422 with field-level error details
    - **Validates: Requirements 14.4**

- [ ] 19. Wire everything together and final integration
  - [ ] 19.1 Register all routers in `app/main.py`
    - Import and include all route modules (auth, inventory, plan, schedule, session, sharing) with their prefixes
    - Verify no route conflicts or missing dependencies
    - _Requirements: 1.1_

  - [ ] 19.2 Create a `.env.example` and update `README.md`
    - Update `.env.example` with all required environment variables and example values
    - Update `README.md` with setup instructions: install dependencies, configure `.env`, run migrations, start the server
    - Include instructions for running tests with `pytest`
    - _Requirements: 1.2_

- [ ] 20. Final checkpoint - Ensure all tests pass
  - Run the full test suite with `pytest`. Verify all endpoints work end-to-end. Ensure all requirements are covered. Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at logical breakpoints
- Property tests validate universal correctness properties from the design document
- The build order ensures no orphaned code — each step integrates with previous steps
- The user should run `pytest` at each checkpoint to verify progress
